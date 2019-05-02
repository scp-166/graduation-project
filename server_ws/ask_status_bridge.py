import server_ws.gevent_header
from django.core.cache import cache
import time
import gevent
import json

from server_ws.base_bridge import BaseBridge


class AskStatusBridge(BaseBridge):
    """
    前后端websocket通信
    前端自动获取数据

    """

    def __init__(self, websocket):
        super(AskStatusBridge, self).__init__(websocket)
        self.category_id_list = None
        self.terminal_id_list = None

    def open(self):
        """
        假如有初始化
        :return:
        """
        try:
            print("获取状态初始化")
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
                    if 'data' in data:
                        print("收到数据", type(data['data']))  # dict
                        # 保存前端发来的所有category_id和terminal_id
                        self.category_id_list = data['data'].get(
                            'category_id_list', None)
                        self.terminal_id_list = data['data'].get(
                            'terminal_id_list', None)
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
            if self.category_id_list is None or self.terminal_id_list is None:
                self._websocket.send(json.dumps({'code': 400}))  # 发送一个400状态码
                return
            # 暴力拿全部keys，后面可以根据model的名称获得, 注意iter_keys返回一个生成器
            cache_names = [i for i in cache.iter_keys("*")]

            # 打开配置文件， 获取终端信息键值对
            with open('./conf/category.conf') as f:
                terminals = eval(f.read())

            exist_category_id_list = []
            exist_terminal_id_list = []
            # 改成(category_id:terminal_id) 方便查询
            # set是去重
            category_terminal_set = set([(k, v) for k in self.category_id_list
                                         for v in self.terminal_id_list])
            # print("键值对", category_terminal_set)
            for category_id, terminal_id in category_terminal_set:
                category_id = int(category_id)
                terminal_id = int(terminal_id)
                for i in cache_names:  # 遍历缓存中的名称
                    for name in terminals.values():  # 遍历配置表中的内容，组合名称查看是否存在于缓存中
                        if (name + '%02d' % category_id + '%02d' % terminal_id) == i:
                            exist_category_id_list.append(category_id)
                            exist_terminal_id_list.append(terminal_id)

            data = json.dumps({"data": {
                "category_id_list": exist_category_id_list,
                "terminal_id_list": exist_terminal_id_list}})
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
