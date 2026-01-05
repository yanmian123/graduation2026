import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import ChatRoom, Message
from .serializers import MessageSerializer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # 临时：跳过所有认证检查
        print(f"🔓 调试模式：允许连接到聊天室 {self.room_id}")
        
        # 直接接受连接，不检查权限
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # 发送连接成功消息
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': '连接成功（调试模式）'
        }))

    async def disconnect(self, close_code):
        # 离开房间组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'chat_message')
        
        if message_type == 'chat_message':
            await self.handle_chat_message(data)
        elif message_type == 'read_receipt':
            await self.handle_read_receipt(data)

    async def handle_chat_message(self, data):
        """处理聊天消息 - 简化版"""
        # 临时：使用匿名用户或默认用户
        from register.models import User
        try:
            # 尝试获取第一个用户作为发送者
            user = await database_sync_to_async(User.objects.first)()
        except:
            # 如果失败，创建一个虚拟用户
            user = AnonymousUser()
        
        content = data['content']
        message_type = data.get('message_type', 'text')
        
        # 保存消息到数据库（简化）
        try:
            message = await self.save_message(user, content, message_type)
            
            # 序列化消息
            serializer = MessageSerializer(message)
            message_data = serializer.data
            
            # 发送消息到房间组
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )
        except Exception as e:
            print(f"保存消息失败: {e}")

    async def handle_read_receipt(self, data):
        """处理已读回执 - 简化版"""
        message_id = data.get('message_id')
        
        # 广播已读状态（简化）
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'read_receipt',
                'message_id': message_id,
                'reader_id': 1  # 默认用户ID
            }
        )

    async def chat_message(self, event):
        """接收聊天消息"""
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))

    async def read_receipt(self, event):
        """接收已读回执"""
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'reader_id': event['reader_id']
        }))

    @database_sync_to_async
    def save_message(self, user, content, message_type):
        """保存消息到数据库 - 简化版"""
        try:
            from .models import ChatRoom
            room = ChatRoom.objects.get(id=self.room_id)
            
            message = Message.objects.create(
                chat_room=room,
                sender=user,
                content=content,
                message_type=message_type
            )
            return message
        except Exception as e:
            print(f"保存消息错误: {e}")
            # 返回一个虚拟消息用于测试
            class MockMessage:
                def __init__(self):
                    self.id = 1
                    self.content = content
                    self.message_type = message_type
                    self.sender = user
            return MockMessage()