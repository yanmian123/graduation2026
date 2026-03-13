from rest_framework import serializers
from .models import Article,Attachment,Comment,Collection,Like,Report

class AttachmentSerializer(serializers.ModelSerializer):
    '''附件序列化器'''
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'file_name','created_at']
        read_only_fields = ['id', 'created_at']
        
        
class ArticleSerializer(serializers.ModelSerializer):
    '''文章序列化器'''
    attachments=AttachmentSerializer(many=True, read_only=True)  # 嵌套序列化附件列表
        # 新增：添加作者相关字段（从关联的 user 模型中提取）
    user_id = serializers.ReadOnlyField(source='user.id')  # 作者 ID（关键）
    username = serializers.ReadOnlyField(source='user.username')  # 作者用户名
    nickname = serializers.SerializerMethodField()  # 作者昵称
    user_avatar = serializers.SerializerMethodField()  # 自定义作者头像字段处理
    is_collected = serializers.SerializerMethodField()  # 文章收藏状态
    is_liked = serializers.SerializerMethodField()  # 文章点赞状态
    is_followed = serializers.SerializerMethodField()  # 是否关注作者
    author_article_count = serializers.SerializerMethodField()  # 作者文章数
    author_total_likes = serializers.SerializerMethodField()  # 作者总点赞数
    author_follower_count = serializers.SerializerMethodField()  # 作者粉丝数
    
    def get_user_avatar(self, obj):
        if obj.user.avatar:
            return obj.user.avatar.url
        return None  # 没有头像时返回None
    
    def get_nickname(self, obj):
        return obj.user.nickname or ""
    
    def get_is_collected(self, obj):
        # 检查当前用户是否收藏了该文章
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Collection.objects.filter(user=request.user, article=obj).exists()
        return False  # 未登录用户默认为未收藏
    
    def get_is_liked(self, obj):
        # 检查当前用户是否点赞了该文章
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, article=obj).exists()
        return False  # 未登录用户默认为未点赞
    
    def get_is_followed(self, obj):
        # 检查当前用户是否关注了文章作者
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from .models import Follow
            return Follow.objects.filter(follower=request.user, followed=obj.user).exists()
        return False  # 未登录用户默认为未关注
    
    def get_author_article_count(self, obj):
        # 获取作者的文章数
        return obj.user.articles.count() if hasattr(obj.user, 'articles') else 0
    
    def get_author_total_likes(self, obj):
        # 获取作者的总点赞数
        total_likes = 0
        for article in obj.user.articles.all() if hasattr(obj.user, 'articles') else []:
            total_likes += article.like_count or 0
        return total_likes
    
    def get_author_follower_count(self, obj):
        # 获取作者的粉丝数
        from .models import Follow
        return Follow.objects.filter(followed=obj.user).count()
    
    class Meta:
        model=Article
        fields = [
            'id', 'title', 'content', 'tags', 'category',
            'view_count', 'like_count', 'comment_count', 'star_count',
            'created_at', 'updated_at', 'user_id', 'username', 'nickname',
            'user_avatar', 'is_collected', 'is_liked', 'is_followed', 'attachments',
            'author_article_count', 'author_total_likes', 'author_follower_count', 'is_draft'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_tags(self,value):
        '''处理标签，去重，去空格'''
        if value:
            tags_list=[tag.strip() for tag in value.split(',') if tag.strip()]
            return ','.join(list(set(tags_list)))
        return value
    
    def create(self, validated_data):
        '''创建文章时，自动关联当前用户'''
        user=self.context['request'].user  # 从上下文获取当前用户
        return Article.objects.create(user=user, **validated_data)


class ArticleSerializer2(serializers.ModelSerializer):
    # 嵌套用户信息
    username = serializers.ReadOnlyField(source='user.username')
    nickname = serializers.ReadOnlyField(source='user.nickname')
    avatar = serializers.SerializerMethodField()
    identity = serializers.ReadOnlyField(source='user.profile.identity')
    
    def get_avatar(self, obj):
        if obj.user.avatar:
            return obj.user.avatar.url
        return None
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'tags', 
            'view_count', 'like_count', 'comment_count', 
            'created_at', 'username', 'nickname', 'avatar', 'identity'
        ]
        
# 评论序列化器
class CommentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    nickname = serializers.ReadOnlyField(source='user.nickname')
    avatar = serializers.SerializerMethodField()
    user_id = serializers.ReadOnlyField(source='user.id')
    article_id = serializers.ReadOnlyField(source='article.id')
    replies = serializers.SerializerMethodField()
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    parent_username = serializers.SerializerMethodField()
    parent_nickname = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    def get_avatar(self, obj):
        if obj.user.avatar:
            return obj.user.avatar.url
        return None
    
    def get_replies(self, obj):
        return CommentSerializer(obj.replies.all(), many=True).data
    
    def get_parent_username(self, obj):
        if obj.parent:
            return obj.parent.user.username
        return None
    
    def get_parent_nickname(self, obj):
        if obj.parent:
            return obj.parent.user.nickname or obj.parent.user.username
        return None
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from .models import Like
            return Like.objects.filter(user=request.user, comment=obj).exists()
        return False
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'like_count', 'username', 'nickname', 'avatar', 'parent', 'replies', 'user_id', 'parent_username', 'parent_nickname', 'article_id', 'is_liked']
        read_only_fields = ['id', 'created_at', 'like_count', 'username', 'nickname', 'avatar', 'parent', 'replies', 'user_id', 'parent_username', 'parent_nickname', 'article_id', 'is_liked']

    def create(self, validated_data):
        return Comment.objects.create(
            user=self.context['request'].user,
            **validated_data
        )

# 收藏状态序列化器
class CollectionStatusSerializer(serializers.ModelSerializer):
    article_title = serializers.ReadOnlyField(source='article.title')
    article_content = serializers.ReadOnlyField(source='article.content')
    article_id = serializers.ReadOnlyField(source='article.id')
    
    class Meta:
        model = Collection
        fields = ['id', 'article_id', 'article_title', 'article_content', 'created_at']

# 点赞状态序列化器
class LikeStatusSerializer(serializers.Serializer):
    is_liked = serializers.BooleanField()
    count = serializers.IntegerField()

# 收藏状态序列化器
class CollectStatusSerializer(serializers.Serializer):
    is_collected = serializers.BooleanField()
    count = serializers.IntegerField()

# 关注状态序列化器
class FollowStatusSerializer(serializers.Serializer):
    is_following = serializers.BooleanField()

# 举报序列化器
class ReportSerializer(serializers.ModelSerializer):
    reporter_username = serializers.ReadOnlyField(source='reporter.username')
    reporter_nickname = serializers.SerializerMethodField()
    reported_user_username = serializers.ReadOnlyField(source='reported_user.username')
    reported_user_nickname = serializers.SerializerMethodField()
    
    def get_reporter_nickname(self, obj):
        return obj.reporter.nickname or obj.reporter.username
    
    def get_reported_user_nickname(self, obj):
        return obj.reported_user.nickname or obj.reported_user.username
    
    class Meta:
        model = Report
        fields = ['id', 'reporter', 'reporter_username', 'reporter_nickname', 
                  'reported_user', 'reported_user_username', 'reported_user_nickname',
                  'report_type', 'reason', 'description', 'status', 'admin_feedback', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'reporter', 'created_at', 'updated_at']

# 举报创建序列化器
class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['reported_user', 'report_type', 'reason', 'description']
        
    def create(self, validated_data):
        return Report.objects.create(
            reporter=self.context['request'].user,
            **validated_data
        )