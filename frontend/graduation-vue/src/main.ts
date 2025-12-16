import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
// import naive from 'naive-ui'

import './assets/styles/global.css'

// 正确导入Naive UI
import { 
  create, 
  NButton, 
  NTable, 
  NCard, 
  NTag, 
  NMessageProvider,
  NConfigProvider,
  NLayout,
  NLayoutHeader,
  NLayoutContent,
  NLayoutFooter,
  NMenu,
  NInput,
  NDropdown,
  NAvatar,
  NIcon,
  NForm,
  NFormItem,
  NSelect,
  NCheckbox,
  NEmpty,
  NSpin,
  NResult,
  NSpace,
  NCollapse,
  NCollapseItem
} from 'naive-ui'

// 创建Naive UI实例
const naive = create({
  components: [
    NButton,
    NTable,        // 确保NTable被注册
    NCard,
    NTag,
    NMessageProvider,
    NConfigProvider,
    NLayout,
    NLayoutHeader,
    NLayoutContent,
    NLayoutFooter,
    NMenu,
    NInput,
    NDropdown,
    NAvatar,
    NIcon,
    NForm,
    NFormItem,
    NSelect,
    NCheckbox,
    NEmpty,
    NSpin,
    NResult,
    NSpace,
    NCollapse,
    NCollapseItem
  ]
})
const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(naive) 
app.mount('#app')
