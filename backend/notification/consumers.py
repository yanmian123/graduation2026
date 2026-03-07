import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from channels.auth import get_user
from .models import Notification
from .serializers import NotificationSerializer

logger = logging.getLogger(__name__)

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("=" * 80)
        logger.info("🔌 WebSocket连接请求开始")
        logger.info(f"📋 连接信息: scope={self.scope}")
        logger.info(f"🍪 Cookies: {self.scope.get('cookies', {})}")
        logger.info(f"📝 Session: {self.scope.get('session')}")
        
        try:
            self.user = None
            self.notification_group_name = None
            
            # 首先尝试从session获取用户（Django Admin使用session）
            self.user = await get_user(self.scope)
            logger.info(f"👤 从session获取用户: {self.user}")
            
            # 如果session中有用户且已认证，直接使用session用户，忽略token
            if self.user and self.user.is_authenticated:
                logger.info(f"✅ 使用Session认证的用户: {self.user.username} (ID: {self.user.id})")
            # 如果session中没有用户，尝试从URL参数获取token（Vue前端使用token）
            else:
                logger.info("🔑 Session认证失败，尝试Token认证")
                query_params = self.scope['query_string'].decode('utf-8').split('&')
                token_param = next((p for p in query_params if p.startswith('token=')), None)
                
                if token_param:
                    token = token_param.split('=')[1]
                    logger.info(f"🔑 找到token: {token[:20]}...")
                    try:
                        # 验证token
                        access_token = AccessToken(token)
                        user_id = access_token['user_id']
                        # 获取用户
                        self.user = await database_sync_to_async(User.objects.get)(id=user_id)
                        logger.info(f"✅ 从token获取用户: {self.user.username} (ID: {self.user.id})")
                    except Exception as e:
                        logger.error(f"❌ Token验证失败: {e}", exc_info=True)
                        await self.close(code=4001, reason='Authentication failed')
                        return
                else:
                    logger.error("❌ Session和Token认证都失败，拒绝WebSocket连接")
                    await self.close(code=4001, reason='No authentication provided')
                    return
            
            # 为当前用户创建通知组
            self.notification_group_name = f'user_notifications_{self.user.id}'
            logger.info(f"📢 通知组名称: {self.notification_group_name}")
            
            # 将用户加入通知组
            await self.channel_layer.group_add(
                self.notification_group_name,
                self.channel_name
            )
            logger.info(f"✅ 用户已加入通知组: {self.notification_group_name}")
            
            # 接受连接
            await self.accept()
            logger.info(f"🎉 WebSocket连接已接受: user={self.user.username} (ID: {self.user.id})")
            logger.info("=" * 80)
            
            # 发送连接成功消息给客户端
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'WebSocket连接成功',
                'user_id': self.user.id
            }))
            
        except Exception as e:
            logger.error(f"❌ WebSocket连接过程中发生错误: {e}", exc_info=True)
            await self.close(code=4000, reason='Connection error')
    
    async def disconnect(self, close_code):
        logger.info("=" * 80)
        logger.info(f"🔌 WebSocket断开连接: code={close_code}")
        
        # 将用户从通知组移除，如果通知组已创建
        if hasattr(self, 'notification_group_name') and self.notification_group_name:
            try:
                await self.channel_layer.group_discard(
                    self.notification_group_name,
                    self.channel_name
                )
                logger.info(f"✅ 用户已从通知组移除: {self.notification_group_name}")
            except Exception as e:
                logger.error(f"❌ 从通知组移除用户时出错: {e}", exc_info=True)
        
        logger.info("=" * 80)
    
    async def receive(self, text_data):
        logger.info(f"📨 收到WebSocket消息: {text_data}")
        
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'ping':
                # 心跳检测
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': text_data_json.get('timestamp')
                }))
                logger.info("💓 心跳响应已发送")
            
            elif message_type == 'mark_as_read':
                # 标记通知为已读
                notification_id = text_data_json.get('notification_id')
                if notification_id:
                    await self.mark_notification_as_read(notification_id)
            
            else:
                logger.warning(f"⚠️ 未知的消息类型: {message_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON解析失败: {e}")
        except Exception as e:
            logger.error(f"❌ 处理WebSocket消息时出错: {e}", exc_info=True)
    
    async def send_notification(self, event):
        logger.info("=" * 80)
        logger.info(f"📨 收到WebSocket事件: {event}")
        
        try:
            # 从事件中获取通知数据
            notification_data = event.get('notification')
            if not notification_data:
                logger.error("❌ 事件中没有通知数据")
                return
            
            logger.info(f"📦 准备发送通知给客户端: {notification_data}")
            logger.info(f"👤 当前WebSocket用户: {self.user.username} (ID: {self.user.id})")
            logger.info(f"🎯 通知接收者ID: {notification_data.get('recipient_id')}")
            
            # 检查通知是否是发给当前用户的
            notification_recipient_id = notification_data.get('recipient_id')
            if notification_recipient_id and notification_recipient_id != self.user.id:
                logger.info(f"⏭️ 通知不是发给当前用户的，跳过发送")
                logger.info(f"   通知接收者ID: {notification_recipient_id}")
                logger.info(f"   当前用户ID: {self.user.id}")
                return
            
            logger.info(f"✅ 通知匹配，准备发送给客户端")
            
            # 发送通知给客户端
            await self.send(text_data=json.dumps({
                'type': 'notification',
                'notification': notification_data
            }))
            
            logger.info(f"✅ 通知已发送给客户端: {self.user.username}")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ 发送通知时出错: {e}", exc_info=True)
    
    async def send_error(self, event):
        logger.error(f"🚨 收到错误事件: {event}")
        error_message = event.get('message', 'Unknown error')
        
        try:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': error_message
            }))
        except Exception as e:
            logger.error(f"❌ 发送错误消息时出错: {e}", exc_info=True)
    
    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, recipient=self.user)
            notification.is_read = True
            notification.save()
            logger.info(f"✅ 通知已标记为已读: ID={notification_id}")
            return True
        except Notification.DoesNotExist:
            logger.warning(f"⚠️ 通知不存在或无权限: ID={notification_id}")
            return False
        except Exception as e:
            logger.error(f"❌ 标记通知为已读时出错: {e}", exc_info=True)
            return False
