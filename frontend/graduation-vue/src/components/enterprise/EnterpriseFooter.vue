<!-- src/components/enterprise/EnterpriseFooter.vue -->
<template>
  <footer class="enterprise-footer">
    <div class="enterprise-footer-content">
      <div class="footer-top">
        <div class="footer-brand">
          <div class="brand-icon-wrapper">
            <n-icon size="32" class="brand-icon">
              <Business />
            </n-icon>
          </div>
          <div class="brand-text">
            <span class="brand-title">企业服务中心</span>
            <span class="brand-subtitle">专业的一站式企业招聘解决方案</span>
          </div>
          <p class="brand-description">为企业提供高效的招聘管理、人才筛选和数据分析服务</p>
        </div>
        
        <div class="footer-sections">
          <div class="footer-section">
            <h3>招聘服务</h3>
            <ul>
              <li><a @click="$router.push('/enterprise/recruitments')">职位管理</a></li>
              <li><a @click="$router.push('/enterprise/resumes')">简历筛选</a></li>
              <li><a>人才推荐</a></li>
              <li><a>批量招聘</a></li>
            </ul>
          </div>
          
          <div class="footer-section">
            <h3>企业服务</h3>
            <ul>
              <li><a>数据统计</a></li>
              <li><a>招聘分析</a></li>
              <li><a>企业认证</a></li>
              <li><a>品牌展示</a></li>
            </ul>
          </div>
          
          <div class="footer-section">
            <h3>支持帮助</h3>
            <ul>
              <li><a>使用指南</a></li>
              <li><a>常见问题</a></li>
              <li><a>联系我们</a></li>
              <li><a>意见反馈</a></li>
            </ul>
          </div>
          
          <div class="footer-section">
            <h3>联系方式</h3>
            <div class="contact-info">
              <div class="contact-item">
                <n-icon size="18"><PhonePortrait /></n-icon>
                <span>企业服务专线：400-xxx-xxxx</span>
              </div>
              <div class="contact-item">
                <n-icon size="18"><Mail /></n-icon>
                <span>邮箱：enterprise@careerplatform.com</span>
              </div>
              <div class="contact-item">
                <n-icon size="18"><Time /></n-icon>
                <span>工作时间：工作日 9:00-18:00</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="footer-bottom">
        <div class="copyright">
          <p>© 2025 职享圈 - 企业招聘服务平台 | 提供专业的企业招聘解决方案</p>
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
import { NButton, NIcon } from 'naive-ui'
import { Business, PhonePortrait, Mail, Time } from '@vicons/ionicons5'
</script>

<style scoped>
.enterprise-footer {
  background: linear-gradient(135deg, #bad2ce 0%,#9ddcd0 100%);
  color: rgb(31, 29, 29);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: auto;
  position: relative;
  overflow: hidden;
}

.enterprise-footer::before {
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

.enterprise-footer-content {
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

.footer-brand {
  flex: 0 0 300px;
}

.brand-icon-wrapper {
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

.brand-icon {
  color: rgb(41, 39, 39);
}

.brand-text {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

.brand-title {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.brand-subtitle {
  font-size: 14px;
  font-weight: 400;
  opacity: 0.9;
}

.brand-description {
  font-size: 14px;
  line-height: 1.8;
  opacity: 0.85;
  margin: 0;
}

.footer-sections {
  flex: 1;
  display: flex;
  gap: 40px;
}

.footer-section {
  flex: 1;
}

.footer-section h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  position: relative;
  padding-bottom: 12px;
}

.footer-section h3::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 3px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 2px;
}

.footer-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-section li {
  margin-bottom: 12px;
}

.footer-section a {
  display: block;
  color: rgba(33, 32, 32, 0.85);
  text-decoration: none;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.footer-section a:hover {
  color: rgb(7, 155, 96);
  transform: translateX(4px);
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: rgba(38, 38, 38, 0.85);
  font-size: 14px;
  line-height: 1.6;
}

.contact-item .n-icon {
  flex-shrink: 0;
  color: rgba(38, 38, 38, 0.85);
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
  
  .footer-brand {
    flex: 0 0 auto;
  }
  
  .footer-sections {
    flex-wrap: wrap;
  }
  
  .footer-section {
    flex: 1 1 calc(50% - 20px);
    min-width: 200px;
  }
}

@media (max-width: 768px) {
  .enterprise-footer-content {
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
  
  .footer-section {
    flex: 1 1 100%;
  }
}

@media (max-width: 480px) {
  .footer-brand {
    text-align: center;
  }
  
  .brand-icon-wrapper {
    margin: 0 auto 16px;
  }
  
  .brand-title {
    font-size: 20px;
  }
  
  .footer-sections {
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