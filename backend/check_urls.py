"""
检查生成的URL
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings')
django.setup()

from django.urls import get_resolver

resolver = get_resolver()
print("📋 生成的URL列表:")
print("=" * 80)

for pattern in resolver.url_patterns:
    try:
        print(f"\n{pattern}")
        if hasattr(pattern, 'url_patterns'):
            for sub_pattern in pattern.url_patterns:
                print(f"  - {sub_pattern}")
                if hasattr(sub_pattern, 'url_patterns'):
                    for sub_sub_pattern in sub_pattern.url_patterns:
                        print(f"    - {sub_sub_pattern}")
    except Exception as e:
        print(f"  Error: {e}")

print("\n" + "=" * 80)
