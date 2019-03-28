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

import socket
from time import sleep
from websocket import create_connection
import websocket
import threading
import json

ws = create_connection("ws://127.0.0.1:8000/echo/", timeout=5)

data = '{"type":%d, "id":%d, "data":%0.2f, "status":%d}'

def do1():
    i = 0
    while 1:
        if ws.connected:
            ws.send(data % (1, 1, 66.666, 1), opcode=websocket.ABNF.OPCODE_TEXT)
            sleep(1)
            print(ws.recv())
        i += 1
        if i == 2:
            ws.send('{"data": "close"}',
                    opcode=websocket.ABNF.OPCODE_TEXT)
            ws.close()
            sleep(1)    # 延时一下
            break

def do2():
    i = 0
    while 1:
        if ws.connected:
            ws.send(data % (1, 2, 68.666, 1), opcode=websocket.ABNF.OPCODE_TEXT)
            sleep(1)
            print(ws.recv())
        i += 1
        if i == 2:
            ws.send('{"data": "close"}',
                    opcode=websocket.ABNF.OPCODE_TEXT)
            ws.close()
            sleep(1)
            break


def do3():
    i = 0
    while 1:
        if ws.connected:
            ws.send(data % (1, 3, 69.666, 1), opcode=websocket.ABNF.OPCODE_TEXT)
            sleep(1)
            print(ws.recv())
        i += 1
        if i == 3:
            ws.send('{"data": "close"}',
                    opcode=websocket.ABNF.OPCODE_TEXT)
            ws.close()
            sleep(1)
            break


if __name__ == '__main__':
    try:
        t1 = threading.Thread(target=do1)
        t2 = threading.Thread(target=do2)
        t3 = threading.Thread(target=do3)

        print(threading.enumerate())

        t1.start()
        t2.start()
        t3.start()

        t1.join()
        t2.join()
        t3.join()
    except KeyboardInterrupt as e:
        print("out")
        exit()

