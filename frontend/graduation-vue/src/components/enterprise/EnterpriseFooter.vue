<!-- src/components/enterprise/EnterpriseFooter.vue -->
<template>
  <footer class="enterprise-footer">
    <div class="enterprise-footer-content">
      <!-- 企业服务链接 -->
      <div class="footer-sections">
        <div class="footer-section">
          <h3>招聘服务</h3>
          <a @click="$router.push('/enterprise/recruitments')">职位管理</a>
          <a @click="$router.push('/enterprise/resumes')">简历筛选</a>
          <a>人才推荐</a>
        </div>
        
        <div class="footer-section">
          <h3>企业服务</h3>
          <a>数据统计</a>
          <a>招聘分析</a>
          <a>企业认证</a>
        </div>
        
        <div class="footer-section">
          <h3>支持帮助</h3>
          <a>使用指南</a>
          <a>常见问题</a>
          <a>联系我们</a>
        </div>
        
        <div class="footer-section">
          <h3>联系我们</h3>
          <p>企业服务专线：400-xxx-xxxx</p>
          <p>邮箱：enterprise@careerplatform.com</p>
          <p>工作时间：工作日 9:00-18:00</p>
        </div>
      </div>
      
      <!-- 版权信息 -->
      <div class="footer-copyright">
        <p>© 2025 职享圈 - 企业招聘服务平台 | 提供专业的企业招聘解决方案</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { NButton } from 'naive-ui'
</script>

<style scoped>
.enterprise-footer {
  background-color: #f5f7fa;
  border-top: 1px solid #e4e7ed;
  margin-top: auto;
}

.enterprise-footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px 20px;
}

.footer-sections {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 40px;
  margin-bottom: 30px;
}

.footer-section h3 {
  color: #1a237e;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
}

.footer-section a {
  display: block;
  color: #606266;
  text-decoration: none;
  margin-bottom: 8px;
  cursor: pointer;
  transition: color 0.2s;
}

.footer-section a:hover {
  color: #1a237e;
}

.footer-section p {
  color: #606266;
  margin-bottom: 8px;
  font-size: 14px;
}

.footer-copyright {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
  color: #909399;
  font-size: 14px;
}

@media (max-width: 768px) {
  .footer-sections {
    grid-template-columns: repeat(2, 1fr);
    gap: 30px;
  }
}

@media (max-width: 480px) {
  .footer-sections {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}
</style>