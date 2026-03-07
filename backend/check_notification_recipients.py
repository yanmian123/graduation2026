"""
检查最近创建的通知，看看通知是发给谁的
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings')
django.setup()

from django.contrib.auth import get_user_model
from notification.models import Notification
from user_info.models import VerificationApplication

User = get_user_model()

# 获取最近的通知
recent_notifications = Notification.objects.all().order_by('-created_at')[:5]
print(f"📋 最近5条通知:")
for i, notification in enumerate(recent_notifications, 1):
    status = "未读" if not notification.is_read else "已读"
    print(f"{i}. [{status}] 接收者: {notification.recipient.username} (ID: {notification.recipient.id}) - {notification.title}")
    print(f"   消息: {notification.message}")
    print(f"   创建时间: {notification.created_at}")
    
    # 检查关联的认证申请
    if notification.related_object_type == 'verification' and notification.related_object_id:
        try:
            application = VerificationApplication.objects.get(id=notification.related_object_id)
            print(f"   关联申请: 用户 {application.user.username} (ID: {application.user.id}) 提交的申请")
        except VerificationApplication.DoesNotExist:
            print(f"   关联申请: 不存在")
    print()
