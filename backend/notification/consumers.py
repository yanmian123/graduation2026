import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from channels.auth import get_user
from .models import Notification
from .serializers import NotificationSerializer

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f"WebSocket连接请求: scope={self.scope}")
        print(f"Cookies: {self.scope.get('cookies', {})}")
        print(f"Session: {self.scope.get('session')}")
        
        # 首先尝试从session获取用户（Django Admin使用session）
        self.user = await get_user(self.scope)
        print(f"从session获取用户: {self.user}")
        
        # 如果session中有用户且已认证，直接使用session用户，忽略token
        if self.user and self.user.is_authenticated:
            print(f"✅ 使用Session认证的用户: {self.user.username}")
        # 如果session中没有用户，尝试从URL参数获取token（Vue前端使用token）
        else:
            print("Session认证失败，尝试Token认证")
            query_params = self.scope['query_string'].decode('utf-8').split('&')
            token_param = next((p for p in query_params if p.startswith('token=')), None)
            
            if token_param:
                token = token_param.split('=')[1]
                try:
                    # 验证token
                    access_token = AccessToken(token)
                    user_id = access_token['user_id']
                    # 获取用户
                    self.user = await database_sync_to_async(User.objects.get)(id=user_id)
                    print(f"✅ 从token获取用户: {self.user.username}")
                except Exception as e:
                    print(f"❌ Token验证失败: {e}")
                    await self.close(code=4001)  # 认证失败
                    return
            else:
                print("❌ Session和Token认证都失败，拒绝WebSocket连接")
                await self.close(code=4001)  # 认证失败
                return
        
        # 为当前用户创建通知组
        self.notification_group_name = f'user_notifications_{self.user.id}'
        print(f"📢 通知组名称: {self.notification_group_name}")
        
        # 将用户加入通知组
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        print(f"✅ 用户已加入通知组: {self.notification_group_name}")
        
        await self.accept()
        print(f"🎉 WebSocket连接已接受: user={self.user.username}")
    
    async def disconnect(self, close_code):
        # 将用户从通知组移除，如果通知组已创建
        if hasattr(self, 'notification_group_name'):
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )
    
    # 接收来自WebSocket的消息
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        # 可以处理客户端发送的消息，比如标记通知为已读
        if text_data_json.get('type') == 'mark_as_read':
            notification_id = text_data_json.get('notification_id')
            await self.mark_notification_as_read(notification_id)
    
    # 发送通知给用户
    async def send_notification(self, event):
        print(f"收到WebSocket事件: {event}")
        # 从事件中获取通知数据
        notification_data = event['notification']
        print(f"准备发送通知给客户端: {notification_data}")
        print(f"当前WebSocket用户: {self.user.username} (ID: {self.user.id})")
        print(f"通知接收者ID: {notification_data.get('recipient_id')}")
        
        # 检查通知是否是发给当前用户的
        notification_recipient_id = notification_data.get('recipient_id')
        if notification_recipient_id and notification_recipient_id != self.user.id:
            print(f"❌ 通知不是发给当前用户的，跳过发送")
            return
        
        # 发送通知给客户端
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': notification_data
        }))
        print(f"✅ 通知已发送给客户端")
    
    # 将通知标记为已读（异步数据库操作）
    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, recipient=self.user)
            notification.is_read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False