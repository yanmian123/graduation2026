"""
验证前端显示逻辑
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

print("📋 验证前端显示逻辑")
print("=" * 80)

# 1. 获取userlzp的用户信息
print("\n1. 获取userlzp的用户信息...")
req = urllib.request.Request(f'{base_url}/api/user/info/', headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            user_info = json.loads(response.read().decode('utf-8'))
            print(f"✅ 用户名: {user_info.get('username')}")
            print(f"   follower_count: {user_info.get('follower_count', 0)}")
            print(f"   following_count: {user_info.get('following_count', 0)}")
            print(f"\n   前端应该显示:")
            print(f"   - 粉丝数: {user_info.get('follower_count', 0)}")
            print(f"   - 关注数: {user_info.get('following_count', 0)}")
except Exception as e:
    print(f"❌ 获取用户信息失败: {e}")

# 2. 获取userlzp2的用户信息（使用userlzp2的token）
print("\n2. 获取userlzp2的用户信息...")
token2 = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcyODA4NzMyLCJpYXQiOjE3NzI3MjIzMzIsImp0aSI6ImM0ZjA2ZDg0Y2NhZDQzODU5OTM0MGQ3MjJmYjYzYTY5IiwidXNlcl9pZCI6IjIzIn0.bC5WwWwTgfmzU0AxgXMlppvuJOTN0uBIKrxtJ-EV06w'
headers2 = {
    'Authorization': f'Bearer {token2}',
    'Content-Type': 'application/json'
}

req = urllib.request.Request(f'{base_url}/api/user/info/', headers=headers2)
try:
    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            user_info = json.loads(response.read().decode('utf-8'))
            print(f"✅ 用户名: {user_info.get('username')}")
            print(f"   follower_count: {user_info.get('follower_count', 0)}")
            print(f"   following_count: {user_info.get('following_count', 0)}")
            print(f"\n   前端应该显示:")
            print(f"   - 粉丝数: {user_info.get('follower_count', 0)}")
            print(f"   - 关注数: {user_info.get('following_count', 0)}")
except Exception as e:
    print(f"❌ 获取用户信息失败: {e}")

print("\n" + "=" * 80)
print("📊 总结:")
print("  - userlzp 关注了 userlzp2")
print("  - userlzp 的个人主页应该显示:")
print("    - 粉丝数: 0")
print("    - 关注数: 1")
print("  - userlzp2 的个人主页应该显示:")
print("    - 粉丝数: 1")
print("    - 关注数: 0")
