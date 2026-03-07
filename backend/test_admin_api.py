"""
测试Django Admin的通知API
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings')
django.setup()

from django.contrib.auth import get_user_model
from notification.models import Notification
from notification.serializers import NotificationSerializer

User = get_user_model()

# 获取管理员用户
admin = User.objects.filter(is_staff=True, is_active=True).first()
if admin:
    print(f"✅ 找到管理员: {admin.username} (ID: {admin.id})")
    
    # 获取管理员的通知
    notifications = Notification.objects.filter(recipient=admin).order_by('-created_at')
    
    # 序列化通知数据
    serializer = NotificationSerializer(notifications[:10], many=True)
    
    print(f"\n📋 管理员通知数据（API格式）:")
    for notification in serializer.data:
        status = "未读" if not notification['is_read'] else "已读"
        print(f"- [{status}] {notification['title']}: {notification['message']}")
    
    print(f"\n📊 统计信息:")
    print(f"- 总通知数: {notifications.count()}")
    print(f"- 未读通知数: {notifications.filter(is_read=False).count()}")
else:
    print("❌ 未找到管理员用户")
