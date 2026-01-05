import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import './assets/styles/global.css'

// 从naive-ui导入需要的组件
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
  NLayoutSider,  // 新增：侧边栏组件
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
  NCollapseItem,
  NModal, 
  NAlert, 
  NRadio, 
  NRadioGroup, 
  NText,
  NDataTable,
  NList,         // 新增：列表组件
  NListItem,     // 新增：列表项组件
  NBadge,        // 新增：徽章组件
  NScrollbar,    // 新增：滚动条组件
  NUpload,       // 保留：上传组件
  // 新增离散API
  createDiscreteApi
} from 'naive-ui'

// 创建Naive UI实例
const naive = create({
  components: [
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
    NLayoutSider,  // 新增
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
    NCollapseItem,
    NModal, 
    NAlert, 
    NRadio, 
    NRadioGroup, 
    NText,
    NDataTable,
    NUpload,
    NList,         // 新增
    NListItem,     // 新增
    NBadge,        // 新增
    NScrollbar,    // 新增
  ]
})

// 创建离散API实例（用于全局调用）
const { message, notification, dialog, loadingBar } = createDiscreteApi([
  'message',
  'notification', 
  'dialog',
  'loadingBar'
])

const app = createApp(App)
const pinia = createPinia()

// 全局挂载离散API（可选，便于在模板中使用）
app.config.globalProperties.$message = message
app.config.globalProperties.$notification = notification
app.config.globalProperties.$dialog = dialog
app.config.globalProperties.$loadingBar = loadingBar

app.use(pinia)
app.use(router)
app.use(naive)

app.mount('#app')

// 导出离散API供JS/TS模块使用
export { message, notification, dialog, loadingBar }