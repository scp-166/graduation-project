import server_ws.gevent_header
from django.core.cache import cache
import time
import gevent
import json


from server_ws.base_bridge import BaseBridge


class AskPiStatusBridge(BaseBridge):
    """
    前后端websocket通信
    前端自动获取数据

    """

    def __init__(self, websocket):
        super(AskPiStatusBridge, self).__init__(websocket)

    def open(self):
        """
        假如有初始化
        :return:
        """
        try:
            print("获取pi状态初始化")
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
                print("ask status from front: ", data)
                if data:
                    data = json.loads(data)  # str->dict
                    if 'data' in data:
                        print("收到数据", data['data'])
                    self._forward_outbound()  # 进行一次响应
                else:
                    print("ask status 接收无")
                    return

        except Exception as e:
            print("ask status有问题 :", str(e))
        finally:
            print("ask status socket is dead")
            self.close()

    def _forward_outbound(self, command_category=0, category=0, id=0, command=0,
                          verification=''):
        """
        后端->前端
        :param flag:
        :return:
        """
        try:

            # 暴力拿全部keys，后面可以根据model的名称获得, 注意iter_keys返回一个生成器
            cache_names = [i for i in cache.iter_keys("*")]
            data = 0
            for i in cache_names:  # 遍历缓存中的名称
                if i == 'PI':
                    data = 1

            data = json.dumps({"data": data})
            self._websocket.send(data)
        finally:
            # 届时写个logger
            print("autoBridge回应状态结束")


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
        self._tasks = [
            gevent.spawn(self._forward_inbound, ),
        ]
        gevent.joinall(self._tasks)
