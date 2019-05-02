import server_ws.gevent_header
from django.core.cache import cache
import time
import gevent
import json

from apps.exhibition.models import TerminalCategory, TerminalData, TerminalInfo
from server_ws.base_bridge import BaseBridge


class AutoGetSensorDataBridge(BaseBridge):
    """
    前后端websocket通信
    前端自动获取数据

    """

    def __init__(self, websocket, category_id, terminal_id):
        super(AutoGetSensorDataBridge, self).__init__(websocket)
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
                            # [::-1]是让前端获得从小到大排列的顺序
                            {'times': [i.create_time.strftime("%m/%d-%H:%M:%S")
                                       for i in data][::-1],
                             "data": [i.data for i in data][::-1]})  # dict->str
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
            # print("autoBridge回应状态结束")
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
