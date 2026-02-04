// src/main.js
import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// 导入Bootstrap
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'bootstrap-icons/font/bootstrap-icons.css'

// 导入全局样式
import '@/assets/scss/main.scss'

Vue.config.productionTip = false

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')