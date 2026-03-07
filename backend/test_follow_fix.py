"""
测试关注功能
"""
import urllib.request
import json

base_url = 'http://localhost:8000'

# 使用userlzp的token（ID: 2）来关注userlzp2（ID: 23）
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcyODA4MjIzLCJpYXQiOjE3NzI3MjE4MjMsImp0aSI6ImZjMzE3MmVkMDg1MDRiZjRiMDI1MGM4Y2EyOTM3MDE2IiwidXNlcl9pZCI6IjIifQ.fcmdlb4r5c0BYoq4SNKBoxMP4lzQ7rrBHBQYt7MuQt4'

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

target_user_id = 23  # userlzp2的ID

print("📋 测试关注功能")
print("=" * 60)

# 1. 获取当前用户信息
print("\n1. 获取当前用户信息...")
req = urllib.request.Request(f'{base_url}/api/user/info/', headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            user_info = json.loads(response.read().decode('utf-8'))
            print(f"✅ 当前用户: {user_info.get('username')}")
            print(f"   粉丝数: {user_info.get('follower_count', 0)}")
            print(f"   关注数: {user_info.get('following_count', 0)}")
except Exception as e:
    print(f"❌ 获取用户信息失败: {e}")

# 2. 关注userlzp2
print(f"\n2. 关注用户ID {target_user_id}...")
req = urllib.request.Request(
    f'{base_url}/api/user/users/{target_user_id}/follow/',
    data=json.dumps({}).encode('utf-8'),
    headers=headers,
    method='POST'
)
try:
    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✅ {result.get('message')}")
        elif response.status == 400:
            result = json.loads(response.read().decode('utf-8'))
            print(f"⚠️ {result.get('error')}")
except Exception as e:
    print(f"❌ 关注失败: {e}")

# 3. 再次获取当前用户信息
print("\n3. 关注后获取用户信息...")
req = urllib.request.Request(f'{base_url}/api/user/info/', headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            user_info = json.loads(response.read().decode('utf-8'))
            print(f"✅ 当前用户: {user_info.get('username')}")
            print(f"   粉丝数: {user_info.get('follower_count', 0)}")
            print(f"   关注数: {user_info.get('following_count', 0)}")
except Exception as e:
    print(f"❌ 获取用户信息失败: {e}")

# 4. 获取关注列表
print("\n4. 获取关注列表...")
req = urllib.request.Request(f'{base_url}/api/user/following/', headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            following = json.loads(response.read().decode('utf-8'))
            print(f"✅ 关注列表（共 {len(following)} 个）:")
            for user in following:
                print(f"   - {user.get('username')} ({user.get('nickname', '无昵称')})")
except Exception as e:
    print(f"❌ 获取关注列表失败: {e}")

print("\n🎉 测试完成！")
