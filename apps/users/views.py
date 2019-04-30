from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from utils.server import WsgBridge, AliveBridge


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
    return HttpResponse("无结果")






