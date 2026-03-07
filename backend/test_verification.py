"""
模拟用户提交认证申请，创建管理员通知
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings')
django.setup()

from django.contrib.auth import get_user_model
from user_info.models import VerificationApplication
from notification.utils import create_notification

User = get_user_model()

# 获取普通用户和管理员
try:
    user = User.objects.get(username='userlzp')
    print(f"找到用户: {user.username} (ID: {user.id})")
except User.DoesNotExist:
    print("未找到用户 userlzp")
    exit(1)

try:
    admin = User.objects.get(username='admin')
    print(f"找到管理员: {admin.username} (ID: {admin.id})")
except User.DoesNotExist:
    print("未找到管理员 admin")
    exit(1)

# 创建认证申请
application = VerificationApplication.objects.create(
    user=user,
    verification_type='student',
    status='pending'
)
print(f"创建认证申请: ID={application.id}")

# 为管理员创建通知
notification = create_notification(
    recipient=admin,
    notification_type='system_general',
    title='新的认证申请',
    message=f'用户 {user.username} 提交了学生认证申请，请及时审核',
    related_object_id=application.id,
    related_object_type='verification'
)
print(f"创建通知: ID={notification.id}")

print("测试完成！")
