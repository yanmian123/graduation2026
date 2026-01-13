from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from enterprise.models import Recruitment
from register.models import User
from rest_framework.decorators import api_view, permission_classes
from django.conf import settings
import os

class IsChatParticipant(permissions.BasePermission):
    """验证用户是否是聊天室的参与者"""
    def has_object_permission(self, request, view, obj):
        return obj.enterprise_user == request.user or obj.job_seeker_user == request.user

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

# 在ChatRoomViewSet中修改start_chat方法
    @action(detail=False, methods=['post'])
    def start_chat(self, request):
        """
        开始聊天 - 忽略recruitment_id，只根据用户ID创建
        """
        enterprise_user_id = request.data.get('enterprise_user_id')
        job_seeker_user_id = request.data.get('job_seeker_user_id')
        recruitment_id = request.data.get('recruitment_id')  # 保留但不使用
        
        print(f"🔍🔍 开始聊天请求参数: enterprise={enterprise_user_id}, job_seeker={job_seeker_user_id}, recruitment={recruitment_id}")
        
        # 1. 验证必需参数
        if not enterprise_user_id or not job_seeker_user_id:
            return Response(
                {"error": "缺少用户ID参数"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. 验证用户是否存在且类型正确
        try:
            enterprise_user = User.objects.get(id=enterprise_user_id, is_enterprise=True)
            job_seeker_user = User.objects.get(id=job_seeker_user_id, is_enterprise=False)
            print(f"✅ 用户验证成功: 企业用户={enterprise_user.username}, 求职者={job_seeker_user.username}")
        except User.DoesNotExist:
            return Response(
                {"error": "用户不存在或用户类型不匹配"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 3. 简单查找或创建聊天室 - 只根据用户ID
        created = False
        
        try:
            # 只根据用户ID查找，忽略recruitment_id
            chat_rooms = ChatRoom.objects.filter(
                enterprise_user=enterprise_user,
                job_seeker_user=job_seeker_user
            ).order_by('-created_at')  # 取最新的一个
            
            if chat_rooms.exists():
                # 使用已存在的聊天室（取最新的）
                chat_room = chat_rooms.first()
                created = False
                print("✅ 找到已存在的聊天室")
            else:
                # 创建新的聊天室，recruitment_id设为null
                chat_room = ChatRoom.objects.create(
                    enterprise_user=enterprise_user,
                    job_seeker_user=job_seeker_user,
                    recruitment=None  # 总是设为null
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
    
    def perform_create(self, serializer):
        room_id = self.kwargs.get('room_id')
        chat_room = ChatRoom.objects.get(id=room_id)
        serializer.save(chat_room=chat_room, sender=self.request.user)
    
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
        
        # 创建文件消息
        message = Message.objects.create(
            chat_room=chat_room,
            sender=request.user,
            content=f"文件: {file_obj.name}",
            message_type='file',
            file=file_obj,
            file_name=file_obj.name,
            file_size=file_obj.size
        )
        
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except ChatRoom.DoesNotExist:
        return Response({"error": "聊天室不存在"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)