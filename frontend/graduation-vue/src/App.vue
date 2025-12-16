<!-- src/App.vue -->
<template>
  <n-config-provider>
    <n-message-provider>
      <!-- 布局切换器 -->
      <component :is="currentLayout">
        <router-view />
      </component>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { NConfigProvider, NMessageProvider } from 'naive-ui'

// 布局组件
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import EnterpriseLayout from '@/layouts/EnterpriseLayout.vue'
import EmptyLayout from '@/layouts/EmptyLayout.vue'
const route = useRoute()

// 根据路由元信息动态选择布局
const currentLayout = computed(() => {
  const layout = route.meta?.layout || 'empty'
  
  const layoutMap = {
    default: DefaultLayout,
    enterprise: EnterpriseLayout,
    empty:EmptyLayout
  }
  
  return layoutMap[layout] || DefaultLayout
})

// 错误处理
const errorHandler = (err) => {
  console.error('应用错误:', err)
}
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #f5f7fa;
}

#app {
  min-height: 100vh;
}
</style>