<!-- src/views/NotFound.vue -->
<template>
  <div class="not-found">
    <div class="text-center py-5">
      <div class="error-icon mb-4">
        <i class="bi bi-emoji-frown" style="font-size: 4rem; color: #6c757d;"></i>
      </div>
      <h2 class="mb-3">页面未找到</h2>
      <p class="text-muted mb-4">您访问的页面不存在或已被移除</p>
      <router-link to="/" class="btn btn-primary">
        <i class="bi bi-house-door me-2"></i>返回首页
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
}
</script>