<template>
  <div class="home-page">
    <!-- Banner轮播区 -->
    <n-carousel 
      autoplay 
      interval="5000" 
      class="banner-carousel"
      indicator-placement="bottom"
    >
      <div v-for="banner in banners" :key="banner.id" class="banner-item">
        <div class="banner-info">
          <h2>{{ banner.title }}</h2>
          <p>{{ banner.desc }}</p>
          <n-button 
            type="primary" 
            @click="handleBannerClick(banner)"
          >
            {{ banner.btnText }}
          </n-button>
        </div>
      </div>
    </n-carousel>

    <!-- 个性化推荐区 -->
    <section class="recommendation-section">
      <div class="section-header">
        <h2>为你推荐</h2>
        <n-button text @click="seeMore('recommendation')">查看更多</n-button>
      </div>
      
      <div class="recommendation-cards">
        <JobCard 
          v-for="item in recommendedJobs" 
          :key="item.id" 
          :job="item"
          @click="$router.push('/jobs')"
        />
      </div>
    </section>

    <!-- 其他部分内容... -->
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NCarousel, NButton } from 'naive-ui'
import JobCard from '@/components/common/JobCard.vue'

const router = useRouter()

// 模拟数据
const banners = ref([
  {
    id: 1,
    title: '2024届秋招专场',
    desc: '名企校招信息实时更新，把握最佳求职时机',
    btnText: '立即查看',
    link: '/jobs'
  },
  // ... 其他banner数据
])

const recommendedJobs = ref([
  {
    id: 1,
    title: '前端开发工程师',
    company: '字节跳动',
    companyLogo: 'https://picsum.photos/id/1/60/60',
    salary: '15k-25k',
    location: '北京',
    type: '校招',
    tags: ['JavaScript', 'Vue', 'React']
  },
  // ... 其他推荐职位
])

const handleBannerClick = (banner) => {
  router.push(banner.link)
}

const seeMore = (type) => {
  switch (type) {
    case 'recommendation':
      router.push('/jobs?type=recommended')
      break
    // ... 其他情况
  }
}
</script>

<style scoped>
/* 首页特定样式 */
</style>