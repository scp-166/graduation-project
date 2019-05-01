from django.urls import path
from . import views

app_name = 'exhibition'

urlpatterns = [
    path('', views.show_index, name='index'),

    path('sensor/<int:category_id>', views.show_sensor_status, name='sensor_status'),

    # 后面改为restful形式
    path('temp/<int:category_id>/<int:terminal_id>/', views.show_temp),
    path('hum/<int:category_id>/<int:terminal_id>/', views.show_hum),


    path('data/cur_week', views.get_data_by_week),
    path('data/month/', views.get_data_by_month),

]
