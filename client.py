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
import requests
import re


def login(url, **kwargs):
    telephone = kwargs.get('telephone', None)
    password = kwargs.get('password', None)
    if telephone is None or password is None:
        return 0
    else:
        print(telephone)
        print(password)
        # 请求头
        appropriate_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }

        # 获取token
        # 使用requests.Session()保持窗口唯一
        sss = requests.Session()
        ret = sss.get(url, headers=appropriate_headers)
        print(ret.content.decode())
        reg = r'<input type="hidden" name="csrfmiddlewaretoken" value="(.*)">'  # 拿到token
        pattern = re.compile(reg)
        result = pattern.findall(ret.content.decode())
        print(result)
        token = result[0]

        # post data
        target_data = {
            'csrfmiddlewaretoken': token,
            'telephone': telephone,
            'password': password
        }

        # 登录后
        ret = sss.post(url, headers=appropriate_headers, data=target_data)
        print(ret.text)
        if 'code' in ret.text:
            a = json.loads(ret.text)['code']
            print(a)

        # 保存cookies
        cookies = requests.utils.dict_from_cookiejar(sss.cookies)
        with open("cookies.txt", "w+") as fp:
            json.dump(cookies, fp)
        print(cookies)
        return sss


import multiprocessing

if __name__ == '__main__':

    session = login('http://127.0.0.1:8000/auth/login/', telephone='17875512067', password='abc666666')
    session.close()

