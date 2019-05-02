from django.urls import path
from . import views

app_name = 'myauth'

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('token_login/', views.TokenLogin.as_view(), name='token_login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/', views.Token.as_view(), name='set_token_together'),

]
