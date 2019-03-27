from django.shortcuts import render
from django.http import HttpResponse
from dwebsocket import require_websocket, accept_websocket
import threading
import json
from utils.server import WsgBridge


def index(request):
    return HttpResponse("呵呵")


def chat(req):
    return render(req, 'chat.html')


def echo(request):

    if not request.environ.get('wsgi.websocket'):
        return HttpResponse("非websocket请求")
    else:
        webscocket = request.environ.get('wsgi.websocket')
        wsg_bright = WsgBridge(webscocket)
        try:
            wsg_bright.open()
        except Exception as e:
            print(e)

        wsg_bright.start()
        # while True:
            # request.environ.get('wsgi.websocket').send(json.dumps({'data': "aaa"}))
            # data = request.environ.get('wsgi.websocket').receive()
            # if not data:  # 没有数据时退出函数
            #     return
            # print(type(data))   # str
            # print(data)  # 字典格式的字符串{"data":"close"}
            # data = json.loads(data) # str->dict
            # print(type(data))   # dict
            # print(data)  # {"data":"close"}
            # if data.get("data", None) == "close":
            #     request.environ.get('wsgi.websocket').close()
            #     break


