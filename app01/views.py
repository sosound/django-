import json
import logging

from .utils import generate_verification_code

from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.cache import cache
from django.views import View
from django.views.decorators.http import require_POST, require_GET
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@require_POST
def register(request):
    """
        以视图函数实现注册功能，接收JSON数据格式的POST请求。限定后端视图函数仅接收POST请求，GET请求的模板渲染通过前端完成。
    :param request: None
    :return: Json data
    """
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    repeat_password = data.get('repeat_password')
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    user = User.objects.filter(username=username).first()
    if password == repeat_password:
        if not user:
            if not User.objects.filter(email=email).first():  # 判断邮箱是否已存在
                User.objects.create_user(username=username, password=password, email=email, first_name=first_name,
                                         last_name=last_name)  # 向数据库新增用户
                return JsonResponse({'code': 200, 'msg': '注册成功'})
            else:
                return JsonResponse({'code': 403, 'msg': '该邮箱已注册'})
        else:
            return JsonResponse({'code': 403, 'msg': '该用户名已存在'})
    else:
        return JsonResponse({'code': 403, 'msg': '两次输入的密码不一致'})


class Login(View):
    """
        以类视图的方式实现登录功能，接收JSON数据格式的POST请求。
    """
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = User.objects.filter(username=username).first()  # 判断是否存在该用户
        if user:
            if user.is_active:  # 判断用户是否激活
                if authenticate(username=username, password=password):  # 判断用户名密码是否匹配
                    auth.login(request, user)
                    return JsonResponse({'code': 200, 'msg': '登录成功'})
                else:
                    return JsonResponse({'code': 403, 'msg': '认证失败'})
            else:
                return JsonResponse({'code': 403, 'msg': '用户未激活'})
        else:
            return JsonResponse({'code': 403, 'msg': '用户不存在'})

    def get(self, request):
        return render(request, 'login.html')


@require_GET
def logout_(request):
    """
        用户退出登录，只接受GET请求方式。
    :param request: None
    :return: Json data
    """
    logout(request)
    return JsonResponse({
        'code': 200,
        'msg': '登出成功'
    })


@require_POST
def query(request, *args, **kwargs):
    """
        查询功能，可接收数量不定的多个参数。限定POST请求，接收数据格式为JSON。
        如果传入的参数为空，则返回全部数据。
    :param request: 用户名or名or姓
    :return: 用户的id列表
    """
    data = json.loads(request.body)
    param1 = data.get('username')
    param2 = data.get('firstname')
    param3 = data.get('lastname')
    query_dict = {}
    if param1:
        query_dict['username'] = param1
    if param2:
        query_dict['first_name'] = param2
    if param3:
        query_dict['last_name'] = param3
    results = User.objects.filter(**query_dict).all().values('id')
    return JsonResponse({'code': 200, 'msg': list(results)})


@login_required
def view(request):
    id = request.session.get('_auth_user_id')
    user = User.objects.get(id=id)
    return JsonResponse({
        'code': 200,
        'msg': '用户%s已登录，具备访问权限' % user.username
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view1(request):
    user = request.user  # tag1，使用JWT进行登录状态的判断
    return Response({
        'code': 200,
        'msg': '用户%s已登录，具备访问权限（使用JWT验证）' % user.username
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
            except Exception as e:
                logger.exception(e)
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



