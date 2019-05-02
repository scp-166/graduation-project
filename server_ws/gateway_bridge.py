import server_ws.gevent_header
# 执行需要的manage.py需要注释上面
import gevent
import json

from apps.exhibition.models import TerminalCategory, TerminalData, TerminalInfo, \
    WarningValue
from utils.custom_command import get_command
from utils.cache_process import cookie_cache_processor
from server_ws.base_bridge import BaseBridge


class GatewayBridge(BaseBridge):
    """
    前后端websocket通信
    """

    def __init__(self, websocket):
        super(GatewayBridge, self).__init__(websocket)

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
                            WarningValue.objects.create(  # 给终端信息绑定一个预警值
                                terminal=TerminalInfo.objects.get(
                                    terminal_category=category,
                                    terminal_id=data['id']))
                        terminal = TerminalInfo.objects.get(
                            terminal_category=category,
                            terminal_id=data['id'])

                        TerminalData.objects.create(terminal=terminal,  # 添加终端数据
                                                    data=data['data'])
                        print("终端信息假装存储完毕")
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
            print("收到的命令是: ", ret)
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
