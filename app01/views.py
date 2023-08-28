from .utils import generate_verification_code

from django.shortcuts import render, HttpResponse, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.cache import cache


def test(request):
    cache.set('username', 'star')
    return HttpResponse(cache.get('username'))


def add(request):
    for i in range(3):
        user = User.objects.create_user(username='useroo%s' % i, password='mmm')
    # user.is_active = False
    # user.save()
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
        if not User.objects.filter(email=email).first():
            User.objects.create_user(username=username, password=password, email=email)
            return JsonResponse({'code':200, 'msg':'注册成功'})
        else:
            return JsonResponse({'code': 403, 'msg': '该邮箱已注册'})
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
    new_repeat_password = request.POST.get('new_repeat_password')
    if new_repeat_password == new_password:
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
    else:
        return JsonResponse({
            'code': 403,
            'msg': '两次输入的新密码不一致'
        })


def reset_password(request):
    if request.method == 'GET':
        return render(request, 'reset_password.html')
    else:
        email = request.POST.get('email')
        username = request.POST.get('username')
        code = request.POST.get('code')
        password = request.POST.get('password')
        repeat_password = request.POST.get('repeat_password')
        user = User.objects.filter(email=email).first()
        if user.username == username:
            if code == cache.get(email):
                if password == repeat_password:
                    user.set_password(password)
                    return JsonResponse({'code': 200, 'msg': '密码重置成功'})
                else:
                    return JsonResponse({'code': 403, 'msg': '两次输入的密码不一致'})
            else:
                return JsonResponse({'code': 403, 'msg': '邮箱验证码不匹配'})
        else:
            return JsonResponse({'code': 403, 'msg': '用户名和邮箱不匹配'})



def send_mail_(request):  # 默认为POST方法
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        user = User.objects.filter(email=email).first()
        if user and user.username == username:
            code = generate_verification_code(6)
            cache.set(email, code)
            try:
                send_mail(
                    '重置密码邮件',
                    '这是重置密码所需要的验证码：%s' % code,
                    'coastline_s@qq.com',
                    [email],
                    # fail_silently=True,  # 发送失败后是否静默，默认为False（也就是失败会报错）
                )
                print('code:', code)
            except:
                return JsonResponse({'code': 403, 'msg': '邮件发送失败，请检查邮箱地址'})
            return JsonResponse({
                'code': 200,
                'msg': '邮件发送成功'
            })
        else:
            return JsonResponse({
                'code': 403,
                'msg': '用户名和邮箱不匹配'
            })



