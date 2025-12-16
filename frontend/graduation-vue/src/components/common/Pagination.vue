<template>
  <div class="pagination">
    <n-pagination 
      v-model:page="internalCurrentPage" 
      :page-count="totalPages" 
      :page-size="pageSize"
      show-size-picker
      :page-sizes="[12, 24, 36, 48]"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { NPagination } from 'naive-ui'

// 定义 props
const props = defineProps({
  currentPage: {
    type: Number,
    default: 1
  },
  totalPages: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 12
  }
})

// 定义 emits
const emit = defineEmits(['update:currentPage', 'update:pageSize'])

// 内部状态
const internalCurrentPage = ref(props.currentPage)
const internalPageSize = ref(props.pageSize)

// 监听内部状态变化并触发事件
watch(internalCurrentPage, (newValue) => {
  emit('update:currentPage', newValue)
})

watch(internalPageSize, (newValue) => {
  emit('update:pageSize', newValue)
})

// 监听 props 变化更新内部状态
watch(() => props.currentPage, (newValue) => {
  internalCurrentPage.value = newValue
})

watch(() => props.pageSize, (newValue) => {
  internalPageSize.value = newValue
})
</script>

<style scoped>
.pagination {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}
</style>