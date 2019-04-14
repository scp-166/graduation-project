from django.urls import path
from . import views


urlpatterns = [
    path('', views.index),
    path('chat/', views.chat),
    path('echo/', views.echo),
    path('is_active/', views.is_active),

]