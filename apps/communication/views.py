from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views import View


from apps.exhibition.models import TerminalCategory, TerminalInfo, TerminalData, \
    WarningValue

from server_ws.gateway_bridge import GatewayBridge
from server_ws.status_alive_bridge import StatusAliveBridge
from server_ws.auto_get_sensor_data_bridge import AutoGetSensorDataBridge
from server_ws.ask_status_bridge import AskStatusBridge
from server_ws.ask_pi_status_bridge import AskPiStatusBridge

from utils.custom_command import get_command, write_command
from utils.cache_process import cookie_cache_processor


def echo(request):
    if not request.environ.get('wsgi.websocket'):
        return HttpResponse("非websocket请求")
    else:
        webscocket = request.environ.get('wsgi.websocket')
        gateway_bright = GatewayBridge(webscocket)
        try:
            gateway_bright.open()
        except Exception as e:
            print(e)

        gateway_bright.start()
    return HttpResponse("无结果")


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


def ask_status(request):
    if not request.environ.get('wsgi.websocket'):
        return JsonResponse({'ret': "非websocket请求"})
    else:
        webscocket = request.environ.get('wsgi.websocket')
        ask_status_bright = AskStatusBridge(webscocket)
        try:
            ask_status_bright.open()
        except Exception as e:
            print(e)

        ask_status_bright.start()

    return JsonResponse({'code': 400})


def ask_pi_status(request):
    if not request.environ.get('wsgi.websocket'):
        return JsonResponse({'ret': "非websocket请求"})
    else:
        webscocket = request.environ.get('wsgi.websocket')
        ask_pi_status_bright = AskPiStatusBridge(webscocket)
        try:
            ask_pi_status_bright.open()
        except Exception as e:
            print(e)

        ask_pi_status_bright.start()

    return JsonResponse({'code': 400})


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


def set_status(request):
    if not request.environ.get('wsgi.websocket'):
        return JsonResponse({'ret': "非websocket请求"})
    else:
        websocket = request.environ.get('wsgi.websocket')
        status_alive_bright = StatusAliveBridge(websocket)
        try:
            status_alive_bright.open()
        except Exception as e:
            print(e)

        status_alive_bright.start()
    return HttpResponse("websocket端")


def auto_get_data(request, category_id, terminal_id):
    if not request.environ.get('wsgi.websocket'):
        return JsonResponse({'ret': "非websocket请求"})
    else:
        webscocket = request.environ.get('wsgi.websocket')
        auto_get_sensor_data_bright = AutoGetSensorDataBridge(webscocket,
                                                              category_id,
                                                              terminal_id)
        try:
            auto_get_sensor_data_bright.open()
        except Exception as e:
            print(e)

        auto_get_sensor_data_bright.start()

    return JsonResponse({'code': 400})


def change_warning_value(request):
    """
    根据前端获取的value，设置预警值
    :param request:
    :return:
    """
    value = request.POST.get("value")
    category_id = request.POST.get("category_id")
    terminal_id = request.POST.get("terminal_id")

    category = TerminalCategory.objects.filter(category_id=category_id)
    if category.exists():
        terminal = TerminalInfo.objects.filter(terminal_category=category.first(), terminal_id=terminal_id)
        if terminal.exists():
            warning_detail = WarningValue.objects.get(terminal=terminal.first())
            if warning_detail:
                warning_detail.value = value
                warning_detail.save()
                # 指令2为设置预警值操作
                write_command(2, int(category_id), int(terminal_id), int(value), cookie_cache_processor.get_verification())
                return JsonResponse({"code": 200})
        else:
            return JsonResponse({"code": 405})
    else:
        return JsonResponse({"code": 404})

