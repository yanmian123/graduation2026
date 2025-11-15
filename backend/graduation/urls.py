"""
URL configuration for graduation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.urls import include 
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path("admin/", admin.site.urls),
    # path("api/", include("api.urls")),  # Include API app URLs
    path('api/', include('register.urls')),  # 注册接口路径：/api/auth/register/
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),# JWT登录接口
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # 刷新令牌接口
    path('api/user/', include('user_info.urls')),  # 用户信息接口路径：/api/user/
    path('api/', include('resume.urls')), #简历接口路径：/api/resumes/
    path('api/', include('article_publish.urls')), #文章发布接口路径：/api/posts/
    path('api/', include('enterprise.urls')), #企业模块接口路径：/api/enterprise/
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
