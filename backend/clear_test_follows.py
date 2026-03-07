"""
清除所有测试关注关系
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings')
django.setup()

from user_info.models import Follow

# 清除所有关注关系
count = Follow.objects.all().count()
Follow.objects.all().delete()

print(f"🗑️ 已清除 {count} 条关注关系")
print("✅ 现在所有用户的粉丝数和关注数都是0")
