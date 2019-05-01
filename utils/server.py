# from gevent import monkey
# monkey.patch_all()
# 执行需要的manage.py需要注释上面
from django.core.cache import cache
import time
import gevent
import json

from apps.exhibition.models import TerminalCategory, TerminalData, TerminalInfo
from utils.custom_command import get_command
from utils.cache_process import cookie_cache_processor
from . import baseBridge


class WsgBridge(baseBridge.BaseBridge):
    """
    前后端websocket通信
    """

    def __init__(self, websocket):
        super(WsgBridge, self).__init__(websocket)

    def open(self):
        """
        假如有初始化
        :return:
        """
        try:
            print("WsgBridge初始化")  # 后期改为logger

        except Exception as e:
            # 前端websocket期望收到一个json数据，键值对是'error': errors_message
            self._websocket.send(json.dumps({'error': e}))
            raise

    def _forward_inbound(self, flag=0):
        """
        前端->后端
        :return:
        """
        try:
            while True:
                data = self._websocket.receive()  # json-like str
                if not data:  # 没有数据时退出函数
                    print("no data")
                data = json.loads(data)  # 其中各个字段对应的值都为正确格式
                if 'verf' in data and data[
                    'verf'] == cookie_cache_processor.get_verification() and 'data' in data:  # 需要验证通过且有数据
                    # 进行数据存储操作
                    if TerminalCategory.objects.filter(  # 存在类别
                            category_id=data['type']).exists():

                        category = TerminalCategory.objects.get(
                            category_id=data['type'])
                        if TerminalInfo.objects.filter(  # 存在具体终端
                                terminal_category=category,
                                terminal_id=data['id']).exists():
                            TerminalInfo.objects.filter(  # 更新终端信息，标记存在过
                                terminal_category=category,
                                terminal_id=data['id']).update(
                                status=True if data['status'] == 1 else False)
                        else:
                            TerminalInfo.objects.create(  # 添加新的终端信息
                                terminal_category=category,
                                terminal_id=data['id'],
                                status=True if data['status'] == 1 else False)
                        terminal = TerminalInfo.objects.get(
                            terminal_category=category,
                            terminal_id=data['id'])

                        TerminalData.objects.create(terminal=terminal,  # 添加终端数据
                                                    data=data['data'])
                        print("终端信息存储完毕")
                        self._forward_outbound(data=1)  # 发个成功响应
                else:
                    self._forward_outbound()  # 发个失败响应

        finally:
            self.close()

    def _forward_outbound(self, flag=0, data_format=0, data=0):
        """
        发送给网关
        :param flag: 指令类别 0是响应 1是指令
        :param data_format: 如果是响应，则是响应格式分类
        :param *data: 如果是响应，对响应格式的填充
        :return:
        """
        try:
            if flag:
                command = get_command()  # 从队列中获得指令
                print("WsgBridge将要发送的指令是: {}".format(command))
                self._websocket.send(command)  # 发送格式需要str
            else:
                if data_format == 0:
                    my_format = '{"cmd_catg": %d, "data_received":%d, "verf":"%s"}'
                    print("data响应!!!!!")
                    received = my_format % (
                        flag, data, cookie_cache_processor.get_verification())
                    self._websocket.send(received)
        finally:
            # 到时候弄个logger
            print("WsgBridge结束发送指令")

    def _bridge(self):
        self._tasks = [
            gevent.spawn(self._forward_inbound, ),
            gevent.spawn(self.send_command_forever, ),
        ]
        gevent.joinall(self._tasks)

    def send_command_forever(self):
        """
        一直循环取出队列中的指令
        :return:
        """
        while True:
            # 堵塞ing
            ret = get_command()  # dict-like str
            self._websocket.send(ret)

    def close(self):
        """
        结束桥接会话
        :return:
        """
        gevent.killall(self._tasks, block=True)  # 关闭协程，设置堵塞
        self._websocket.close()  # 关闭websocket
        self._tasks = []

    def start(self):
        """
        启动一个shell通信界面
        :return:
        """
        self._bridge()  # 将激活的终端的通道设置无延时不堵塞，gevent添加任务


class AliveBridge(baseBridge.BaseBridge):
    """
    前后端websocket通信
    需要区分功能
        树莓派 发送 数据给后端
        后端 定时发指令 给 树莓派
        前端 控制 指令

    """

    def __init__(self, websocket):
        super(AliveBridge, self).__init__(websocket)

    def open(self):
        """
        假如有初始化
        :return:
        """
        try:
            print("状态接收初始化")
        except Exception as e:
            # 前端websocket期望收到一个json数据，键值对是'error': errors_message
            self._websocket.send(json.dumps({'error': e}))
            raise

    def _forward_inbound(self):
        """
        前端->后端
        :return:
        """
        try:
            while True:
                data = self._websocket.receive()  # str
                print("alivebriget: ", data)
                if data:
                    data = json.loads(data)  # str->dict
                else:
                    print("alive接收无")
                    self._forward_outbound(verification='cookies')  # 进行一次响应
                    return

                if 'alive' in data and 'name' in data:
                    # 字典中存在键alive和name，则保存进缓存10s
                    cache.set(data["name"], 1, 10)
                    print("存储终端名称进缓存：", data['name'])
                    self._forward_outbound(verification='cookies')  # 进行一次响应
                else:
                    print("无用数据", end=' ')
                    self._forward_outbound(0)
        except Exception as e:
            print("Alive有问题 :", str(e))
        finally:
            print("socket is dead")
            self.close()

    def _forward_outbound(self, command_category=0, category=0, id=0, command=0,
                          verification=''):
        """
        后端->前端
        :param flag:
        :return:
        """
        try:
            names = [i for i in cache.iter_keys("*")]  # 暴力拿全部keys，后面可以根据model的名称获得, 注意iter_keys返回一个生成器
            print("AliveBridge查询所有终端键", end=' ')
            for i in names:
                print(i, end=' ')
                print(type(i), end='#')
            print()

            with open('./conf/category.conf') as f:
                terminals = eval(f.read())
            print(terminals)

            for i in names:
                if i == 'PI':
                    print("PI在线")
                for name in terminals.values():
                    if i.startswith(name):
                        print(i, "在线")

            data = json.dumps({'received': 0})  # dict->str
            self._websocket.send(data)
        finally:
            # 届时写个logger
            print("AliveBridge回应状态结束")

    def _bridge(self):
        self._tasks = [
            gevent.spawn(self._forward_inbound, ),
            # gevent.spawn(self._forward_outbound, ),
            # gevent.spawn(self.must_close, ),
        ]
        gevent.joinall(self._tasks)

    def close(self):
        """
        结束桥接会话
        :return:
        """
        gevent.killall(self._tasks, block=True)  # 关闭协程，设置堵塞
        self._websocket.close()  # 关闭websocket
        self._tasks = []

    def must_close(self):
        time.sleep(2)
        # self.close()

    def start(self):
        """
        启动一个shell通信界面
        :return:
        """
        self._bridge()  # 将激活的终端的通道设置无延时不堵塞，gevent中添加任务


class AutoDataBridge(baseBridge.BaseBridge):
    """
    前后端websocket通信
    前端自动获取数据

    """

    def __init__(self, websocket, category_id, terminal_id):
        super(AutoDataBridge, self).__init__(websocket)
        self.category_id = category_id
        self.terminal_id = terminal_id

    def open(self):
        """
        假如有初始化
        :return:
        """
        try:
            print("自动获取初始化")
        except Exception as e:
            # 前端websocket期望收到一个json数据，键值对是'error': errors_message
            self._websocket.send(json.dumps({'error': e}))
            raise

    def _forward_inbound(self):
        """
        前端->后端
        :return:
        """
        try:
            while True:
                data = self._websocket.receive()  # str
                print("get from front: ", data)
                if data:
                    data = json.loads(data)  # str->dict
                    if 'data' in data:
                        print("收到数据", data['data'])
                    self._forward_outbound()  # 进行一次响应
                else:
                    print("aoto接收无")
                    return

        except Exception as e:
            print("auto有问题 :", str(e))
        finally:
            print("auto socket is dead")
            self.close()

    def _forward_outbound(self, command_category=0, category=0, id=0, command=0,
                          verification=''):
        """
        后端->前端
        :param flag:
        :return:
        """
        try:
            category = TerminalCategory.objects.filter(
                category_id=self.category_id)
            if category.exists():
                sensor = TerminalInfo.objects.filter(
                    terminal_category=category.first(),
                    terminal_id=self.terminal_id)
                if sensor.exists():
                    data = TerminalData.objects.filter(
                        terminal=sensor.first()).order_by('-create_time')
                    length = 5
                    if data.count() > length:  # 如果数据过多，取十条
                        data = data[:length]
                        data = json.dumps(
                            {'times': [i.create_time.strftime("%m/%d-%H:%M:%S")
                                       for i in data],
                             "data": [i.data for i in data]})  # dict->str
                    else:  # 取剩下的数据
                        data = json.dumps(
                            {'times': [i.create_time.strftime("%m/%d-%H:%M:%S")
                                       for i in data],
                             "data": [i.data for i in data]})  # dict->str
                else:
                    data = json.dumps({'times': [1, ],
                                       "data": [1, ]})  # dict->str
            else:
                data = json.dumps({'times': [2, ],
                                   "data": [2, ]})  # dict->str
            self._websocket.send(data)
        finally:
            # 届时写个logger
            print("autoBridge回应状态结束")

    def _bridge(self):
        self._tasks = [
            gevent.spawn(self._forward_inbound, ),
            # gevent.spawn(self._forward_outbound, ),
            # gevent.spawn(self.must_close, ),
        ]
        gevent.joinall(self._tasks)

    def close(self):
        """
        结束桥接会话
        :return:
        """
        gevent.killall(self._tasks, block=True)  # 关闭协程，设置堵塞
        self._websocket.close()  # 关闭websocket
        self._tasks = []

    def must_close(self):
        time.sleep(2)
        # self.close()

    def start(self):
        """
        启动一个shell通信界面
        :return:
        """
        self._bridge()  # 将激活的终端的通道设置无延时不堵塞，gevent中添加任务
