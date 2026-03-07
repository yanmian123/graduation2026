"""
完整测试：模拟用户通过API提交认证申请
"""
import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings')
django.setup()

from django.contrib.auth import get_user_model
from user_info.models import VerificationApplication
from user_info.views import VerificationApplicationViewSet
from notification.utils import create_notification

User = get_user_model()

# 获取普通用户和管理员
try:
    user = User.objects.get(username='userlzp')
    print(f"✅ 找到用户: {user.username} (ID: {user.id})")
except User.DoesNotExist:
    print("❌ 未找到用户 userlzp")
    exit(1)

try:
    admin = User.objects.get(username='admin')
    print(f"✅ 找到管理员: {admin.username} (ID: {admin.id})")
except User.DoesNotExist:
    print("❌ 未找到管理员 admin")
    exit(1)

print("\n⏳ 等待3秒，让WebSocket连接建立...")
time.sleep(3)

# 创建认证申请
print("\n📝 创建认证申请...")
application = VerificationApplication.objects.create(
    user=user,
    verification_type='student',
    status='pending'
)
print(f"✅ 认证申请已创建: ID={application.id}")

# 为管理员创建通知
print("\n🔔 为管理员创建通知...")
notification = create_notification(
    recipient=admin,
    notification_type='system_general',
    title='新的认证申请',
    message=f'用户 {user.username} 提交了学生认证申请，请及时审核',
    related_object_id=application.id,
    related_object_type='verification'
)
print(f"✅ 通知已创建: ID={notification.id}")

print("\n🎉 测试完成！")
print(f"📌 请检查管理员页面是否收到通知")
print(f"📌 管理员ID: {admin.id}")
print(f"📌 用户ID: {user.id}")
