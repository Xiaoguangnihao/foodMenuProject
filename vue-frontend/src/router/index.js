// src/router/index.js
import Vue from 'vue'
import VueRouter from 'vue-router'
import OrderList from '@/views/orders/OrderList.vue';
import OrderDetail from '@/views/orders/OrderDetail.vue';

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/add',
    name: 'AddRecipe',
    component: () => import('@/views/Recipe/AddRecipe.vue')
  },
  {
    path: '/recipe/:id',
    name: 'RecipeDetail',
    component: () => import('@/views/Recipe/RecipeDetail.vue')
  },
  {
    path: '*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  },
  {
    path: '/orders',
    name: 'OrderList',
    component: OrderList
  },
  {
    path: '/orders/:id',
    name: 'OrderDetail',
    component: OrderDetail
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router