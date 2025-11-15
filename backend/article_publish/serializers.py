from rest_framework import serializers
from .models import Article,Attachment,Comment

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
    user_avatar = serializers.ReadOnlyField(source='user.avatar.url')  # 作者头像（如果有）
    class Meta:
        model=Article
        exclude = ['user',]  # 排除user字段，自动关联当前用户
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
    avatar = serializers.ReadOnlyField(source='user.avatar.url')
    identity = serializers.ReadOnlyField(source='user.profile.identity')
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'tags', 
            'view_count', 'like_count', 'comment_count', 
            'created_at', 'username', 'avatar', 'identity'
        ]
        
# 评论序列化器
class CommentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    avatar = serializers.ReadOnlyField(source='user.avatar.url')
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'like_count', 'username', 'avatar']
        read_only_fields = ['id', 'created_at', 'like_count', 'username', 'avatar']

    def create(self, validated_data):
        return Comment.objects.create(
            user=self.context['request'].user,
            **validated_data
        )

# 收藏状态序列化器
class CollectionStatusSerializer(serializers.Serializer):
    is_collected = serializers.BooleanField()
    count = serializers.IntegerField()

# 点赞状态序列化器
class LikeStatusSerializer(serializers.Serializer):
    is_liked = serializers.BooleanField()
    count = serializers.IntegerField()

# 关注状态序列化器
class FollowStatusSerializer(serializers.Serializer):
    is_following = serializers.BooleanField()