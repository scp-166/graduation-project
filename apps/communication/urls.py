from django.urls import path
from . import views

urlpatterns = [
    path('', views.control_led),

    path('echo/', views.echo, name='communicate_with_echo'),

    path('ask_status/pi/', views.ask_pi_status, name='ask_pi_status'),
    path('ask_status/', views.ask_status, name='ask_terminal_status'),

    path('auto_get_data/<int:category_id>/<terminal_id>/', views.auto_get_data, name='auto_get_terminal_data'),

    path('warning_value/', views.change_warning_value, name='change_waring_value'),

    path('change_led/<int:led_id>/', views.change_led_status),
    path('command/', views.TestCommand.as_view()),
    path('set_status/', views.set_status, name='set_terminal_status'),

]
