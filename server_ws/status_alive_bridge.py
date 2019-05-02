import server_ws.gevent_header
from django.core.cache import cache
import time
import gevent
import json

from server_ws.base_bridge import BaseBridge


class StatusAliveBridge(BaseBridge):
    """
    前后端websocket通信
    需要区分功能
        树莓派 发送 数据给后端
        后端 定时发指令 给 树莓派
        前端 控制 指令

    """

    def __init__(self, websocket):
        super(StatusAliveBridge, self).__init__(websocket)

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

                if data:
                    data = json.loads(data)  # str->dict
                else:
                    print("alive接收无")
                    self._forward_outbound(verification='cookies')  # 进行一次响应
                    return

                if 'alive' in data and 'name' in data:
                    # 字典中存在键alive和name，则保存进缓存10s
                    cache.set(data["name"], 1, 2)
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
            data = json.dumps({'received': 0})  # dict->str
            self._websocket.send(data)
        finally:
            # 届时写个logger
            # print("AliveBridge回应状态结束")
            pass

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


