from django.shortcuts import render
from django.http import JsonResponse

from .models import *


def show(request):
    context = {
        'data': [1, 2, 3, 4, 5, 6]
    }
    return render(request, 'show.html', context)


def show_temp(request, category_id, terminal_id):
    return render(request, 'show_temp_sensor_data.html')


def show_hum(request, category_id, terminal_id):
    data = None
    category = TerminalCategory.objects.filter(category_id=category_id)
    if category.exists():
        sensor = TerminalInfo.objects.filter(terminal_category=category.first(),
                                             terminal_id=terminal_id)
        if sensor.exists():
            data = TerminalData.objects.filter(
                terminal=sensor.first())  # 拿到具体传感器的所有内容
    context = {
        'sensor_data': data
    }
    return render(request, 'show_hum_sensor_data.html', context=context)


def show_temp_status(request):
    return render(request, 'show_temp_sensor_status.html')


def show_hum_status(request):
    context = {}
    category = TerminalCategory.objects.filter(category_name="湿度传感器")
    if category:
        terminal_info = TerminalInfo.objects.filter(
            terminal_category=category.first())
        count = terminal_info.count()
        context = {
            'all_temp_sensor_info': terminal_info,
            'sensor_count': count,
        }

    return render(request, 'show_hum_sensor_status.html', context=context)


def show_temp_by_day(request, category_id, terminal_id, days):
    return render(request, 'show_temp_sensor_data.html')


import datetime
from django.utils import timezone
from django.db.models import Sum, Avg


def show_hum_by_day(request, category_id, terminal_id, days):

    today = timezone.now().date()  # 今天
    sensor_data_average_list = []  # 保存每天的访问总数
    dates = []  # 保存各日期，给前端使用

    category = TerminalCategory.objects.filter(category_id=category_id)
    if category.exists():
        sensor = TerminalInfo.objects.filter(terminal_category=category.first(),
                                             terminal_id=terminal_id)
        if sensor.exists():

            for i in range(days, -1, -1):  # 获取前n天(包括今天)

                date = today - datetime.timedelta(days=i)  # 取得前第i天
                dates.append(date.strftime("%m/%d"))  # 前端要求字符串

                today_sensor_detail = TerminalData.objects.filter(
                    create_time=date)
                result = today_sensor_detail.aggregate(
                    data_average=Avg(
                        "data"))  # 分组统计，统计命名为data_average
                # print(result['data_average'])  # 可以获取最终结果
                sensor_data_average_list.append(result["data_average"] or 0)

    context = {
        'dates': dates,
        'sensor_data': sensor_data_average_list,
    }

    return render(request, 'show_hum_sensor_data_by_day.html', context=context)
