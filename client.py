# import websocket
# try:
#     import thread
# except ImportError:
#     import _thread as thread
# import time
#
#
# def on_message(ws, message):
#     print("*************message************")
#     print(message)
#
#
# def on_error(ws, error):
#     print("*************error************")
#     print(error)
#
#
# def on_close(ws):
#     print("### closed ###")
#
#
# def on_open(ws):
#     def run(*args):
#         ws.send("hello")
#         time.sleep(1)
#         ws.close()
#
#     thread.start_new_thread(run, ())
#
#
# if __name__ == "__main__":
#     websocket.enableTrace(True)
#     ws = websocket.WebSocketApp("ws://127.0.0.1:8000/echo/",
#                               on_message = on_message,
#                               on_error = on_error,
#                               on_close = on_close)
#     ws.on_open = on_open
#     ws.run_forever(ping_interval=60, ping_timeout=5)  # 长连接

from time import sleep
from websocket import create_connection
import websocket
import threading
import json


data = '{"type":%d, "id":%d, "data":%0.2f, "status":%d}'


def do1(ws):
    i = 0
    try:
        while True:
            if ws.connected:
                ws.send(data % (1, 1, 66.666, 1),
                         opcode=websocket.ABNF.OPCODE_TEXT)
                sleep(1)
                print("do1: ", ws.recv())
            i += 1
            if i == 20:
                ws.send('{"data": "close"}',
                         opcode=websocket.ABNF.OPCODE_TEXT)
                ws.close()
                sleep(1)  # 延时一下
                break
    except ConnectionAbortedError:
        print("do1 ConnectionAbortedError")
    except websocket._exceptions.WebSocketConnectionClosedException as e:
        print("do1 WebSocketConnectionClosedException")


def ask_alive(ws):
    try:
        while True:
            if ws.connected:
                ws.send('{"status": "1"}',  # 定时发送树莓派状态
                         opcode=websocket.ABNF.OPCODE_TEXT)
                print(ws.recv(), "存在回应")
                sleep(10)  # 延时一下,10s左右表示存在

    except ConnectionAbortedError:
        print("ask_alive ConnectionAbortedError")
    except websocket._exceptions.WebSocketConnectionClosedException:
        print("ask_alive WebSocketConnectionClosedException")


if __name__ == '__main__':
    # ws1 = create_connection("ws://127.0.0.1:8000/echo/", timeout=5)
    # t1 = threading.Thread(target=do1, args=(ws1,))
    # t1.start()

    ws2 = create_connection("ws://127.0.0.1:8000/is_active/", timeout=60)
    t2 = threading.Thread(target=ask_alive, args=(ws2,))
    t2.start()

    # t1.join()
    t2.join()


