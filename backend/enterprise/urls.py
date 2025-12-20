from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnterpriseViewSet, RecruitmentViewSet, JobApplicationViewSet
# 注册视图集
router = DefaultRouter()
router.register(r'enterprises', EnterpriseViewSet, basename='enterprise')  # 企业信息接口
router.register(r'recruitments', RecruitmentViewSet, basename='recruitment')  # 招聘信息接口
router.register(r'applications', JobApplicationViewSet, basename='application')  
# 应用内路由
urlpatterns = [
    path('', include(router.urls)),
    
]