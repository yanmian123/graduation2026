
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import action
from .models import Article, Attachment, Comment, Like, Collection, Follow, Report
from register.models import User
from .serializers import ArticleSerializer, AttachmentSerializer, ArticleSerializer2,CommentSerializer,LikeStatusSerializer, CollectStatusSerializer, CollectionStatusSerializer,FollowStatusSerializer,ReportSerializer,ReportCreateSerializer
from user_info.serializers import UserSerializer
from django.db import models
import logging
import time
import os
from django.conf import settings
logger = logging.getLogger(__name__)
from notification.utils import create_notification

# 自定义权限：仅允许文章所有者操作（查看/编辑/删除）
class IsArticleOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
    
class ArticleViewSet(viewsets.ModelViewSet):
    """
    文章发布视图集：
    - list: 获取当前用户的所有文章
    - retrieve: 获取单个文章详情
    - create: 创建新文章（自动关联当前用户）
    - update: 全量更新文章（需传所有必填字段）
    - partial_update: 部分更新（如仅修改标题）
    - destroy: 删除文章
    """
    serializer_class = ArticleSerializer

    # 动态设置权限
    def get_permissions(self):
        """
        - 收藏/点赞：允许所有登录用户
        - 修改/删除文章：仅允许作者
        - 查看文章/评论：允许所有用户（包括未登录）
        """
        if self.action in ['collect', 'like']:
            # 收藏/点赞：必须登录，但无需是作者
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # 修改/删除：必须是作者
            permission_classes = [IsAuthenticated, IsArticleOwner]
        else:
            # 其他操作（如查看文章）：允许所有用户
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    
    def get_queryset(self):
        '''支持按分类、标签过滤和自定义排序'''
        queryset=Article.objects.all()
        category=self.request.query_params.get('category')
        tag=self.request.query_params.get('tag')
        keyword=self.request.query_params.get('keyword')
        ordering=self.request.query_params.get('ordering')
        user_only=self.request.query_params.get('user_only')
        user_id=self.request.query_params.get('user_id')
        is_draft=self.request.query_params.get('is_draft')
        
        # 如果请求参数 user_only=true，只返回当前用户的文章
        if user_only == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        
        # 如果请求参数 user_id存在，返回指定用户的文章
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # 如果请求参数 is_draft 存在，过滤草稿
        if is_draft is not None:
            queryset = queryset.filter(is_draft=(is_draft == 'true'))
        
        if category and category != 'all':
            queryset=queryset.filter(category=category)
        if tag:
            queryset=queryset.filter(tags__icontains=tag)
        if keyword:
            queryset=queryset.filter(models.Q(title__icontains=keyword) | models.Q(content__icontains=keyword))
            
        # 尊重前端传入的排序参数，如果没有则使用默认排序
        if ordering:
            return queryset.order_by(ordering)
        return queryset.order_by('-created_at')  # 按创建时间倒序
    
    def get_serializer_context(self):
        context=super().get_serializer_context() 
        context.update({'request': self.request}) # 补充请求对象
        return context
    
    def create(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        article=self.perform_create(serializer) # 保存文章基本信息（自动关联当前用户）
        print("请求中的文件：", request.FILES)
        
        return Response({
            "code": 201,
            "message": "文章发布成功",
            "data": {
                "postId": article.id,
                **serializer.data
                }
        },status=status.HTTP_201_CREATED)
        
    def perform_create(self, serializer):
        return serializer.save()    
    
    def update(self, request, *args, **kwargs):
        partial=kwargs.pop('partial', False)
        instance=self.get_object()
        serializer=self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            "code": 200,
            "message": "文章更新成功",
            "data": serializer.data
        })
        
    def destroy(self, request, *args, **kwargs):
        instance=self.get_object()
        self.perform_destroy(instance)
        return Response({
            "code": 204,
            "message": "文章删除成功"
        }, status=status.HTTP_204_NO_CONTENT)
        
    def retrieve(self, request, pk=None):
        article = self.get_object()
        serializer = ArticleSerializer(article, context={'request': request})
        # 新增：判断当前用户是否已关注文章作者
        is_followed = False
        if request.user.is_authenticated:
            # 检查 Follow 表中是否存在该关联
            is_followed = Follow.objects.filter(
                follower=request.user,
                followed=article.user
            ).exists()
        # 将关注状态添加到返回数据中
        data = serializer.data
        data['is_followed'] = is_followed
        return Response(data)

    # 增加阅读量
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def view(self, request, pk=None):
        article = self.get_object()
        article.view_count += 1
        article.save()
        return Response({'view_count': article.view_count})

    # 文章点赞/取消点赞
    @action(detail=True, methods=['post', 'delete'],  permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        article = self.get_object()
        logger.info(f"点赞操作 - 用户: {request.user.id}, 文章: {article.id}, 方法: {request.method}")
        
        # like, created = Like.objects.get_or_create(user=request.user, article=article)
        like_exists = Like.objects.filter(user=request.user, article=article).exists()
        logger.info(f"点赞操作 - 当前点赞状态: {like_exists}")
        
        if request.method == 'POST':
            if not like_exists:
                # 首次点赞
                logger.info(f"点赞操作 - 添加点赞记录")
                Like.objects.create(user=request.user, article=article)
                article.like_count += 1
                article.save()
                logger.info(f"点赞操作 - 点赞数更新为: {article.like_count}")
                
                # 发送点赞通知给文章作者
                if request.user != article.user:
                    create_notification(
                        recipient=article.user,
                        notification_type='post_liked',
                        title='文章被点赞',
                        message=f'{request.user.nickname}点赞了你的文章《{article.title}》',
                        related_object_id=article.id,
                        related_object_type='article'
                    )
            # 即使重复点赞，也返回当前状态（已点赞）
            return Response(LikeStatusSerializer({
                'is_liked': True,
                'count': article.like_count
            }).data)
            
        if request.method == 'DELETE':
            if like_exists:
                # 取消已有的点赞
                logger.info(f"点赞操作 - 删除点赞记录")
                Like.objects.filter(user=request.user, article=article).delete()
                article.like_count -= 1
                article.save()
                logger.info(f"点赞操作 - 点赞数更新为: {article.like_count}")
            # 即使重复取消，也返回当前状态（未点赞）
            return Response(LikeStatusSerializer({
                'is_liked': False,
                'count': article.like_count
            }).data)
            
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # 文章收藏/取消收藏
    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def collect(self, request, pk=None):
        logger.info(f"收藏操作 - 用户认证状态: {request.user.is_authenticated}")
        logger.info(f"请求头认证信息: {request.headers.get('Authorization')}")
        article = self.get_object()
        logger.info(f"收藏操作 - 用户: {request.user.id}, 文章: {article.id}, 方法: {request.method}")
        
        # collect, created = Collection.objects.get_or_create(user=request.user, article=article)
        collect_exists = Collection.objects.filter(user=request.user, article=article).exists()
        logger.info(f"收藏操作 - 当前收藏状态: {collect_exists}")
        
        if request.method == 'POST':
            if not collect_exists:
                logger.info(f"收藏操作 - 添加收藏记录")
                Collection.objects.create(user=request.user, article=article)
                article.star_count += 1
                article.save()
                logger.info(f"收藏操作 - 收藏数更新为: {article.star_count}")
                
                # 发送收藏通知给文章作者
                if request.user != article.user:
                    create_notification(
                        recipient=article.user,
                        notification_type='post_collected',
                        title='文章被收藏',
                        message=f'{request.user.nickname}收藏了你的文章《{article.title}》',
                        related_object_id=article.id,
                        related_object_type='article'
                    )
            # 即使重复收藏，也返回当前状态（已收藏）
            return Response(CollectStatusSerializer({
                'is_collected': True,
                'count': article.star_count
            }).data)
            
        if request.method == 'DELETE':
            if collect_exists:
                logger.info(f"收藏操作 - 删除收藏记录")
                Collection.objects.filter(user=request.user, article=article).delete()
                article.star_count -= 1
                article.save()
                logger.info(f"收藏操作 - 收藏数更新为: {article.star_count}")
            # 即使重复取消，也返回当前状态（未收藏）
            return Response(CollectStatusSerializer({
                'is_collected': False,
                'count': article.star_count
            }).data)
            
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # 获取文章评论
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def get_comments(self, request, pk=None):
        article = self.get_object()
        # 只返回顶级评论（parent为null的评论），回复通过serializer的replies字段返回
        comments = article.comments.filter(parent__isnull=True).order_by('-created_at')
        
        # 添加分页支持
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 5)
        
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        
        paginated_comments = paginator.paginate_queryset(comments, request)
        serializer = CommentSerializer(paginated_comments, many=True, context={'request': request})
        
        # 返回分页数据
        return paginator.get_paginated_response(serializer.data)
    
    # 获取收藏
    @action(detail=False, methods=['get'])
    def collections(self, request):
        user_id = request.query_params.get('user_id')
        
        if user_id:
            # 获取指定用户的收藏
            collections = Collection.objects.filter(user_id=user_id).order_by('-created_at')
        else:
            # 获取当前用户的收藏（需要认证）
            if not request.user.is_authenticated:
                return Response({'error': '需要登录'}, status=status.HTTP_401_UNAUTHORIZED)
            collections = Collection.objects.filter(user=request.user).order_by('-created_at')
        
        serializer = CollectionStatusSerializer(collections, many=True)
        return Response(serializer.data)

    # 发表评论
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_comment(self, request, pk=None):
        article = self.get_object()
        
        # 获取parent_id参数（如果有）
        parent_id = request.data.get('parent_id')
        parent_comment = None
        
        # 如果提供了parent_id，验证它是否存在
        if parent_id:
            try:
                parent_comment = Comment.objects.get(id=parent_id, article=article)
            except Comment.DoesNotExist:
                return Response({'error': 'Parent comment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            comment = serializer.save(article=article, parent=parent_comment)
            
            # 更新文章的评论数
            article.comment_count += 1
            article.save()
            
            # 生成通知
            from notification.utils import create_notification
            
            # 如果是回复评论，通知被回复的评论作者
            if parent_comment and request.user != parent_comment.user:
                create_notification(
                    recipient=parent_comment.user,
                    notification_type='post_comment',
                    title='新评论回复',
                    message=f"{request.user.nickname or request.user.username}回复了你的评论: {comment.content[:20]}...",
                    related_object_id=article.id,
                    related_object_type='article',
                    comment_id=comment.id
                )
            # 如果是顶级评论，通知文章作者
            elif not parent_comment and request.user != article.user:
                create_notification(
                    recipient=article.user,
                    notification_type='post_comment',
                    title='新评论通知',
                    message=f"{request.user.nickname or request.user.username}评论了你的文章: {comment.content[:20]}...",
                    related_object_id=article.id,
                    related_object_type='article',
                    comment_id=comment.id
                )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CommentViewSet(viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        
        # 检查是否是评论作者或文章作者
        if comment.user != request.user and comment.article.user != request.user:
            return Response(
                {'error': '只能删除自己的评论或文章作者可以删除文章下的评论'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 获取关联的文章
        article = comment.article
        
        # 计算要删除的评论总数（包括所有二级评论）
        if comment.parent is None:
            # 顶级评论：计算自身 + 所有二级评论的数量
            total_comments_to_delete = 1 + comment.replies.count()
        else:
            # 二级评论：只删除自己
            total_comments_to_delete = 1
        
        # 删除评论（会级联删除二级评论）
        comment.delete()
        
        # 减少文章的评论数
        article.comment_count -= total_comments_to_delete
        article.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_queryset(self):
        '''获取当前用户的评论'''
        queryset = Comment.objects.all()
        user_only = self.request.query_params.get('user_only')
        user_id = self.request.query_params.get('user_id')
        
        # 如果请求参数 user_only=true，只返回当前用户的评论
        if user_only == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        
        # 如果请求参数 user_id存在，返回指定用户的评论
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.order_by('-created_at')

    # 评论点赞/取消点赞
    @action(detail=True, methods=['post', 'delete'],permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        comment = self.get_object()
        like_exists = Like.objects.filter(user=request.user, comment=comment).exists()
        
        if request.method == 'POST':
            if not like_exists:
                Like.objects.create(user=request.user, comment=comment)
                comment.like_count += 1
                comment.save()
                return Response({'is_liked': True, 'count': comment.like_count})
            else:
                return Response({'is_liked': True, 'count': comment.like_count})
            
        if request.method == 'DELETE':
            if like_exists:
                Like.objects.filter(user=request.user, comment=comment).delete()
                comment.like_count -= 1
                comment.save()
                return Response({'is_liked': False, 'count': comment.like_count})
            else:
                return Response({'is_liked': False, 'count': comment.like_count})
            
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = []  # 移除默认认证要求
    
    def get_permissions(self):
        """根据不同的action设置不同的权限"""
        if self.action in ['retrieve', 'follow_status', 'info', 'followers', 'following', 'following_enterprises']:
            return []  # 获取用户详情和关注状态不需要认证
        return [IsAuthenticated()]  # 其他操作需要认证
    
    def retrieve(self, request, pk=None):
        """获取用户详情（包括is_enterprise字段）"""
        try:
            user = self.get_object()
            return Response({
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'avatar': user.avatar.url if user.avatar else None,
                'is_enterprise': user.is_enterprise,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'email': user.email,
                'follower_count': Follow.objects.filter(followed=user).count(),
                'following_count': Follow.objects.filter(follower=user, follow_type='user').count(),
                'following_enterprise_count': Follow.objects.filter(follower=user, follow_type='enterprise').count()
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get', 'put'], url_path='info')
    def info(self, request):
        """获取或更新当前用户信息"""
        try:
            user = request.user
            
            if request.method == 'PUT':
                serializer = UserSerializer(user, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'id': user.id,
                    'username': user.username,
                    'nickname': user.nickname,
                    'avatar': user.avatar.url if user.avatar else None,
                    'sex': user.sex,
                    'age': user.age,
                    'major': user.major,
                    'phone_number': user.phone_number,
                    'graduation_school': user.graduation_school,
                    'education_level': user.education_level,
                    'graduation_year': user.graduation_year,
                    'current_status': user.current_status,
                    'intended_position': user.intended_position,
                    'intended_salary': user.intended_salary,
                    'address': user.address,
                    'intended_city': user.intended_city,
                    'personal_profile': user.personal_profile,
                    'is_enterprise': user.is_enterprise,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                    'email': user.email,
                    'follower_count': Follow.objects.filter(followed=user).count(),
                    'following_count': Follow.objects.filter(follower=user, follow_type='user').count(),
                    'following_enterprise_count': Follow.objects.filter(
                        follower=user,
                        follow_type='enterprise'
                    ).count()
                })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='followers')
    def followers(self, request):
        """获取当前用户的粉丝列表"""
        try:
            followers = Follow.objects.filter(followed=request.user).select_related('follower')
            result = []
            for follow in followers:
                result.append({
                    'id': follow.follower.id,
                    'username': follow.follower.username,
                    'nickname': follow.follower.nickname,
                    'avatar': follow.follower.avatar.url if follow.follower.avatar else None
                })
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='following')
    def following(self, request):
        """获取当前用户关注的用户列表"""
        try:
            following = Follow.objects.filter(follower=request.user, follow_type='user').select_related('followed')
            result = []
            for follow in following:
                result.append({
                    'id': follow.followed.id,
                    'username': follow.followed.username,
                    'nickname': follow.followed.nickname,
                    'avatar': follow.followed.avatar.url if follow.followed.avatar else None
                })
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='following-enterprises')
    def following_enterprises(self, request):
        """获取当前用户关注的企业列表"""
        try:
            from enterprise.models import Enterprise
            
            # 获取当前用户关注的企业用户
            enterprise_follows = Follow.objects.filter(
                follower=request.user,
                follow_type='enterprise'
            ).select_related('followed')
            
            result = []
            for follow in enterprise_follows:
                user = follow.followed
                # 获取企业信息
                try:
                    enterprise = Enterprise.objects.get(user=user)
                    result.append({
                        'id': enterprise.id,  # 使用企业ID而不是用户ID
                        'user_id': user.id,    # 保留用户ID用于其他用途
                        'username': user.username,
                        'name': enterprise.name,
                        'logo': enterprise.logo.url if enterprise.logo else None,
                        'industry': enterprise.industry,
                        'scale': enterprise.scale
                    })
                except Enterprise.DoesNotExist:
                    continue
            
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 获取关注状态
    @action(detail=True, methods=['get'])
    def follow_status(self, request, pk=None):
        followed_user = self.get_object()
        is_following = Follow.objects.filter(
            follower=request.user,
            followed=followed_user
        ).exists()
        return Response({'is_following': is_following})

    # 关注/取消关注用户或企业
    @action(detail=True, methods=['post', 'delete'])
    def follow(self, request, pk=None):
        followed_user = self.get_object()
        
        logger.info(f"请求头认证信息: {request.headers.get('Authorization')}")
        logger.info(f"用户是否认证: {request.user.is_authenticated}")
        
        # 防止用户关注自己
        if request.user == followed_user:
            return Response(
                {"message": "不能关注自己"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 判断关注类型：用户还是企业
        follow_type = 'enterprise' if followed_user.is_enterprise else 'user'
        
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            followed=followed_user,
            defaults={'follow_type': follow_type}
        )
        
        if request.method == 'POST':
            if created:
                # 只有关注用户时才发送通知，关注企业不发送通知
                if follow_type == 'user':
                    create_notification(
                        recipient=followed_user,
                        notification_type='user_followed',
                        title='新粉丝关注',
                        message=f'{request.user.nickname or request.user.username}关注了你',
                        related_object_id=request.user.id,
                        related_object_type='user'
                    )
                return Response(
                    FollowStatusSerializer({'is_following': True}).data,
                    status=status.HTTP_201_CREATED
                )
            else:
                # 已经关注过的情况
                return Response(
                    FollowStatusSerializer({'is_following': True}).data,
                    status=status.HTTP_200_OK
                )
            
        if request.method == 'DELETE':
            if not created:  # 存在关注关系
                follow.delete()
                return Response(
                    FollowStatusSerializer({'is_following': False}).data,
                    status=status.HTTP_200_OK
                )
            else:
                # 不存在关注关系却要取消关注
                return Response(
                    FollowStatusSerializer({'is_following': False}).data,
                    status=status.HTTP_200_OK
                )
            
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        """举报用户"""
        reported_user = self.get_object()
        
        # 检查是否举报自己
        if request.user == reported_user:
            return Response(
                {'error': '不能举报自己'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查是否已经举报过该用户
        existing_report = Report.objects.filter(
            reporter=request.user,
            reported_user=reported_user,
            status='pending'
        ).first()
        
        if existing_report:
            return Response(
                {'error': '您已经举报过该用户，请等待管理员处理'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 创建举报
        report = Report.objects.create(
            reporter=request.user,
            reported_user=reported_user,
            report_type='user',
            reason=request.data.get('reason', ''),
            description=request.data.get('description', '')
        )
        
        return Response(
            {'message': '举报提交成功，管理员会尽快处理'},
            status=status.HTTP_201_CREATED
        )

class FileUploadView(APIView):
    '''附件上传接口'''
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, format=None):
        file=request.FILES.get('file')
        article_id=request.data.get('article_id')
        
        if not file:
            return Response({
                "code": 400,
                "message": "缺少文件"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 如果提供了 article_id，则作为附件上传到文章
        if article_id:
            article=get_object_or_404(Article, id=article_id)
            
            if article.user != request.user:
                return Response({
                    "code": 403,
                    "message": "无权限为该文章上传附件"
                }, status=status.HTTP_403_FORBIDDEN)
            
            attachment=Attachment(article=article, file=file)
            attachment.save()
            
            serializer=AttachmentSerializer(attachment)
            logger.info(f"用户 {request.user.username} 上传文件: {file.name}")
            return Response({
                "code": 201,
                "message": "附件上传成功",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            # 通用文件上传（用于认证、简历等）
            # 生成文件名
            file_extension = os.path.splitext(file.name)[1]
            new_filename = f"{request.user.id}_{int(time.time())}{file_extension}"
            
            # 保存文件
            upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'general')
            os.makedirs(upload_path, exist_ok=True)
            
            file_path = os.path.join(upload_path, new_filename)
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            # 返回文件URL
            file_url = f"/media/uploads/general/{new_filename}"
            logger.info(f"用户 {request.user.username} 上传通用文件: {file.name}")
            
            return Response({
                "code": 201,
                "message": "文件上传成功",
                "url": file_url
            }, status=status.HTTP_201_CREATED)
        
        
class PostSearchView(APIView):
    """简单的文章搜索接口"""
    def get(self, request):
        # 获取前端参数
        logger.info(f"收到搜索请求 - 路径: {request.path}, 参数: {request.query_params}")
        keyword = request.query_params.get('keyword', '')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        print(f"Received keyword: {keyword}, page: {page}, page_size: {page_size}")
        # 计算分页偏移量
        start = (page - 1) * page_size
        end = start + page_size
        
        # 搜索逻辑：标题/内容/标签包含关键词
        if keyword:
            queryset = Article.objects.filter(
                title__icontains=keyword  # 标题模糊匹配
            ) | Article.objects.filter(
                content__icontains=keyword  # 内容模糊匹配
            ) | Article.objects.filter(
                tags__icontains=keyword  # 标签模糊匹配
            )
        else:
            queryset = Article.objects.all()
        
        # 按创建时间倒序
        queryset = queryset.order_by('-created_at')
        
        # 分页处理
        total = queryset.count()
        results = queryset[start:end]
        
        # 序列化返回
        serializer = ArticleSerializer2(results, many=True)
        return Response({
            'results': serializer.data,
            'count': total,
            'next': page * page_size < total  # 是否有下一页
        })

class ReportViewSet(viewsets.ModelViewSet):
    """举报视图集"""
    queryset = Report.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReportCreateSerializer
        return ReportSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        """创建举报"""
        try:
            # 检查是否举报自己
            reported_user_id = request.data.get('reported_user')
            if int(reported_user_id) == request.user.id:
                return Response(
                    {'error': '不能举报自己'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 检查是否已经举报过该用户
            existing_report = Report.objects.filter(
                reporter=request.user,
                reported_user_id=reported_user_id,
                status='pending'
            ).first()
            
            if existing_report:
                return Response(
                    {'error': '您已经举报过该用户，请等待管理员处理'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            return Response(
                {'message': '举报提交成功，管理员会尽快处理'},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f'创建举报失败: {e}')
            return Response(
                {'error': '举报提交失败，请重试'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def my_reports(self, request):
        """获取当前用户的举报记录"""
        reports = Report.objects.filter(reporter=request.user)
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """管理员通过举报"""
        if not request.user.is_staff:
            return Response(
                {'error': '只有管理员可以处理举报'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        report = self.get_object()
        report.status = 'approved'
        report.admin_feedback = request.data.get('admin_feedback', '')
        report.save()
        
        # 通知举报人
        create_notification(
            recipient=report.reporter,
            notification_type='report_approved',
            title='举报处理结果',
            message=f'您对{report.reported_user.nickname or report.reported_user.username}的举报已通过处理。{report.admin_feedback}',
            related_object_id=report.id,
            related_object_type='report'
        )
        
        # 通知被举报人
        create_notification(
            recipient=report.reported_user,
            notification_type='user_reported',
            title='账号被举报',
            message=f'您的账号因"{report.reason}"被举报，已通过处理。{report.admin_feedback}',
            related_object_id=report.id,
            related_object_type='report'
        )
        
        return Response({'message': '举报已通过处理'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """管理员拒绝举报"""
        if not request.user.is_staff:
            return Response(
                {'error': '只有管理员可以处理举报'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        report = self.get_object()
        report.status = 'rejected'
        report.admin_feedback = request.data.get('admin_feedback', '')
        report.save()
        
        # 通知举报人
        create_notification(
            recipient=report.reporter,
            notification_type='report_rejected',
            title='举报处理结果',
            message=f'您对{report.reported_user.nickname or report.reported_user.username}的举报已被拒绝。{report.admin_feedback}',
            related_object_id=report.id,
            related_object_type='report'
        )
        
        return Response({'message': '举报已拒绝处理'})