<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-top">
        <div class="footer-logo">
          <div class="logo-icon-wrapper">
            <n-icon size="32" class="logo-icon">
              <Briefcase />
            </n-icon>
          </div>
          <div class="logo-text">
            <span class="logo-title">职享圈</span>
            <span class="logo-subtitle">大学生就业资源共享平台</span>
          </div>
          <p class="logo-description">为大学生提供专业的就业信息、求职指导和职业发展服务</p>
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
            <h3>帮助中心</h3>
            <ul>
              <li><a href="#">使用指南</a></li>
              <li><a href="#">常见问题</a></li>
              <li><a href="#">意见反馈</a></li>
            </ul>
          </div>
        </div>
      </div>
      
      <div class="footer-bottom">
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
  background: linear-gradient(135deg, #bad2ce 0%, #9ddcd0 100%);
  color: rgb(40, 37, 37);
  margin-top: 60px;
  position: relative;
  overflow: hidden;
}

.footer::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="rgba(255,255,255,0.03)"/></svg>');
  background-size: 200px;
  opacity: 0.5;
  pointer-events: none;
}

.footer-content {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 20px 30px;
  position: relative;
  z-index: 1;
}

.footer-top {
  display: flex;
  gap: 60px;
  margin-bottom: 40px;
}

.footer-logo {
  flex: 0 0 300px;
}

.logo-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 14px;
  margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.logo-icon {
  color: rgb(37, 36, 36);
}

.logo-text {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

.logo-title {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 1px;
  margin-bottom: 4px;
}

.logo-subtitle {
  font-size: 14px;
  font-weight: 400;
  opacity: 0.9;
}

.logo-description {
  font-size: 14px;
  line-height: 1.8;
  opacity: 0.85;
  margin: 0;
}

.footer-links {
  flex: 1;
  display: flex;
  gap: 40px;
}

.link-group {
  flex: 1;
}

.link-group h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  position: relative;
  padding-bottom: 12px;
}

.link-group h3::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 3px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 2px;
}

.link-group ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.link-group li {
  margin-bottom: 12px;
}

.link-group a {
  color: rgba(30, 29, 29, 0.85);
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s ease;
  display: inline-block;
}

.link-group a:hover {
  color: rgb(47, 181, 136);
  transform: translateX(4px);
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

.footer-bottom {
  padding-top: 30px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

@media (max-width: 1024px) {
  .footer-top {
    flex-direction: column;
    gap: 40px;
  }
  
  .footer-logo {
    flex: 0 0 auto;
  }
  
  .footer-links {
    flex-wrap: wrap;
  }
  
  .link-group {
    flex: 1 1 calc(50% - 20px);
    min-width: 200px;
  }
}

@media (max-width: 768px) {
  .footer-content {
    padding: 40px 20px 20px;
  }
  
  .link-group {
    flex: 1 1 100%;
  }
}

@media (max-width: 480px) {
  .footer-logo {
    text-align: center;
  }
  
  .logo-icon-wrapper {
    margin: 0 auto 16px;
  }
  
  .logo-title {
    font-size: 24px;
  }
  
  .footer-links {
    flex-direction: column;
    gap: 30px;
  }
}
</style>