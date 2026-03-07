"""
检查管理员的通知数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings')
django.setup()

from django.contrib.auth import get_user_model
from notification.models import Notification

User = get_user_model()

# 获取管理员用户
admin = User.objects.filter(is_staff=True, is_active=True).first()
if admin:
    print(f"✅ 找到管理员: {admin.username} (ID: {admin.id})")
    
    # 获取管理员的所有通知
    notifications = Notification.objects.filter(recipient=admin).order_by('-created_at')
    print(f"\n📋 管理员通知总数: {notifications.count()}")
    
    # 获取未读通知
    unread_notifications = notifications.filter(is_read=False)
    print(f"🔔 未读通知数量: {unread_notifications.count()}")
    
    # 显示最近的通知
    print(f"\n📌 最近的通知:")
    for i, notification in enumerate(notifications[:5], 1):
        status = "未读" if not notification.is_read else "已读"
        print(f"{i}. [{status}] {notification.title} - {notification.created_at}")
else:
    print("❌ 未找到管理员用户")
