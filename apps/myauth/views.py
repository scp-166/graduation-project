from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.core.management import utils

from utils.cache_process import cookie_cache_processor


class Login(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        telephone = request.POST.get('telephone')
        password = request.POST.get('password')
        print(telephone)
        print(password)
        user = authenticate(request, username=telephone, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return JsonResponse({'code': 200})
            else:
                return JsonResponse({"code": 400})
        return JsonResponse({'code': 405})


def logout_view(request):
    user = request.user
    print(user)
    print(request.session.keys())
    print(request.session.items())
    logout(request)
    return JsonResponse({"code": 200})


class Token(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        telephone = request.POST.get('telephone')
        password = request.POST.get('password')
        print(telephone)
        print(password)
        user = authenticate(request, username=telephone, password=password)
        if user:  # 验证通过
            if user.is_active:
                token = utils.get_random_secret_key()  # 随机获得一个token值
                cookie_cache_processor.set_verification(token)  # 设置进缓存中
                response = JsonResponse({'code': 200})
                response.set_cookie('token', token)  # 将其设置在cookies中，默认两个星期过期
                return response
            else:
                return JsonResponse({"code": 400})
        return JsonResponse({'code': 405})


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, reverse


@login_required(login_url='/auth/view2/')
def my_view(request):
    print(type(reverse('view2')))
    print(reverse('view2'))
    return JsonResponse({'code': 10086})

def my_redirect_field(request):
    return JsonResponse({'code': 1})