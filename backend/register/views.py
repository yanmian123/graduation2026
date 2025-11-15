from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import RegisterSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    print(f"Received data: {request.data}")  # 打印接收到的数据
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "注册成功！请登录"},
            status=status.HTTP_201_CREATED
        )
    print(f"Errors: {serializer.errors}")  # 打印验证错误
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

