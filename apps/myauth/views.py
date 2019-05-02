from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.core.management import utils


from utils.cache_process import cookie_cache_processor


class TokenLogin(View):
    def get(self, request):
        return render(request, 'token_login.html')

    def post(self, request):
        telephone = request.POST.get('telephone')
        password = request.POST.get('password')
        user = authenticate(request, username=telephone, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return JsonResponse({'code': 200})
            else:
                return JsonResponse({"code": 400})
        return JsonResponse({'code': 405})


class Login(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        telephone = request.POST.get('telephone')
        password = request.POST.get('password')
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


# method_decorator装饰器将函数装饰器转换成方法装饰器，这样它就可以用于实例方法。
# @method_decorator(login_required(login_url='/auth/login/'), name='dispatch')  # name指定修饰的请求类型
class Token(View):
    # @method_decorator(login_required)  # 在函数上装饰
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

