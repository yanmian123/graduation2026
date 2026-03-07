"""
测试通知发送脚本 - 发送给当前登录用户
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings')
django.setup()

from register.models import User
from notification.utils import create_notification

# 发送给用户ID 28（当前登录的用户）
try:
    user = User.objects.get(id=28)
    print(f"👤 找到测试用户: {user.username} (ID: {user.id})")
    
    # 创建一个测试通知
    print("📝 开始创建测试通知...")
    notification = create_notification(
        recipient=user,
        notification_type='post_comment',
        title='测试通知',
        message='这是一条测试通知，用于验证WebSocket推送是否正常工作',
        related_object_id=1,
        related_object_type='article'
    )
    
    print(f"✅ 测试通知创建成功: ID={notification.id}")
    print(f"📊 通知详情:")
    print(f"   - 接收者: {notification.recipient.username}")
    print(f"   - 类型: {notification.notification_type}")
    print(f"   - 标题: {notification.title}")
    print(f"   - 消息: {notification.message}")
    print(f"   - 是否已读: {notification.is_read}")
    print(f"   - 创建时间: {notification.created_at}")
    
    print("\n🔍 如果WebSocket连接正常，你应该在前端控制台看到通知消息")
    print("🔍 请检查前端控制台是否有：")
    print("   📨 [NotificationWebSocket] 收到WebSocket消息")
    print("   🔔 [NotificationWebSocket] 收到新通知")
    print("   📢 [NotificationStore] 添加新通知到store")
    
except User.DoesNotExist:
    print("❌ 没有找到ID为28的用户")
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
