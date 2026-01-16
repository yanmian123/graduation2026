from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'chatrooms', views.ChatRoomViewSet, basename='chatroom')

urlpatterns = [
    path('', include(router.urls)),

    path('chatrooms/<int:room_id>/messages/', views.MessageViewSet.as_view({
        'get': 'list', 
        'post': 'create'
    }), name='message-list'),
    path('chatrooms/<int:room_id>/messages/<int:pk>/mark_as_read/', views.MessageViewSet.as_view({
        'post': 'mark_as_read'
    }), name='message-mark-as-read'),
    path('chatrooms/<int:room_id>/upload/', views.upload_file, name='upload-file'),
]