"""
简单测试API
"""
import urllib.request
import json

base_url = 'http://localhost:8000'

# 测试获取用户信息（使用已有的token）
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcyODAxNjY5LCJpYXQiOjE3NzI3MTUyNjksImp0aSI6ImQ0NGNhMGE2NDRkYjQwNmY4ZWRhYjFmYzhkZmM1MTBlIiwidXNlcl9pZCI6IjIifQ.xMA0S2q_-njCFJ-2wZqRRHIfdImh-1LGpHdGgypcQ_I'

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

print("📋 获取用户信息...")
req = urllib.request.Request(f'{base_url}/api/user/info/', headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            user_info = json.loads(response.read().decode('utf-8'))
            print(f"✅ 用户信息获取成功:")
            print(f"  - 用户名: {user_info.get('username')}")
            print(f"  - 昵称: {user_info.get('nickname')}")
            print(f"  - 粉丝数: {user_info.get('follower_count', 0)}")
            print(f"  - 关注数: {user_info.get('following_count', 0)}")
        else:
            print(f"❌ 获取用户信息失败: {response.status}")
except Exception as e:
    print(f"❌ 请求失败: {e}")

print("\n👥 获取粉丝列表...")
req = urllib.request.Request(f'{base_url}/api/user/followers/', headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            followers = json.loads(response.read().decode('utf-8'))
            print(f"✅ 粉丝列表获取成功，共 {len(followers)} 个粉丝:")
            for follower in followers:
                print(f"  - {follower.get('username')} ({follower.get('nickname', '无昵称')})")
        else:
            print(f"❌ 获取粉丝列表失败: {response.status}")
except Exception as e:
    print(f"❌ 请求失败: {e}")

print("\n👥 获取关注列表...")
req = urllib.request.Request(f'{base_url}/api/user/following/', headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            following = json.loads(response.read().decode('utf-8'))
            print(f"✅ 关注列表获取成功，共 {len(following)} 个关注:")
            for user in following:
                print(f"  - {user.get('username')} ({user.get('nickname', '无昵称')})")
        else:
            print(f"❌ 获取关注列表失败: {response.status}")
except Exception as e:
    print(f"❌ 请求失败: {e}")

print("\n🎉 测试完成！")
