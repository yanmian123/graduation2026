"""
测试关注用户API
"""
import urllib.request
import json

base_url = 'http://localhost:8000'

# 使用userlzp的token
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcyODA4MjIzLCJpYXQiOjE3NzI3MjE4MjMsImp0aSI6ImZjMzE3MmVkMDg1MDRiZjRiMDI1MGM4Y2EyOTM3MDE2IiwidXNlcl9pZCI6IjIifQ.fcmdlb4r5c0BYoq4SNKBoxMP4lzQ7rrBHBQYt7MuQt4'

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

print("📋 测试关注用户API")
print("=" * 80)

# 1. 关注用户（用户ID 21）
print("\n1. 关注用户 (ID: 21)...")
req = urllib.request.Request(
    f'{base_url}/api/user/users/21/follow/',
    data=json.dumps({}).encode('utf-8'),
    headers=headers,
    method='POST'
)
try:
    with urllib.request.urlopen(req) as response:
        print(f"   状态码: {response.status}")
        if response.status == 200:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✅ {result.get('message')}")
        elif response.status == 400:
            result = json.loads(response.read().decode('utf-8'))
            print(f"⚠️ {result.get('error')}")
        elif response.status == 500:
            print(f"❌ 服务器错误")
            error_data = json.loads(response.read().decode('utf-8'))
            print(f"   错误信息: {error_data}")
except urllib.error.HTTPError as e:
    print(f"❌ HTTP错误: {e.code}")
    try:
        error_data = json.loads(e.read().decode('utf-8'))
        print(f"   错误信息: {error_data}")
    except:
        print(f"   无法解析错误信息")
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 2. 取消关注
print("\n2. 取消关注 (ID: 21)...")
req = urllib.request.Request(
    f'{base_url}/api/user/users/21/follow/',
    headers=headers,
    method='DELETE'
)
try:
    with urllib.request.urlopen(req) as response:
        print(f"   状态码: {response.status}")
        if response.status == 200:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✅ {result.get('message')}")
        elif response.status == 400:
            result = json.loads(response.read().decode('utf-8'))
            print(f"⚠️ {result.get('error')}")
        elif response.status == 500:
            print(f"❌ 服务器错误")
            error_data = json.loads(response.read().decode('utf-8'))
            print(f"   错误信息: {error_data}")
except urllib.error.HTTPError as e:
    print(f"❌ HTTP错误: {e.code}")
    try:
        error_data = json.loads(e.read().decode('utf-8'))
        print(f"   错误信息: {error_data}")
    except:
        print(f"   无法解析错误信息")
except Exception as e:
    print(f"❌ 请求失败: {e}")

print("\n" + "=" * 80)
print("📊 总结:")
print("  - 关注用户API现在应该正常工作")
print("  - 取消关注API现在应该正常工作")
