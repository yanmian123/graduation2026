from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from enterprise.models import Recruitment
from register.models import User

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
        """开始聊天（创建或获取聊天室）- 修改版：recruitment_id 可选"""
        enterprise_user_id = request.data.get('enterprise_user_id')
        job_seeker_user_id = request.data.get('job_seeker_user_id')
        recruitment_id = request.data.get('recruitment_id')  # 可选参数
        
        # 验证必需参数
        if not enterprise_user_id or not job_seeker_user_id:
            return Response(
                {"error": "缺少用户ID参数"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证用户是否存在
        try:
            enterprise_user = User.objects.get(id=enterprise_user_id, is_enterprise=True)
            job_seeker_user = User.objects.get(id=job_seeker_user_id, is_enterprise=False)
        except User.DoesNotExist:
            return Response(
                {"error": "用户不存在或用户类型不匹配"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取招聘信息（可选）
        recruitment = None
        if recruitment_id:
            try:
                recruitment = Recruitment.objects.get(id=recruitment_id)
            except Recruitment.DoesNotExist:
                # 招聘信息不存在不影响聊天室创建
                pass
        
        # 查找或创建聊天室 - 修改查找逻辑
        try:
            # 如果提供了 recruitment_id，精确匹配
            if recruitment_id:
                chat_room = ChatRoom.objects.get(
                    enterprise_user=enterprise_user,
                    job_seeker_user=job_seeker_user,
                    recruitment=recruitment
                )
            else:
                # 如果没有提供 recruitment_id，查找任意聊天室（包括没有关联招聘的）
                chat_room = ChatRoom.objects.filter(
                    enterprise_user=enterprise_user,
                    job_seeker_user=job_seeker_user
                ).first()
                
                # 如果没有找到，创建新的
                if not chat_room:
                    chat_room = ChatRoom.objects.create(
                        enterprise_user=enterprise_user,
                        job_seeker_user=job_seeker_user,
                        recruitment=None  # 明确设置为 None
                    )
                    created = True
                else:
                    created = False
                    
        except ChatRoom.DoesNotExist:
            # 精确匹配没找到，创建新的
            chat_room = ChatRoom.objects.create(
                enterprise_user=enterprise_user,
                job_seeker_user=job_seeker_user,
                recruitment=recruitment
            )
            created = True
        except ChatRoom.MultipleObjectsReturned:
            # 处理重复数据的情况
            chat_room = ChatRoom.objects.filter(
                enterprise_user=enterprise_user,
                job_seeker_user=job_seeker_user,
                recruitment=recruitment
            ).first()
            created = False
        
        serializer = self.get_serializer(chat_room)
        return Response(serializer.data, 
                    status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

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