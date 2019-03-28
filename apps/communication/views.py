from django.shortcuts import render
from apps.exhibition.models import TerminalInfo,TerminalData


def control_led(request):
    data = TerminalData.objects.filter(terminal_id__type_id=2)
    print(data.first().status)
    context = {
        'data': data,
    }
    return render(request, 'LedControl.html', context)
