from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache
from apps.exhibition.models import TerminalInfo,TerminalData


def control_led(request):
    data = TerminalData.objects.filter(terminal_id__type_id=2)
    print(data.first().status)
    context = {
        'data': data,
    }
    return render(request, 'LedControl.html', context)


def change_led_status(request, led_id):
    print(led_id)
    led = TerminalData.objects.filter(terminal_id__type_id=2,terminal_id__terminal_id=led_id)
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
