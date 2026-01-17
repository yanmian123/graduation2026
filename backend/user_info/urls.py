from django.urls import include, path
from .views import UserInfoView, ActiveUsersView
urlpatterns = [
    # 接口路径：/api/user/info/（用于获取和更新用户信息）
    path('info/', UserInfoView.as_view(),name='userinfo'),  # 用户信息相关路由
    path('active/', ActiveUsersView.as_view(),name='active-users'),  # 活跃用户列表路由
]
