from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  # 要求登录才能访问
from django.contrib.auth import get_user_model
from .serializers import UserInfoSerializer, UserInfoUpdateSerializer

User=get_user_model()

class UserInfoView(APIView):
    """
    处理用户信息的获取（GET）和更新（PUT）
    - 仅登录用户可访问（IsAuthenticated 权限）
    - 用户只能操作自己的信息
    """
    """获取和更新用户信息的视图"""
    permission_classes = [IsAuthenticated]  # 仅允许已认证用户访问

    def get(self, request):
        """获取当前登录用户的信息"""
        user = request.user
        serializer = UserInfoSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """更新当前登录用户的信息"""
        user = request.user
        #传入用户实例和请求数据，partial=True允许部分更新
        serializer = UserInfoUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        #验证失败返回错误信息
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)