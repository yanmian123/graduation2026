from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from enterprise.models import Recruitment
from register.models import User
from rest_framework.decorators import api_view, permission_classes
from django.conf import settings
import os
from notification.utils import create_notification

class IsChatParticipant(permissions.BasePermission):
    """验证用户是否是聊天室的参与者"""
    def has_object_permission(self, request, view, obj):
        # 如果是ChatRoom对象
        if isinstance(obj, ChatRoom):
            return obj.enterprise_user == request.user or obj.job_seeker_user == request.user
        # 如果是Message对象，通过chat_room属性检查
        elif isinstance(obj, Message):
            return obj.chat_room.enterprise_user == request.user or obj.chat_room.job_seeker_user == request.user
        return False

class ChatRoomViewSet(viewsets.ModelViewSet):
    """聊天室视图集"""
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """用户只能看到自己参与的聊天室"""
        user = self.request.user
        return ChatRoom.objects.filter(
            Q(enterprise_user=user) | Q(job_seeker_user=user)
        ).select_related('enterprise_user', 'job_seeker_user').prefetch_related('messages')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=True, methods=['post'])
    def mark_all_as_read(self, request, pk=None):
        """标记聊天室中所有未读消息为已读"""
        chat_room = self.get_object()
        
        # 只标记接收到的消息为已读（不包括自己发送的）
        unread_messages = chat_room.messages.filter(
            is_read=False
        ).exclude(sender=request.user)
        
        count = unread_messages.update(is_read=True, read_at=timezone.now())
        
        return Response({
            'success': True,
            'marked_count': count
        })

# 在ChatRoomViewSet中修改start_chat方法
    @action(detail=False, methods=['post'])
    def start_chat(self, request):
        """
        开始聊天 - 支持普通用户之间的聊天
        """
        enterprise_user_id = request.data.get('enterprise_user_id')
        job_seeker_user_id = request.data.get('job_seeker_user_id')
        
        print(f"🔍🔍 开始聊天请求参数: enterprise={enterprise_user_id}, job_seeker={job_seeker_user_id}")
        
        # 1. 验证必需参数
        if not enterprise_user_id or not job_seeker_user_id:
            return Response(
                {"error": "缺少用户ID参数"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. 验证用户是否存在
        try:
            enterprise_user = User.objects.get(id=enterprise_user_id)
            job_seeker_user = User.objects.get(id=job_seeker_user_id)
            print(f"✅ 用户验证成功: enterprise={enterprise_user.username}, job_seeker={job_seeker_user.username}")
        except User.DoesNotExist:
            return Response(
                {"error": "用户不存在"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 3. 查找或创建聊天室
        created = False
        
        try:
            # 查找已存在的聊天室（两个用户之间的聊天室）
            chat_rooms = ChatRoom.objects.filter(
                enterprise_user=enterprise_user,
                job_seeker_user=job_seeker_user
            ).order_by('-created_at')
            
            if not chat_rooms.exists():
                # 如果找不到，尝试反向查找
                chat_rooms = ChatRoom.objects.filter(
                    enterprise_user=job_seeker_user,
                    job_seeker_user=enterprise_user
                ).order_by('-created_at')
            
            if chat_rooms.exists():
                # 使用已存在的聊天室
                chat_room = chat_rooms.first()
                created = False
                print("✅ 找到已存在的聊天室")
            else:
                # 创建新的聊天室
                chat_room = ChatRoom.objects.create(
                    enterprise_user=enterprise_user,
                    job_seeker_user=job_seeker_user,
                    recruitment=None
                )
                created = True
                print("✅ 创建新的聊天室")
                
        except Exception as e:
            print(f"❌❌ 创建聊天室时发生错误: {e}")
            return Response(
                {"error": "创建聊天室失败"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 4. 序列化并返回结果
        serializer = self.get_serializer(chat_room)
        
        print(f"🎯🎯 聊天室处理完成: 创建={created}, 聊天室ID={chat_room.id}")
        
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
class MessageViewSet(viewsets.ModelViewSet):
    """消息视图集"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsChatParticipant]
    
    def get_queryset(self):
        """获取聊天室的消息"""
        room_id = self.kwargs.get('room_id')
        return Message.objects.filter(chat_room_id=room_id).select_related('sender')
    
    def get_serializer_context(self):
        """添加request到serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        room_id = self.kwargs.get('room_id')
        chat_room = ChatRoom.objects.get(id=room_id)
        
        # 保存消息
        message = serializer.save(chat_room=chat_room, sender=self.request.user)
        
        # 手动更新聊天室的 updated_at，确保聊天列表排序正确
        chat_room.save()
        
        # 确定接收者和通知类型
        sender = self.request.user
        recipient = None
        notification_type = None
        
        # 根据发送者确定接收者
        if chat_room.enterprise_user == sender:
            # 发送者是enterprise_user，接收者是job_seeker_user
            recipient = chat_room.job_seeker_user
            notification_type = 'company_chat' if sender.is_enterprise else 'jobseeker_message'
        else:
            # 发送者是job_seeker_user，接收者是enterprise_user
            recipient = chat_room.enterprise_user
            notification_type = 'company_chat' if recipient.is_enterprise else 'jobseeker_message'
        
        # 创建通知
        if recipient:
            title = "新消息"
            message_content = message.content if len(message.content) <= 50 else f"{message.content[:50]}..."
            create_notification(
                recipient=recipient,
                notification_type=notification_type,
                title=title,
                message=message_content,
                related_object_id=chat_room.id,
                related_object_type='chat_room'
            )
        
        # 通过WebSocket广播消息
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{room_id}'
        
        # 序列化消息并传递context
        serializer = MessageSerializer(message, context={'request': self.request})
        message_data = serializer.data
        
        # 广播消息
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'chat_message',
                'message': message_data
            }
        )
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, room_id=None, pk=None):
        """标记消息为已读"""
        message = self.get_object()
        if message.sender != request.user:  # 只有接收者才能标记已读
            message.is_read = True
            message.save()
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)
    
    
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_file(request, room_id):
    """处理文件上传"""
    try:
        # 验证聊天室存在且用户有权限
        chat_room = ChatRoom.objects.get(id=room_id)
        if chat_room.enterprise_user != request.user and chat_room.job_seeker_user != request.user:
            return Response({"error": "无权限访问此聊天室"}, status=status.HTTP_403_FORBIDDEN)
        
        # 检查文件是否存在
        if 'file' not in request.FILES:
            return Response({"error": "未找到文件"}, status=status.HTTP_400_BAD_REQUEST)
        
        file_obj = request.FILES['file']
        
        # 打印调试信息
        print(f"📤 上传文件信息:")
        print(f"  - 文件名: {file_obj.name}")
        print(f"  - 文件大小: {file_obj.size}")
        print(f"  - MIME类型: {file_obj.content_type}")
        
        # 判断是否为图片 - 使用MIME类型更可靠
        image_mime_types = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/jpg']
        is_image = file_obj.content_type in image_mime_types
        
        print(f"  - 是否为图片: {is_image}")
        
        # 确定消息类型
        message_type = 'image' if is_image else 'file'
        
        # 创建文件消息
        message = Message.objects.create(
            chat_room=chat_room,
            sender=request.user,
            content=f"{'图片' if is_image else '文件'}: {file_obj.name}",
            message_type=message_type,
            file=file_obj,
            file_name=file_obj.name,
            file_size=file_obj.size
        )
        
        print(f"✅ 消息创建成功:")
        print(f"  - 消息ID: {message.id}")
        print(f"  - 消息类型: {message.message_type}")
        
        serializer = MessageSerializer(message, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except ChatRoom.DoesNotExist:
        return Response({"error": "聊天室不存在"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"❌ 上传文件失败: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)