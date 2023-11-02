import asyncio
import json
import logging
import os
import time

from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib import auth
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.cache import cache
from django.views import View
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import connections, DEFAULT_DB_ALIAS
from django.views.decorators.csrf import csrf_protect

from .utils import generate_verification_code
from .decorators import time_test, async_decorator
from .models import UserModel

logger = logging.getLogger('debug_')
logger_exception = logging.getLogger('django_exception')


def add(request):
    # UserModel.objects.create(username='ss', password='uu', nickname='star', nickname1='sssss')

    def get_current_database():
        connection = connections[DEFAULT_DB_ALIAS]
        database_name = connection.settings_dict['NAME']
        database_engine = connection.settings_dict['ENGINE']
        return database_name, database_engine

    # 调用函数获取当前数据库信息
    db_name, db_engine = get_current_database()
    print(f"当前应用程序使用的数据库：{db_name}，数据库引擎：{db_engine}")
    return HttpResponse('add success')


@csrf_protect
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # 在这里处理登录逻辑，例如验证用户名和密码

        # 示例代码，简单判断用户名和密码是否正确
        if username == 'admin' and password == 'sss':
            return 'login success'
        else:
            return 'login failure'

    return render(request, 'login.html')


@time_test
def sync_view(request):
    for i in range(3):
        time.sleep(1)
    return HttpResponse('Sync Done')


@async_decorator
async def async_view(request):
    for i in range(3):
        await asyncio.sleep(1)
    return HttpResponse('Async Done')


@require_GET
def cors_(request):
    return HttpResponse('cors test')


@require_POST
@csrf_exempt  # tag1 关闭csrf防护
def register(request):
    """
        以视图函数实现注册功能，接收JSON数据格式的POST请求。限定后端视图函数仅接收POST请求，GET请求的模板渲染通过前端完成。
    :param request: None
    :return: Json data
    """
    data = json.loads(request.body)  # tag3,接收json类型数据格式的post请求
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
                logger.info('register username:%s' % username)  # tag7，记录日志保存信息至debug.log文件中
                return JsonResponse({'code': 200, 'msg': '注册成功'})
            else:
                return JsonResponse({'code': 403, 'msg': '该邮箱已注册'})
        else:
            return JsonResponse({'code': 403, 'msg': '该用户名已存在'})
    else:
        return JsonResponse({'code': 403, 'msg': '两次输入的密码不一致'})


@method_decorator(csrf_exempt, name='dispatch')  # tag1，对类视图关闭csrf防护
class Login(View):  #
    """
        以类视图的方式实现登录功能，接收from表单数据格式的POST请求。
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


@require_GET  # tag4,限制请求方式为GET
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


@cache_page(60 * 5)  # tag8，缓存视图函数的输出结果5分钟
@csrf_exempt
@require_POST  # tag4，限制请求方式为POST
def query(request, *args, **kwargs):  # tag2，接收多个过滤参数
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
    res1 = User.objects.filter(**query_dict).all().values('id')  # queryset对象。tag11，queryset数据类型的验证。
    res11 = res1[:2]  # 切片操作

    res2 = User.objects.filter(id=24)  # queryset对象，指向单个数据
    res21 = User.objects.get(id=25)  # models.User对象

    res3 = User.objects.all()  # queryset对象
    res31 = res3.first()  # models.User对象
    res32 = res3.order_by('first_name')  # queryset对象，链式调用
    res321 = res32.values('username')  # queryset对象，链式调用

    res4 = User.objects.all()[:3]  # queryset对象，切片

    users = list(User.objects.all())  # 将 QuerySet 转换为列表
    for user in users:  # 这里不会执行数据库查询
        print(user.username)
    for user in users:  # 这里也不会执行数据库查询
        print(user.email)

    res5 = User.objects.all()
    list(res5)  # 执行查询（结果被缓存）
    list(res5)  # 不执行查询，使用缓存结果

    res6 = User.objects.all()
    new_user = User(username='sss', password='uuu', email='iii')
    res61 = list(res6)
    res61.append(new_user)  # 执行list的append添加数据

    return JsonResponse({'code': 200, 'msg': list(res1)})


"""
        
    res1数据类型为：<class 'django.db.models.query.QuerySet'>
    res1的值为：<QuerySet [{'id': 24}, {'id': 25}, {'id': 26}, {'id': 27}, {'id': 28}, {'id': 29}, {'id': 30}, {'id': 31}, {'id': 32}, {'id': 33}]>
    
    res11数据类型：<class 'django.db.models.query.QuerySet'>
    res11值：<QuerySet [{'id': 24}, {'id': 25}]>
    
    res2数据类型：<class 'django.db.models.query.QuerySet'>
    res2值：<QuerySet [<User: star>]>
    
    res21数据类型：<class 'django.contrib.auth.models.User'>
    
    res3数据类型：<class 'django.db.models.query.QuerySet'>
    res31数据类型：<class 'django.contrib.auth.models.User'>
    
    res61值：[<User: star>, <User: star1>, <User: star2>, <User: star3>, <User: star4>, <User: star5>, <User: star6>, <User: star7>, <User: star8>, <User: star9>, <User: sss>]
    
    获取数据库查询（批量数据）的过程分为两步：
    第一步：获取queryset类型数据，不消耗查询时间不占用内存。大数据量的复杂处理可以选择该步骤内处理。
    第二步：将queryset类型的数据转换为实际数据（执行list(res1)、print(res1)等）。执行中耗费查询时间，执行后占用较大内存。
    
    利用queryset的特性在以下场景优势明显（相比输出具体数据后进行处理）：
    1、需要执行切片的情况。避免了在python端对大量数据执行处理的性能损耗。
    2、使用链式调用或条件查询等情况。在链式查询的不同阶段快速输出不同的结果。
    3、重复调用查询结果的情况。初次queryset被执行的结果被缓存，提高后续调用结果的速度。
    
    适合将queryset数据转为list数据进行处理的情况：
    1、需要对数据进行多次迭代。每次queryset迭代需要查询一次，转为list可以提高速度。
    2、需要进行特定的列表操作。如append、insert、remove等。
    
    
    
    
"""


@login_required
def view(request):
    id = request.session.get('_auth_user_id')
    user = User.objects.get(id=id)
    return JsonResponse({
        'code': 200,
        'msg': '用户%s已登录，具备访问权限' % user.username
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # tag6，使用JWT进行登录状态的判断
def view1(request):
    user = request.user
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


@csrf_exempt
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
            except Exception as e:  # tag5，捕获到异常的具体类型，保存文件至exception.log文件
                logger_exception.exception(e)
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


@csrf_exempt
@require_POST
def upload_file(request):
    """
        文件上传
    :param request:
    :return:
    """
    file = request.FILES['file']
    if file:
        filename = file.name
        bas_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 获取项目根目录
        file_path = os.path.join(bas_dir, 'upload_files', filename)  # 构建文件的完整路径
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return JsonResponse({'code': 200, 'msg': '文件上传成功'})
    else:
        return JsonResponse({'code': 403, 'msg': '未传入有效文件'})
