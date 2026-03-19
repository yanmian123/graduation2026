from django.urls import path
from . import views
from .serializers import CustomTokenObtainPairView

urlpatterns = [
    path('send-register-code/', views.send_register_code, name='send_register_code'),
    path('register/', views.register, name='register'),
    path('send-reset-code/', views.send_reset_code, name='send_reset_code'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('login/', CustomTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),
    path('user/info/', views.user_info, name='user_info'),
]