from django.urls import path
from . import views

app_name = 'myauth'

urlpatterns = [
    path('login', views.Login.as_view()),
    path('token_login/', views.TokenLogin.as_view()),
    path('logout/', views.logout_view),
    path('token/', views.Token.as_view()),
    path('view/', views.my_view, name="view1"),
    path('view2/', views.my_redirect_field, name='view2'),
]
