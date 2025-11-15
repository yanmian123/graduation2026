from django.urls import path, include
from .views import ResumeViewSet
from rest_framework.routers import DefaultRouter
from .views import PdfUploadView
# 注册视图集（自动生成 CRUD 路由）
router = DefaultRouter()
# 路由前缀：/api/resumes/，后续前端请求需对应此路径
router.register(r'resumes', ResumeViewSet, basename='resume')

urlpatterns = [
    path('', include(router.urls)),
    path('upload-pdf/', PdfUploadView.as_view(), name='resume-upload-pdf'),
]