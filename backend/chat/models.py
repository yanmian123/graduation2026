from django.db import models
from register.models import User
from django.conf import settings

class ChatRoom(models.Model):
    """聊天室模型 - 企业用户和求职者用户之间的对话"""
    enterprise_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="enterprise_chatrooms",
        verbose_name="企业用户"
    )
    job_seeker_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="job_seeker_chatrooms", 
        verbose_name="求职者用户"
    )
    recruitment = models.ForeignKey(
        'enterprise.Recruitment', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="关联招聘信息"
    )
    
    # 聊天室状态
    is_active = models.BooleanField(default=True, verbose_name="是否活跃")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="最后活动时间")
    
    class Meta:
        verbose_name = "聊天室"
        verbose_name_plural = "聊天室"
        unique_together = ['enterprise_user', 'job_seeker_user', 'recruitment']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.enterprise_user.username} - {self.job_seeker_user.username}"

class Message(models.Model):
    """消息模型"""
    chat_room = models.ForeignKey(
        ChatRoom, 
        on_delete=models.CASCADE, 
        related_name="messages",
        verbose_name="聊天室"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        verbose_name="发送者"
    )
    content = models.TextField(verbose_name="消息内容")
    message_type = models.CharField(
        max_length=20,
        choices=[
            ('text', '文本'),
            ('file', '文件'),
            ('system', '系统消息'),
        ],
        default='text',
        verbose_name="消息类型"
    )
    file = models.FileField(
        upload_to='chat/files/%Y/%m/%d/', 
        null=True, 
        blank=True,
        verbose_name="文件"
    )
    file_name = models.CharField(max_length=255, blank=True, verbose_name="文件名")
    file_size = models.IntegerField(default=0, verbose_name="文件大小")
    
    # 消息状态
    is_read = models.BooleanField(default=False, verbose_name="是否已读")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="阅读时间")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发送时间")
    
    class Meta:
        verbose_name = "聊天消息"
        verbose_name_plural = "聊天消息"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"