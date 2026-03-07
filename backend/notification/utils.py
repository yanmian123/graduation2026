import logging
from .models import Notification
from .serializers import NotificationSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

def create_notification(recipient, notification_type, title, message, related_object_id=None, related_object_type=None, comment_id=None):
    """
    创建通知的工具函数
    
    Args:
        recipient: 接收通知的用户对象
        notification_type: 通知类型（字符串，必须在Notification.NOTIFICATION_TYPES中定义）
        title: 通知标题
        message: 通知内容
        related_object_id: 关联对象的ID（可选）
        related_object_type: 关联对象的类型（可选，如'resume', 'job', 'user'等）
        comment_id: 评论ID（可选，用于评论通知）
    
    Returns:
        创建的Notification对象
    """
    logger.info("=" * 80)
    logger.info("📝 开始创建通知")
    logger.info(f"👤 接收者: {recipient.username} (ID: {recipient.id})")
    logger.info(f"📋 通知类型: {notification_type}")
    logger.info(f"📌 标题: {title}")
    logger.info(f"💬 消息: {message[:50]}...")
    
    try:
        # 创建通知对象
        notification = Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            related_object_id=related_object_id,
            related_object_type=related_object_type,
            comment_id=comment_id
        )
        
        logger.info(f"✅ 通知已创建: ID={notification.id}")
        logger.info(f"📊 通知详情:")
        logger.info(f"   - 接收者ID: {notification.recipient.id}")
        logger.info(f"   - 类型: {notification.notification_type}")
        logger.info(f"   - 是否已读: {notification.is_read}")
        logger.info(f"   - 创建时间: {notification.created_at}")
        
        # 发送实时通知
        send_notification_via_websocket(notification)
        
        logger.info("=" * 80)
        return notification
        
    except Exception as e:
        logger.error(f"❌ 创建通知失败: {e}", exc_info=True)
        logger.info("=" * 80)
        raise

def send_notification_via_websocket(notification):
    """
    通过WebSocket发送实时通知
    
    Args:
        notification: Notification对象
    """
    logger.info("=" * 80)
    logger.info("📡 开始发送WebSocket通知")
    logger.info(f"📋 通知ID: {notification.id}")
    logger.info(f"👤 接收者ID: {notification.recipient.id}")
    
    try:
        # 序列化通知数据
        serializer = NotificationSerializer(notification)
        notification_data = serializer.data
        
        logger.info(f"📦 通知数据序列化完成:")
        logger.info(f"   - ID: {notification_data.get('id')}")
        logger.info(f"   - 类型: {notification_data.get('notification_type')}")
        logger.info(f"   - 标题: {notification_data.get('title')}")
        logger.info(f"   - 是否已读: {notification_data.get('is_read')}")
        logger.info(f"   - 接收者ID: {notification_data.get('recipient_id')}")
        
        # 获取Channel Layer
        channel_layer = get_channel_layer()
        
        if not channel_layer:
            logger.error("❌ 无法获取Channel Layer")
            logger.info("=" * 80)
            return
        
        logger.info(f"🔌 Channel Layer类型: {type(channel_layer).__name__}")
        
        # 构建用户通知组名称
        group_name = f'user_notifications_{notification.recipient.id}'
        logger.info(f"🎯 目标通知组: {group_name}")
        
        # 发送消息到用户的通知组
        logger.info("📤 正在发送消息到Channel Layer...")
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_notification',
                'notification': notification_data
            }
        )
        
        logger.info(f"✅ WebSocket通知已成功发送到组: {group_name}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ 发送WebSocket通知失败: {e}", exc_info=True)
        logger.info("=" * 80)

def send_notification_via_websocket_sync(notification):
    """
    通过WebSocket发送实时通知（同步版本，用于在同步上下文中调用）
    
    Args:
        notification: Notification对象
    """
    logger.info("=" * 80)
    logger.info("📡 开始发送WebSocket通知（同步版本）")
    logger.info(f"📋 通知ID: {notification.id}")
    logger.info(f"👤 接收者ID: {notification.recipient.id}")
    
    try:
        # 序列化通知数据
        serializer = NotificationSerializer(notification)
        notification_data = serializer.data
        
        logger.info(f"📦 通知数据序列化完成")
        
        # 获取Channel Layer
        channel_layer = get_channel_layer()
        
        if not channel_layer:
            logger.error("❌ 无法获取Channel Layer")
            logger.info("=" * 80)
            return
        
        logger.info(f"🔌 Channel Layer类型: {type(channel_layer).__name__}")
        
        # 构建用户通知组名称
        group_name = f'user_notifications_{notification.recipient.id}'
        logger.info(f"🎯 目标通知组: {group_name}")
        
        # 发送消息到用户的通知组
        logger.info("📤 正在发送消息到Channel Layer...")
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_notification',
                'notification': notification_data
            }
        )
        
        logger.info(f"✅ WebSocket通知已成功发送到组: {group_name}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ 发送WebSocket通知失败: {e}", exc_info=True)
        logger.info("=" * 80)
