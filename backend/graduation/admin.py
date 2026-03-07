"""
自定义Django Admin配置
让管理员界面与平台风格一致
"""
from django.contrib import admin
from django.contrib.admin.sites import AdminSite

# 覆盖默认Admin站点的标题
admin.site.site_header = '大学生就业信息共享平台'
admin.site.site_title = '管理后台'
admin.site.index_title = '欢迎来到管理后台'