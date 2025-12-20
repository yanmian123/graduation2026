<!-- src/layouts/EnterpriseLayout.vue -->
<template>
  <div class="enterprise-layout">
    <!-- 企业专用导航栏 -->
    <EnterpriseHeader />
    
    <!-- 主要内容区域 -->
    <main class="enterprise-main-content">
      <router-view />
    </main>
    
    <!-- 企业专用页脚 -->
    <EnterpriseFooter />
  </div>
</template>

<script setup>
import EnterpriseHeader from '@/components/enterprise/EnterpriseHeader.vue'
import EnterpriseFooter from '@/components/enterprise/EnterpriseFooter.vue'
</script>

<style scoped>
.enterprise-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.enterprise-main-content {
  flex: 1;
  padding: 20px 0;
  background-color: #f8f9fa;
}
</style>