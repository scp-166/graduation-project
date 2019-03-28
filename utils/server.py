from gevent import monkey
monkey.patch_all()
import gevent
import json


class WsgBridge:
    """
    前后端websocket通信
    需要区分功能
        树莓派 发送 数据给后端
        后端 定时发指令 给 树莓派
        前端 控制 指令

    """

    def __init__(self, websocket):

        self._websocket = websocket
        self._tasks = []  # 需要执行的任务

    def open(self):
        """
        假如有初始化
        :param host_ip:
        :param host_port:
        :param username:
        :param password:
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

    def _forward_outbound(self):
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
        finally:
            self.close()

    def _bridge(self):
        self._tasks = [
            gevent.spawn(self._forward_inbound, ),
            gevent.spawn(self._forward_outbound, ),
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

    def start(self):
        """
        启动一个shell通信界面
        :return:
        """
        self._bridge()  # 将激活的终端的通道设置无延时不堵塞，gevent添加任务

