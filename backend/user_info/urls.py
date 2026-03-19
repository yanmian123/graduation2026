from django.urls import path, include
from rest_framework.routers import DefaultRouter
from article_publish.views import UserViewSet, FileUploadView
from .views import VerificationViewSet, SensitiveWordViewSet

router = DefaultRouter()
router.register(r'verifications', VerificationViewSet, basename='verification')
router.register(r'sensitive_words', SensitiveWordViewSet, basename='sensitive_word')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('info/', UserViewSet.as_view({'get': 'info', 'put': 'info'}), name='user-info'),
    path('followers/', UserViewSet.as_view({'get': 'followers'}), name='user-followers'),
    path('following/', UserViewSet.as_view({'get': 'following'}), name='user-following'),
    path('following-enterprises/', UserViewSet.as_view({'get': 'following_enterprises'}), name='user-following-enterprises'),
    path('upload/file/', FileUploadView.as_view(), name='file-upload'),
]
