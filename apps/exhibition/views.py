from django.shortcuts import render
from django.http import JsonResponse
import datetime
from django.utils import timezone
from django.db.models import Avg

from .models import *


def show_index(request):
    return render(request, 'real_index.html')


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


def show_sensor_status(request, category_id):
    category = TerminalCategory.objects.filter(category_id=category_id)
    terminal_info = TerminalInfo.objects.filter(
        terminal_category=category.first())
    count = terminal_info.count()
    context = {
        'category_id': category.first().category_id,
        'all_temp_sensor_info': terminal_info,
        'sensor_count': count,
    }
    return render(request, 'sensor_status.html', context=context)


def show_sensor_data_by_day(category_id, terminal_id, days):
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
                dates.append(date.strftime("%Y/%m/%d"))  # 前端要求字符串

                today_sensor_detail = TerminalData.objects.filter(
                    terminal=sensor.first(),
                    create_time__date=date)
                result = today_sensor_detail.aggregate(
                    data_average=Avg(
                        "data"))  # 分组统计，统计命名为data_average
                # print(result['data_average'])  # 可以获取最终结果
                sensor_data_average_list.append(float('%.2f' % result["data_average"]) if result["data_average"] else 0)

    return dates, sensor_data_average_list


def get_data_by_week(request):
    category_id = request.GET.get("category_id")
    terminal_id = request.GET.get("terminal_id")

    dates, sensor_data_average_list = show_sensor_data_by_day(category_id, terminal_id, 6)
    print(dates)
    print(sensor_data_average_list)
    return JsonResponse({"code": 200, 'dates': dates, 'sensor_data_average_list': sensor_data_average_list})


def get_data_by_month(request):

    category_id = request.GET.get('category_id')
    terminal_id = request.GET.get('terminal_id')

    year = timezone.now().year  # 当年

    sensor_data_average_list = []  # 保存每天的访问总数
    months = []  # 保存各日期，给前端使用

    category = TerminalCategory.objects.filter(category_id=category_id)
    if category.exists():
        print(category.first())
        sensor = TerminalInfo.objects.filter(terminal_category=category.first(),
                                             terminal_id=terminal_id)
        if sensor.exists():
            print(sensor.first())
            for month in range(1, 12):  # 获取前12月

                months.append("/".join([str(year), str(month)]))  # 前端要求字符串

                today_sensor_detail = TerminalData.objects.filter(
                    terminal=sensor.first(),
                    create_time__month=month)
                print(today_sensor_detail)
                result = today_sensor_detail.aggregate(
                    data_average=Avg(
                        "data"))  # 分组统计，统计命名为data_average

                # print(type(result['data_average']))  # float

                sensor_data_average_list.append(float('%.2f' % result["data_average"]) if result["data_average"] else 0)

    return JsonResponse({'code': 200, 'months': months, 'sensor_data_average_list': sensor_data_average_list})

