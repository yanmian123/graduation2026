from rest_framework import serializers
from .models import ChatRoom, Message
from register.models import User
from enterprise.models import Enterprise

class UserSimpleSerializer(serializers.ModelSerializer):
    """简化用户序列化器"""
    # 添加完整头像URL字段
    avatar = serializers.SerializerMethodField()
    
    def get_avatar(self, obj):
        """生成完整的头像URL"""
        if obj.avatar:
            # 如果是完整URL，直接返回
            if obj.avatar.url.startswith('http'):
                return obj.avatar.url
            # 否则生成完整URL
            return self.context['request'].build_absolute_uri(obj.avatar.url)
        return None
    
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'is_enterprise', 'avatar']

class MessageSerializer(serializers.ModelSerializer):
    """消息序列化器"""
    sender_info = UserSimpleSerializer(source='sender', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'chat_room', 'sender', 'sender_info', 'content', 
            'message_type', 'file', 'file_name', 'file_size',
            'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'sender_info','sender','chat_room']

class EnterpriseSimpleSerializer(serializers.ModelSerializer):
    """简化企业信息序列化器"""
    # 添加完整logo URL字段
    logo = serializers.SerializerMethodField()
    
    def get_logo(self, obj):
        """生成完整的logo URL"""
        if obj.logo:
            # 如果是完整URL，直接返回
            if obj.logo.url.startswith('http'):
                return obj.logo.url
            # 否则生成完整URL
            return self.context['request'].build_absolute_uri(obj.logo.url)
        return None
    
    class Meta:
        model = Enterprise
        fields = ['id', 'name', 'logo', 'industry']  # 企业名称、logo、行业

class ChatRoomSerializer(serializers.ModelSerializer):
    """聊天室序列化器"""
    enterprise_user_info = UserSimpleSerializer(source='enterprise_user', read_only=True)
    job_seeker_user_info = UserSimpleSerializer(source='job_seeker_user', read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    
    enterprise_info = serializers.SerializerMethodField()
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'enterprise_user', 'job_seeker_user', 'recruitment',
            'enterprise_user_info', 'job_seeker_user_info','enterprise_info',
            'last_message', 'unread_count', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_last_message(self, obj):
        """获取最后一条消息"""
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message, context=self.context).data
        return None
    
    def get_unread_count(self, obj):
        """获取未读消息数量"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0
    
    def get_enterprise_info(self, obj):
        """获取企业详细信息"""
        try:
            # 获取企业用户的关联企业信息
            enterprise = obj.enterprise_user.enterprise_profile
            # 传递context参数，确保能生成完整的logo URL
            return EnterpriseSimpleSerializer(enterprise, context=self.context).data
        except Exception as e:
            # 捕获所有可能的异常，包括RelatedObjectDoesNotExist
            print(f"❌ 获取企业信息时发生错误: {e}")
            return None