from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    # 通知类型常量
    NOTIFICATION_TYPES = (
        # 企业端通知
        ('resume_received', '收到简历'),
        ('jobseeker_message', '收到求职者私信'),
        ('system_notification', '系统通知'),
        # 求职用户端通知
        ('interview_invitation', '面试邀请'),
        ('application_status_update', '招聘流程更新'),
        ('company_chat', '企业发起聊天'),
        ('report_feedback', '举报反馈'),
        ('post_comment', '帖子评论'),
        ('user_followed', '被关注'),
        ('user_message', '用户私信'),
        # 通用通知类型
        ('system_general', '系统通用通知'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='接收者')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, verbose_name='通知类型')
    title = models.CharField(max_length=200, verbose_name='通知标题')
    message = models.TextField(verbose_name='通知内容')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    related_object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name='关联对象ID')
    related_object_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='关联对象类型')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.title}"
