// src/store/index.js
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    recipes: [],
    loading: false,
    error: null
  },
  mutations: {
    SET_RECIPES(state, recipes) {
      state.recipes = recipes
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    ADD_RECIPE(state, recipe) {
      state.recipes.unshift(recipe)
    }
  },
  actions: {
    async fetchRecipes({ commit }) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)

      try {
        // 模拟API调用
        setTimeout(() => {
          const recipes = [
            {
              id: '1',
              name: '番茄炒蛋',
              category: '家常菜',
              prep_time: 15,
              ingredients: ['鸡蛋 2个', '番茄 1个', '盐 适量'],
              steps: ['准备食材', '热锅加油', '先炒鸡蛋', '加入番茄翻炒'],
              tags: ['简单', '快捷'],
              image_url: null,
              created_at: '2024-01-15 10:30:00',
              updated_at: '2024-01-15 10:30:00'
            },
            {
              id: '2',
              name: '红烧肉',
              category: '家常菜',
              prep_time: 60,
              ingredients: ['五花肉 500g', '冰糖 50g', '生抽 适量', '老抽 适量'],
              steps: ['五花肉切块', '焯水去腥', '炒糖色', '炖煮1小时'],
              tags: ['传统', '经典'],
              image_url: null,
              created_at: '2024-01-16 10:30:00',
              updated_at: '2024-01-16 10:30:00'
            }
          ]
          commit('SET_RECIPES', recipes)
          commit('SET_LOADING', false)
        }, 1000)
      } catch (error) {
        commit('SET_ERROR', error.message)
        commit('SET_LOADING', false)
      }
    },

    addRecipe({ commit }, recipe) {
      commit('ADD_RECIPE', recipe)
    }
  },
  getters: {
    getRecipeById: (state) => (id) => {
      return state.recipes.find(recipe => recipe.id === id)
    },

    getRecipesByCategory: (state) => (category) => {
      if (category === '全部') return state.recipes
      return state.recipes.filter(recipe => recipe.category === category)
    }
  }
})