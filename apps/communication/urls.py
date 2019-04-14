from django.urls import path
from . import views


urlpatterns = [
    path('', views.control_led),
    path('change_led/<int:led_id>/', views.change_led_status),
    path('is_alive/', views.is_alive),
]