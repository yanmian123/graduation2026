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
from rest_framework_simplejwt.views import TokenObtainPairView
urlpatterns = [
    path("admin/", admin.site.urls),
    # path("api/", include("api.urls")),  # Include API app URLs
    path('api/', include('register.urls')),  # 注册接口路径：/api/auth/register/
    path('login/', TokenObtainPairView.as_view(), name='login'),# JWT登录接口
]
