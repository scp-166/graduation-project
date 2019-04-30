from django.urls import path
from . import views

urlpatterns = [
    path('', views.show),

    path('temp/status/', views.show_temp_status),
    path('hum/status/', views.show_hum_status),

    # 后面改为restful形式
    path('temp/<int:category_id>/<int:terminal_id>/', views.show_temp),
    path('hum/<int:category_id>/<int:terminal_id>/', views.show_hum),

    path('temp/<int:category_id>/<int:terminal_id>/<int:days>/',
         views.show_temp_by_day),
    path('hum/<int:category_id>/<int:terminal_id>/<int:days>/',
         views.show_hum_by_day),

]
