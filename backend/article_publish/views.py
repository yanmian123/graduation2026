
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import action
from .models import Article, Attachment, Comment, Like, Collection, Follow
from register.models import User
from .serializers import ArticleSerializer, AttachmentSerializer, ArticleSerializer2,CommentSerializer,LikeStatusSerializer, CollectionStatusSerializer,FollowStatusSerializer
from django.db import models
import logging
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
    # permission_classes = [permissions.IsAuthenticated, IsArticleOwner]  # 登录+所有者权限

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
        
        # 如果请求参数 user_only=true，只返回当前用户的文章
        if user_only == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        
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
            return Response(CollectionStatusSerializer({
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
            return Response(CollectionStatusSerializer({
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
    
    # 获取当前用户的收藏
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def collections(self, request):
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
                    related_object_type='article'
                )
            # 如果是顶级评论，通知文章作者
            elif not parent_comment and request.user != article.user:
                create_notification(
                    recipient=article.user,
                    notification_type='post_comment',
                    title='新评论通知',
                    message=f"{request.user.nickname or request.user.username}评论了你的文章: {comment.content[:20]}...",
                    related_object_id=article.id,
                    related_object_type='article'
                )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CommentViewSet(viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        '''获取当前用户的评论'''
        queryset = Comment.objects.all()
        user_only = self.request.query_params.get('user_only')
        
        # 如果请求参数 user_only=true，只返回当前用户的评论
        if user_only == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset.order_by('-created_at')

    # 评论点赞/取消点赞
    @action(detail=True, methods=['post', 'delete'],permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        comment = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, comment=comment)
        
        if request.method == 'POST' and created:
            comment.like_count += 1
            comment.save()
            return Response({'is_liked': True, 'count': comment.like_count})
            
        if request.method == 'DELETE' and not created:
            like.delete()
            comment.like_count -= 1
            comment.save()
            return Response({'is_liked': False, 'count': comment.like_count})
            
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

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

class FileUploadView(APIView):
    '''附件上传接口'''
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, format=None):
        file=request.FILES.get('file')
        article_id=request.data.get('article_id')
        
        if not file or not article_id:
            return Response({
                "code": 400,
                "message": "缺少文件或文章ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
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