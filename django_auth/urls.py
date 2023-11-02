"""
URL configuration for django_auth project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from app01 import views

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/query/', views.query),
    path('accounts/view/', views.view),
    path('accounts/view1/', views.view1),
    path('accounts/register/', views.register),
    path('accounts/logout/', views.logout_),
    path('accounts/chpassword/', views.change_password),
    path('accounts/repassword/', views.reset_password),
    path('accounts/send_mail/', views.send_mail_),
    path('accounts/login/', views.Login.as_view()),
    path('upload_file/', views.upload_file),
    path('cors/', views.cors_),
    path('sync/', views.sync_view),
    path('async/', views.async_view),
    path('login/', views.login_view, name='login'),
    path('add/', views.add, name='add'),
]
