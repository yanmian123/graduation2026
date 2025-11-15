from django.urls import include, path
from .views import UserInfoView
urlpatterns = [
    # 接口路径：/api/user/info/（用于获取和更新用户信息）
    path('info/', UserInfoView.as_view(),name='userinfo'),  # 用户信息相关路由
]
