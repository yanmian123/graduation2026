<template>
  <div>
    <h1>Message from Django:</h1>
    <p>{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

const message = ref('');

onMounted(async () => {
  try {
    // 向 Django 后端发送请求
    const response = await axios.get('http://127.0.0.1:8000/api/hello/');
    message.value = response.data.message;
  } catch (error) {
    console.error('Error fetching data:', error);
    message.value = 'Failed to load message.';
  }
});
</script>