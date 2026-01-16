from .models import Notification
from .serializers import NotificationSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def create_notification(recipient, notification_type, title, message, related_object_id=None, related_object_type=None):
    """
    创建通知的工具函数
    
    Args:
        recipient: 接收通知的用户对象
        notification_type: 通知类型（字符串，必须在Notification.NOTIFICATION_TYPES中定义）
        title: 通知标题
        message: 通知内容
        related_object_id: 关联对象的ID（可选）
        related_object_type: 关联对象的类型（可选，如'resume', 'job', 'user'等）
    
    Returns:
        创建的Notification对象
    """
    notification = Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        related_object_id=related_object_id,
        related_object_type=related_object_type
    )
    
    # 发送实时通知
    send_notification_via_websocket(notification)
    
    return notification

def send_notification_via_websocket(notification):
    """
    通过WebSocket发送实时通知
    
    Args:
        notification: Notification对象
    """
    # 序列化通知数据
    serializer = NotificationSerializer(notification)
    notification_data = serializer.data
    
    # 获取Channel Layer
    channel_layer = get_channel_layer()
    
    # 构建用户通知组名称
    group_name = f'user_notifications_{notification.recipient.id}'
    
    # 发送消息到用户的通知组
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_notification',
            'notification': notification_data  # 改为与前端期望一致的字段名
        }
    )