<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-logo">
        <n-icon size="24" class="logo-icon">
          <Briefcase />
        </n-icon>
        <span class="logo-text"> - 大学生就业资源共享平台</span>
      </div>
      
      <div class="footer-links">
        <div class="link-group">
          <h3>平台服务</h3>
          <ul>
            <li><a href="#">校招信息</a></li>
            <li><a href="#">实习推荐</a></li>
            <li><a href="#">简历服务</a></li>
            <li><a href="#">就业指导</a></li>
          </ul>
        </div>
        
        <div class="link-group">
          <h3>关于我们</h3>
          <ul>
            <li><a href="#">平台介绍</a></li>
            <li><a href="#">联系我们</a></li>
            <li><a href="#">合作招募</a></li>
            <li><a href="#">隐私政策</a></li>
          </ul>
        </div>
        
        <div class="link-group">
          <h3>帮助中心</h3>
          <ul>
            <li><a href="#">使用指南</a></li>
            <li><a href="#">常见问题</a></li>
            <li><a href="#">意见反馈</a></li>
          </ul>
        </div>
      </div>
      
      <div class="copyright">
        <p>© 2025 lzp 版权所有 | 大学生就业信息资源共享平台</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { NIcon } from 'naive-ui'
import { Briefcase } from '@vicons/ionicons5'
</script>

<style scoped>
.footer {
  background-color: #f7f8fa;
  border-top: 1px solid #e8e8e8;
  margin-top: 60px;
}

.footer-content {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.footer-logo {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}

.footer-links {
  display: flex;
  gap: 80px;
  margin-bottom: 32px;
}

.link-group h3 {
  font-size: 16px;
  margin-bottom: 16px;
}

.link-group ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.link-group li {
  margin-bottom: 8px;
}

.link-group a {
  color: #4e5969;
  text-decoration: none;
  font-size: 14px;
}

.link-group a:hover {
  color: #2d8cf0;
}

.copyright {
  text-align: center;
  color: #86909c;
  font-size: 14px;
  padding-top: 20px;
  border-top: 1px solid #e8e8e8;
}

@media (max-width: 768px) {
  .footer-links {
    flex-direction: column;
    gap: 30px;
  }
}
</style>