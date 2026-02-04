<!-- src/App.vue -->
<template>
  <div id="app">
    <!-- 顶部导航栏 -->
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
      <div class="container">
        <router-link class="navbar-brand" to="/">
          <i class="bi bi-journal-bookmark-fill text-primary me-2"></i>
          <span class="fw-bold">菜谱管理</span>
        </router-link>

        <div class="navbar-nav ml-auto">
          <router-link class="nav-link" to="/" exact-active-class="active">
            首页
          </router-link>
<!--          <router-link class="nav-link" to="/add" active-class="active">-->
<!--            添加菜谱-->
<!--          </router-link>-->
        </div>
      </div>
    </nav>

    <!-- 主要内容 -->
    <main class="main-content">
      <router-view/>
    </main>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  min-height: 100vh;
}

.navbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.main-content {
  min-height: calc(100vh - 56px);
}

.nav-link.active {
  color: #0d6efd !important;
  font-weight: 600;
}
</style>