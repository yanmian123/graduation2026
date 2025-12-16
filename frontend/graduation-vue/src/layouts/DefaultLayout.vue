<!-- src/layouts/DefaultLayout.vue -->
<template>
  <div class="default-layout">
    <LayoutHeader />
    <main class="main-content">
      <router-view />
    </main>
    <LayoutFooter />
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/layout/Header.vue'
import LayoutFooter from '@/components/layout/Footer.vue'
</script>

<style scoped>
.default-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
}
</style>