from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import RegisterSerializer
from .models import User
from django.core.cache import cache
import random

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    print(f"Received data: {request.data}")  # 打印接收到的数据
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "注册成功！请登录"},
            status=status.HTTP_201_CREATED
        )
    print(f"Errors: {serializer.errors}")  # 打印验证错误
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_reset_code(request):
    """发送重置密码验证码"""
    username = request.data.get('username')
    email = request.data.get('email')
    
    # 验证用户名和邮箱是否匹配
    try:
        user = User.objects.get(username=username, email=email)
    except User.DoesNotExist:
        return Response(
            {"error": "用户名或邮箱不正确"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 生成4位随机验证码
    code = str(random.randint(1000, 9999))
    
    # 将验证码存入缓存，5分钟有效
    cache_key = f'reset_code_{username}'
    cache.set(cache_key, code, 300)  # 300秒 = 5分钟
    
    # 这里应该发送邮件，简化版直接返回验证码
    # 实际项目中需要配置邮件发送功能
    return Response({
        "message": "验证码已发送",
        "code": code  # 开发环境返回验证码，生产环境应该发送邮件
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """重置密码"""
    username = request.data.get('username')
    code = request.data.get('code')
    new_password = request.data.get('new_password')
    
    # 验证验证码
    cache_key = f'reset_code_{username}'
    cached_code = cache.get(cache_key)
    
    if not cached_code or cached_code != code:
        return Response(
            {"error": "验证码错误或已过期"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 更新密码
    try:
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        
        # 清除验证码
        cache.delete(cache_key)
        
        return Response({"message": "密码重置成功"})
    except User.DoesNotExist:
        return Response(
            {"error": "用户不存在"},
            status=status.HTTP_400_BAD_REQUEST
        )

