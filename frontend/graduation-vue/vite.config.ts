import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    proxy: {
      // 将所有以 '/api' 开头的请求转发到后端
      '/api': {
        target: 'http://localhost:8000',  // 后端服务器地址
        changeOrigin: true,  // 允许跨域
        // rewrite: (path) => path.replace(/^\/api/, ''),  // 移除路径中的 '/api' 前缀（根据后端接口是否需要决定）
        ws: false // 如果不需要代理 websockets，可以设置为 false
      },
    },
  },
})
