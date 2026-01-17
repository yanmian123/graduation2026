from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny  # 要求登录才能访问
from django.contrib.auth import get_user_model
from .serializers import UserInfoSerializer, UserInfoUpdateSerializer
from article_publish.models import Article, Comment
from django.db.models import Count

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

    def post(self, request):
        """处理用户头像上传"""
        user = request.user
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
            user.save()
            serializer = UserInfoSerializer(user)
            return Response({
                'message': '头像上传成功',
                'avatar': serializer.data['avatar']
            }, status=status.HTTP_200_OK)
        return Response(
            {'error': '未提供头像文件'},
            status=status.HTTP_400_BAD_REQUEST
        )

class ActiveUsersView(APIView):
    """
    获取活跃用户列表
    按用户发布的文章数量排序，取前5名活跃用户
    """
    permission_classes = [AllowAny]  # 允许所有人访问
    
    def get(self, request):
        # 获取活跃用户：按发布的文章数量排序，取前5名
        active_users = User.objects.annotate(
            article_count=Count('articles'),
            comment_count=Count('comments')
        ).order_by('-article_count', '-comment_count')[:5]
        
        # 构建响应数据
        data = []
        for user in active_users:
            data.append({
                'id': user.id,
                'username': user.username,
                'avatar': request.build_absolute_uri(user.avatar.url) if user.avatar else None,
                'article_count': user.article_count,
                'help_count': user.comment_count  # 使用评论数作为帮助人数的近似值
            })
        
        return Response(data, status=status.HTTP_200_OK)