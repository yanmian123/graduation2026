"""
测试关注企业API（详细版）
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

print("📋 测试关注企业API（详细版）")
print("=" * 80)

# 1. 获取用户信息（包含关注企业数量）
print("\n1. 获取用户信息...")
req = urllib.request.Request(
    f'{base_url}/api/user/info/',
    headers=headers,
    method='GET'
)
try:
    with urllib.request.urlopen(req) as response:
        print(f"   状态码: {response.status}")
        if response.status == 200:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✅ 获取成功")
            print(f"   用户名: {result.get('username')}")
            print(f"   粉丝数: {result.get('follower_count', 0)}")
            print(f"   关注数: {result.get('following_count', 0)}")
            print(f"   关注企业数: {result.get('following_enterprise_count', 0)}")
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

# 2. 获取关注的企业列表
print("\n2. 获取关注的企业列表...")
req = urllib.request.Request(
    f'{base_url}/api/user/following-enterprises/',
    headers=headers,
    method='GET'
)
try:
    with urllib.request.urlopen(req) as response:
        print(f"   状态码: {response.status}")
        if response.status == 200:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✅ 获取成功")
            print(f"   关注企业数量: {len(result)}")
            if result:
                for enterprise in result:
                    print(f"   - {enterprise.get('name')} (ID: {enterprise.get('id')})")
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
