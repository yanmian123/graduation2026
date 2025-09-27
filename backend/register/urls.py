from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    # path('login/', views.login, name='login'),  # 添加登录路径
]