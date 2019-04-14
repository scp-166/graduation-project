# coding=utf-8

from ws4py.client.threadedclient import WebSocketClient
from ws4py import websocket
import json, threading, time

wsHost = "ws://127.0.0.1:8000/echo/"

string = '{"type":%d, "id":%d, "data":%0.2f, "status":%d}'


class Ws(WebSocketClient):

    def __init__(self, url, data):
        super().__init__(url)
        self.data = data
        self.count = 0

    def opened(self):  # socket连接后调用
        self.send(string % self.data)
        print("发送: ", self.count)
        time.sleep(1)

    def closed(self, code, reason=None):  # wk关闭时调用
        print(code, time.strftime('%Y-%m-%d %H:%M:%S'))

    def received_message(self, message):  # 长连接时接收socket的所有消息,可根据消息做对应处理
        try:
            if self.count <= 5:
                ms = json.loads(str(message))
                if type(ms) is dict:
                    print(ms, "count: ", self.count)
                    self.count += 1
                    time.sleep(1)
        except ConnectionResetError as e:
            print("over")


def start():
    ws = Ws(wsHost, (1, 1, 66.666, 1))  # 创建websocket
    ws.connect()  # 连接wk
    websocket.Heartbeat(ws).run()  # 发送心跳
    ws.run_forever()  # 运行


if __name__ == '__main__':
    alist = []
    try:
        for i in range(5):
            th = threading.Thread(target=start)  # 创建线程
            print(th)
            alist.append(th)
            th.start()  # 启动线程

        for i in alist:
            i.join()
    except KeyboardInterrupt as e:
        print("over")





