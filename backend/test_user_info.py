import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings')
django.setup()

from django.test import Client
import json

def test_user_info():
    client = Client()
    
    # 模拟登录获取token
    login_response = client.post('/api/login/',
                                   data=json.dumps({'username': 'testuser', 'password': 'testpass123'}),
                                   content_type='application/json',
                                   HTTP_ORIGIN='http://localhost:5173')
    
    print(f"登录响应: {login_response.status_code}")
    if login_response.status_code == 200:
        token_data = json.loads(login_response.content)
        token = token_data.get('access')
        print(f"获取到token: {token[:20]}...")
        
        # 测试获取用户信息
        info_response = client.get('/api/user/info/',
                                   HTTP_AUTHORIZATION=f'Bearer {token}',
                                   HTTP_ORIGIN='http://localhost:5173')
        
        print(f"\n获取用户信息状态码: {info_response.status_code}")
        print(f"响应内容: {info_response.content.decode('utf-8')}")
        
        if info_response.status_code == 200:
            print("✓ 用户信息获取成功")
        else:
            print("✗ 用户信息获取失败")
    else:
        print(f"登录失败: {login_response.content.decode('utf-8')}")

if __name__ == "__main__":
    test_user_info()
