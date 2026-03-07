"""
检查普通用户的通知数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings')
django.setup()

from django.contrib.auth import get_user_model
from notification.models import Notification

User = get_user_model()

# 获取普通用户
try:
    user = User.objects.get(username='userlzp')
    print(f"✅ 找到用户: {user.username} (ID: {user.id})")
    
    # 获取用户的所有通知
    notifications = Notification.objects.filter(recipient=user).order_by('-created_at')
    print(f"\n📋 用户通知总数: {notifications.count()}")
    
    # 获取未读通知
    unread_notifications = notifications.filter(is_read=False)
    print(f"🔔 未读通知数量: {unread_notifications.count()}")
    
    # 显示最近的通知
    print(f"\n📌 最近的通知:")
    for i, notification in enumerate(notifications[:5], 1):
        status = "未读" if not notification.is_read else "已读"
        print(f"{i}. [{status}] {notification.title} - {notification.message} ({notification.created_at})")
except User.DoesNotExist:
    print("❌ 未找到用户 userlzp")
