<template>
  <n-message-provider>
    <!-- 你的路由出口，所有页面都会渲染在这里 -->
    <router-view />
  </n-message-provider>
</template>

<script setup lang="ts">
import { NMessageProvider } from 'naive-ui';
</script>