from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache
from django.views import View
from django.http import HttpResponse

from apps.exhibition.models import TerminalCategory, TerminalInfo, TerminalData

from utils.server import AliveBridge
from utils.custom_command import get_command, write_command
from utils.cache_process import cookie_cache_processor


def control_led(request):
    # 获得data对应的info的terminal_category外键
    data = TerminalData.objects.filter(terminal__terminal_category=2)
    context = {
        'data': data,
    }
    return render(request, 'LedControl.html', context)


def change_led_status(request, led_id):
    print(led_id)
    led = TerminalData.objects.filter(terminal__terminal_category_id=2,
                                      terminal__terminal_id=led_id)
    if led.exists():
        led = led.first()
        status = request.GET.get('status')  # 参数都是str
        if status == 'True':
            led.status = False
        else:
            led.status = True
        led.save()
        return JsonResponse({'is_changed': 1})
    else:
        return JsonResponse({'is_changed': 0})


def is_alive(request):
    if cache.get('status'):
        status = 1
    else:
        status = 0
    data = {
        'status': status
    }
    return JsonResponse(data)


class TestCommand(View):
    def get(self, request):
        return render(request, 'command.html')

    def post(self, request):
        category = int(request.POST.get('category', 0))
        id = int(request.POST.get('id', 0))
        write_command(1, category, id, 1,
                      cookie_cache_processor.get_verification())
        write_command(1, category, id, 1,
                      cookie_cache_processor.get_verification())
        print("写了数据")
        print(get_command())
        return HttpResponse("www")


def is_active(request):
    if not request.environ.get('wsgi.websocket'):
        return JsonResponse({'ret': "非websocket请求"})
    else:
        webscocket = request.environ.get('wsgi.websocket')
        wsg_bright = AliveBridge(webscocket)
        try:
            wsg_bright.open()
        except Exception as e:
            print(e)

        wsg_bright.start()
    return HttpResponse("websocket端")


def get_temp_data(request):

    data = [1, 2, 2, 3, 4, 5, 6]
    day = [1, 2, 3, 4, 5, 6, 7]
    return JsonResponse({'day': day, 'data': data})


def get_hum_data(request):

    data = [1, 2, 2, 3, 4, 5, 6]
    day = [1, 2, 3, 4, 5, 6, 7]
    return JsonResponse({'day': day, 'data': data})
