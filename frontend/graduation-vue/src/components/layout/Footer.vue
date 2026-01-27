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
          
          <div class="link-group">
            <h3>关注我们</h3>
            <div class="social-links">
              <a href="#" class="social-link">
                <n-icon size="24"><LogoGithub /></n-icon>
              </a>
              <a href="#" class="social-link">
                <n-icon size="24"><LogoWechat /></n-icon>
              </a>
            </div>
            <p class="contact-info">企业服务专线：400-xxx-xxxx</p>
            <p class="contact-info">邮箱：service@careerplatform.com</p>
          </div>
        </div>
      </div>
      
      <div class="footer-bottom">
        <div class="copyright">
          <p>© 2025 lzp 版权所有 | 大学生就业信息资源共享平台</p>
          <p class="icp">ICP备案号：京ICP备XXXXXXXX号</p>
        </div>
        <div class="footer-links-bottom">
          <a href="#">用户协议</a>
          <span class="separator">|</span>
          <a href="#">隐私政策</a>
          <span class="separator">|</span>
          <a href="#">免责声明</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { NIcon } from 'naive-ui'
import { Briefcase, LogoGithub, LogoWechat } from '@vicons/ionicons5'
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
  color: rgb(47, 181, 159);
  transform: translateX(4px);
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

.social-links {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.social-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  transition: all 0.3s ease;
  color: white;
}

.social-link:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.contact-info {
  font-size: 13px;
  opacity: 0.85;
  margin: 8px 0;
  line-height: 1.6;
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 30px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.copyright {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.copyright p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

.icp {
  font-size: 12px;
  opacity: 0.7;
}

.footer-links-bottom {
  display: flex;
  align-items: center;
  gap: 12px;
}

.footer-links-bottom a {
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  font-size: 13px;
  transition: all 0.3s ease;
}

.footer-links-bottom a:hover {
  color: white;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

.separator {
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
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
  
  .footer-bottom {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .footer-links-bottom {
    flex-wrap: wrap;
    justify-content: center;
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
  
  .footer-links-bottom {
    flex-direction: column;
    gap: 8px;
  }
  
  .separator {
    display: none;
  }
}
</style>