import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings')
django.setup()

from django.test import Client
import json

def test_login():
    client = Client()
    
    # 测试登录
    url = '/api/login/'
    data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    
    response = client.post(url, 
                           data=json.dumps(data),
                           content_type='application/json',
                           HTTP_ORIGIN='http://localhost:5173')
    
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应内容: {response.content.decode('utf-8')}")
    
    # 检查CORS头
    if 'Access-Control-Allow-Origin' in response:
        print(f"✓ CORS配置正确: {response['Access-Control-Allow-Origin']}")
    else:
        print("✗ 缺少CORS头")

if __name__ == "__main__":
    test_login()
