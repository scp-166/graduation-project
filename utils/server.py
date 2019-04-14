from gevent import monkey
monkey.patch_all()
from . import baseBridge
from django.core.cache import cache
import time
import gevent
import json


class WsgBridge(baseBridge.BaseBridge):
    """
    前后端websocket通信
    需要区分功能
        树莓派 发送 数据给后端
        后端 定时发指令 给 树莓派
        前端 控制 指令

    """

    def __init__(self, websocket):
        super(WsgBridge, self).__init__(websocket)

    def open(self):
        """
        假如有初始化
        :return:
        """
        try:
            print("假装open初始化")
        except Exception as e:
            # 前端websocket期望收到一个json数据，键值对是'error': errors_message
            self._websocket.send(json.dumps({'error': e}))
            raise

    def _forward_inbound(self):
        """
        前端->后端
        :param channel:
        :return:
        """
        try:
            while True:
                data = self._websocket.receive()  # str
                if not data:  # 没有数据时退出函数
                    return
                data = json.loads(data)  # str->dict

                if 'data' in data:
                    # 字典中存在键data，则进行操作
                    print("假装保存了数据", data["data"])
                for i in data.keys():
                    print(i, data[i], type(data[i]))
        finally:
            self.close()

    def _forward_outbound(self, flag=0):
        """
        后端->前端
        :param channel:
        :return:
        """
        try:
            while True:
                # 到时候这里改为指令
                data = json.dumps({'type': 2, 'id':1, 'command': 1, 'other': ''})  # dict->str
                if not len(data):
                    return
                self._websocket.send(data)
                time.sleep(1)
        finally:
            self.close()

    def _bridge(self):
        self._tasks = [
            gevent.spawn(self._forward_inbound, ),
            gevent.spawn(self._forward_outbound, ),
            # gevent.spawn(self.must_close, ),
        ]
        gevent.joinall(self._tasks)

    def close(self):
        """
        结束桥接会话
        :return:
        """
        gevent.killall(self._tasks, block=True)  # 关闭协程，设置堵塞
        self._websocket.close() # 关闭websocket
        self._tasks = []

    def must_close(self):
        """
        强制终止，中断会被迫ConnectAbortError
        :return:
        """
        time.sleep(2)
        self.close()

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
            print("树莓派开始发送")
        except Exception as e:
            # 前端websocket期望收到一个json数据，键值对是'error': errors_message
            self._websocket.send(json.dumps({'error': e}))
            raise

    def _forward_inbound(self):
        """
        前端->后端
        :param channel:
        :return:
        """
        try:
            while True:
                data = self._websocket.receive()  # str
                # if not data:  # 没有数据时退出函数
                #     return
                data = json.loads(data)  # str->dict
                print("树莓派表示状态为: ", data)

                if 'status' in data:
                    # 字典中存在键status，则保存进缓存10s
                    cache.set("status", 1, 10)
                    print("status 1")
                    self._forward_outbound(1)  # 进行一次响应
                else:
                    print("status 0")
                    self._forward_outbound(0)
        finally:
            print("socket is dead")
            self.close()

    def _forward_outbound(self, flag=0):
        """
        后端->前端
        :param channel:
        :return:
        """
        try:
            if flag:
                if cache.get("status"):
                    print("树莓派存在")
                    data = json.dumps({'received': 1})  # dict->str
            # 到时候这里改为指令
                else:
                    print("树莓派不存在")
                    data = json.dumps({'received': 0})  # dict->str
                if not len(data):
                    return
                else:
                    self._websocket.send(data)
            else:
                data = json.dumps({'received': 0})  # dict->str
                print("树莓派不存在2")
                self._websocket.send(data)
        finally:
            print("休眠9s")
            time.sleep(9)

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
        self._websocket.close() # 关闭websocket
        self._tasks = []

    def must_close(self):
        time.sleep(2)
        # self.close()

    def start(self):
        """
        启动一个shell通信界面
        :return:
        """
        self._bridge()  # 将激活的终端的通道设置无延时不堵塞，gevent添加任务


