from rest_framework import serializers
from .models import Article,Attachment,Comment,Collection,Like

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
    
    class Meta:
        model=Article
        fields = [
            'id', 'title', 'content', 'tags', 'category',
            'view_count', 'like_count', 'comment_count', 'star_count',
            'created_at', 'updated_at', 'user_id', 'username', 'nickname',
            'user_avatar', 'is_collected', 'is_liked', 'attachments'
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
    replies = serializers.SerializerMethodField()
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    
    def get_avatar(self, obj):
        if obj.user.avatar:
            return obj.user.avatar.url
        return None
    
    def get_replies(self, obj):
        # 直接获取回复，不依赖hasattr检查
        return CommentSerializer(obj.replies.all(), many=True).data
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'like_count', 'username', 'nickname', 'avatar', 'parent', 'replies']
        read_only_fields = ['id', 'created_at', 'like_count', 'username', 'nickname', 'avatar', 'parent', 'replies']

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

# 关注状态序列化器
class FollowStatusSerializer(serializers.Serializer):
    is_following = serializers.BooleanField()