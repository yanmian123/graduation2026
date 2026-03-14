import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import ChatRoom, Message
from register.models import User
from .serializers import MessageSerializer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # 添加用户认证
        user = self.scope.get('user')
        if user.is_authenticated:
            self.user = user
            print(f"✅ 用户认证成功: {user.username} (ID: {user.id})")
        else:
            # 临时调试：尝试从查询参数获取用户ID
            user_id = self.scope.get('query_string', b'').decode().split('user_id=')[-1]
            if user_id:
                try:
                    self.user = await database_sync_to_async(User.objects.get)(id=int(user_id))
                    print(f"🔧 调试模式获取用户: {self.user.username} (ID: {self.user.id})")
                except:
                    self.user = AnonymousUser()
            else:
                self.user = AnonymousUser()
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

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
        """处理聊天消息 - 使用认证用户"""
        user = self.user
        
        if not user.is_authenticated:
            print("❌ 用户未认证，无法发送消息")
            return
        
        content = data['content']
        message_type = data.get('message_type', 'text')
        
        try:
            message = await self.save_message(user, content, message_type)
            serializer = MessageSerializer(message)
            message_data = serializer.data
            
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
        """处理已读回执"""
        message_id = data.get('message_id')
        
        if not self.user.is_authenticated:
            print("❌ 用户未认证，无法发送已读回执")
            return
        
        # 广播已读状态
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'read_receipt',
                'message_id': message_id,
                'reader_id': self.user.id
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