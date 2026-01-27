from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('send-reset-code/', views.send_reset_code, name='send_reset_code'),
    path('reset-password/', views.reset_password, name='reset_password'),
]