import random
import string

from django.shortcuts import render, HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required


def add(request):
    for i in range(3):
        user = User.objects.create_user(username='user%s' % i, password='mmm')
    user.is_active = False
    user.save()
    return JsonResponse({
        'code': 200,
        'msg': '新增用户成功'
    })


def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    user = User.objects.filter(username=username).first()
    if not user:
        User.objects.create_user(username=username, password=password, email=email)
        return JsonResponse({'code':200, 'msg':'注册成功'})
    else:
        return JsonResponse({
            'code': 403,
            'msg': '该用户名已存在'
        })


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    username = request.POST.get('username')
    password = request.POST.get('password')
    # 判断是否存在该用户
    user = User.objects.filter(username=username).first()
    if user:
        # 判断用户是否激活
        if user.is_active:
            # 判断用户名密码是否匹配
            if authenticate(username=username, password=password):
                auth.login(request, user)
                return JsonResponse({'code':200, 'msg':'登录成功'})
            else:
                return JsonResponse({
                    'code': 403,
                    'msg': '认证失败'
                })
        else:
            return JsonResponse({
                'code': 403,
                'msg': '用户未激活'
            })
    else:
        return JsonResponse({
            'code': 403,
            'msg': '用户不存在'
        })


def logout_(request):
    logout(request)
    return JsonResponse({
        'code': 200,
        'msg': '登出成功'
    })


def query(request):
    users = User.objects.all().values('username')
    user = User.objects.filter(username='userss1').first()
    print(user.is_active)
    return JsonResponse({
        'code': 200,
        'msg': list(users)
    })


@login_required
def view(request):
    id = request.session.get('_auth_user_id')
    user = User.objects.get(id=id)
    return JsonResponse({
        'code': 200,
        'msg': '用户%s已登录，具备访问权限' % user.username
    })


@login_required
def change_password(request):
    if request.method == 'GET':
        return render(request, 'change_password.html')
    id = request.session.get('_auth_user_id')
    user = User.objects.get(id=id)
    password = request.POST.get('password')
    new_password = request.POST.get('new_password')
    if authenticate(username=user.username, password=password):
        # user.password = new_password
        user.set_password(new_password)
        user.save()
        return JsonResponse({
            'code': 200,
            'msg': '密码修改成功'
        })

    else:
        return JsonResponse({
            'code': 403,
            'msg': '原密码验证失败'
        })


# 生成特定长度的验证码，包含数字和字母
def generate_verification_code(length):
    # 定义验证码中包含的字符类型
    chars = string.ascii_letters + string.digits  # 包含大小写字母和数字
    # 使用random.choices方法生成随机验证码
    code = ''.join(random.choices(chars, k=length))
    return code


def reset_password(request):
    if request.method == 'GET':
        captcha = generate_verification_code(6)
        print(captcha)
        return render(request, 'reset_password.html')
    # username = request.POST.get('username')
    # email = request.POST.get('email')
    # captcha = request.POST.get('captcha')
    # password = request.POST.get('password')

