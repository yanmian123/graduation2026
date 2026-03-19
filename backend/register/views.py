from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .serializers import RegisterSerializer
from .models import User
from django.core.cache import cache
import random

@api_view(['POST'])
@permission_classes([AllowAny])
def send_register_code(request):
    """发送注册验证码"""
    email = request.data.get('email')
    
    if not email:
        return Response(
            {"error": "请输入邮箱"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 检查邮箱是否已被注册
    if User.objects.filter(email=email).exists():
        return Response(
            {"error": "该邮箱已被注册"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 生成6位随机验证码
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    # 将验证码存入缓存，5分钟有效
    cache_key = f'register_code_{email}'
    cache.set(cache_key, code, 300)  # 300秒 = 5分钟
    
    # 这里应该发送邮件，简化版直接返回验证码
    # 实际项目中需要配置邮件发送功能
    return Response({
        "message": "验证码已发送",
        "code": code  # 开发环境返回验证码，生产环境应该发送邮件
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    print(f"Received data: {request.data}")  # 打印接收到的数据
    
    # 验证邮箱验证码
    email = request.data.get('email')
    code = request.data.get('verification_code')
    
    if not email or not code:
        return Response(
            {"error": "请输入邮箱和验证码"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 验证验证码
    cache_key = f'register_code_{email}'
    cached_code = cache.get(cache_key)
    
    if not cached_code or cached_code != code:
        return Response(
            {"error": "验证码错误或已过期"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 验证码验证通过，清除验证码
    cache.delete(cache_key)
    
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    """获取当前用户信息"""
    try:
        user = request.user
        
        # 检查用户是否通过实名认证
        from user_info.models import VerificationApplication
        verification = VerificationApplication.objects.filter(
            user=user,
            status='APPROVED'
        ).first()
        
        is_verified = verification is not None
        
        return Response({
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'avatar': user.avatar.url if user.avatar else None,
            'email': user.email,
            'phone_number': user.phone_number,
            'is_enterprise': user.is_enterprise,
            'is_verified': is_verified,
            'verification_type': verification.verification_type if verification else None
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

