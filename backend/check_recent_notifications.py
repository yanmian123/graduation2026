"""
检查最近创建的通知
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings')
django.setup()

from django.contrib.auth import get_user_model
from notification.models import Notification

User = get_user_model()

# 获取所有用户
users = User.objects.all()
print(f"📊 总用户数: {users.count()}")

# 获取最近的通知
recent_notifications = Notification.objects.all().order_by('-created_at')[:20]
print(f"\n📋 最近20条通知:")
for i, notification in enumerate(recent_notifications, 1):
    status = "未读" if not notification.is_read else "已读"
    print(f"{i}. [{status}] 接收者: {notification.recipient.username} (ID: {notification.recipient.id}) - {notification.title} - {notification.created_at}")
