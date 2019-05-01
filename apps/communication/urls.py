from django.urls import path
from . import views

urlpatterns = [
    path('', views.control_led),
    path('change_led/<int:led_id>/', views.change_led_status),
    path('is_alive/', views.is_alive),
    path('command/', views.TestCommand.as_view()),
    path('is_active/', views.is_active),

    path('auto_get_data/<int:category_id>/<terminal_id>/', views.auto_get_data),

]
