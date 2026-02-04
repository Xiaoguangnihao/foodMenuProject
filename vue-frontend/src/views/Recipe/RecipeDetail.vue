<!-- src/views/RecipeDetail.vue -->
<template>
  <div class="recipe-detail">
    <div class="container">
      <button class="btn btn-light mb-4" @click="$router.back()">
        <i class="bi bi-arrow-left me-2"></i>返回
      </button>

      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="sr-only">加载中...</span>
        </div>
        <p class="mt-2 text-muted">正在加载菜谱详情...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="alert alert-danger">
        {{ error }}
      </div>

      <!-- 菜谱内容 -->
      <div v-else-if="recipe">
        <!-- 图片展示 -->
        <div v-if="recipe.image_url" class="recipe-image mb-4">
          <img :src="getImageUrl(recipe.image_url)" :alt="recipe.name" class="img-fluid rounded shadow-sm">
        </div>

        <h2 class="mb-3">{{ recipe.name }}</h2>

        <div class="recipe-info mb-4">
          <span class="badge bg-primary me-2">{{ recipe.category }}</span>
          <span class="text-muted me-3">
            <i class="bi bi-clock me-1"></i>{{ recipe.prep_time }}分钟
          </span>
          <span v-if="recipe.created_at" class="text-muted">
            <i class="bi bi-calendar me-1"></i>{{ formatDate(recipe.created_at) }}
          </span>
        </div>

        <div class="recipe-content">
          <!-- 食材 -->
          <div class="mb-4">
            <h5 class="mb-3">
              <i class="bi bi-basket me-2"></i>食材
            </h5>
            <ul v-if="parsedIngredients.length > 0" class="list-group">
              <li
                v-for="(ingredient, index) in parsedIngredients"
                :key="index"
                class="list-group-item"
              >
                {{ ingredient }}
              </li>
            </ul>
            <p v-else class="text-muted">暂无食材信息</p>
          </div>

          <!-- 步骤 -->
          <div class="mb-4">
            <h5 class="mb-3">
              <i class="bi bi-list-ol me-2"></i>制作步骤
            </h5>
            <ol v-if="parsedSteps.length > 0" class="list-group list-group-numbered">
              <li
                v-for="(step, index) in parsedSteps"
                :key="index"
                class="list-group-item"
              >
                {{ step }}
              </li>
            </ol>
            <p v-else class="text-muted">暂无步骤信息</p>
          </div>

          <!-- 标签 -->
          <div v-if="parsedTags.length > 0">
            <h5 class="mb-3">
              <i class="bi bi-tags me-2"></i>标签
            </h5>
            <div class="d-flex flex-wrap gap-2">
              <span
                v-for="tag in parsedTags"
                :key="tag"
                class="badge bg-light text-dark border"
              >
                {{ tag }}
              </span>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="mt-4 pt-4 border-top d-flex gap-2">
          <router-link :to="`/edit/${recipe.id}`" class="btn btn-outline-primary">
            <i class="bi bi-pencil me-2"></i>编辑
          </router-link>
          <button class="btn btn-outline-danger" @click="confirmDelete">
            <i class="bi bi-trash me-2"></i>删除
          </button>
        </div>
      </div>

      <!-- 不存在 -->
      <div v-else class="text-center py-5">
        <div class="mb-3">
          <i class="bi bi-journal-x" style="font-size: 4rem; color: #dee2e6;"></i>
        </div>
        <h5 class="text-muted">菜谱不存在</h5>
        <p class="text-muted">该菜谱可能已被删除或您没有访问权限</p>
        <router-link to="/" class="btn btn-primary">返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script>
// 导入 API 模块
import api from '@/api';

export default {
  name: 'RecipeDetail',

  data() {
    return {
      recipe: null,
      loading: false,
      error: null
    }
  },

  computed: {
    // 解析食材（支持字符串或数组）
    parsedIngredients() {
      if (!this.recipe?.ingredients) return []

      // 如果是数组直接返回
      if (Array.isArray(this.recipe.ingredients)) {
        return this.recipe.ingredients.filter(item => item && item.trim())
      }

      // 如果是字符串，按行分割
      if (typeof this.recipe.ingredients === 'string') {
        return this.recipe.ingredients
          .split('\n')
          .map(line => line.trim())
          .filter(line => line.length > 0)
      }

      return []
    },

    // 解析步骤（支持字符串或数组）
    parsedSteps() {
      if (!this.recipe?.steps) return []

      // 如果是数组直接返回
      if (Array.isArray(this.recipe.steps)) {
        return this.recipe.steps.filter(item => item && item.trim())
      }

      // 如果是字符串，按行分割
      if (typeof this.recipe.steps === 'string') {
        return this.recipe.steps
          .split('\n')
          .map(line => line.trim())
          .filter(line => line.length > 0)
      }

      return []
    },

    // 解析标签（支持字符串或数组）
    parsedTags() {
      if (!this.recipe?.tags) return []

      // 如果是数组直接返回
      if (Array.isArray(this.recipe.tags)) {
        return this.recipe.tags
      }

      // 如果是字符串，按逗号分割
      if (typeof this.recipe.tags === 'string') {
        return this.recipe.tags
          .split(',')
          .map(tag => tag.trim())
          .filter(tag => tag.length > 0)
      }

      return []
    }
  },

  mounted() {
    this.fetchRecipe()
  },

  methods: {
    // 获取菜谱详情
    async fetchRecipe() {
      const id = this.$route.params.id
      if (!id) {
        this.error = '无效的菜谱ID'
        return
      }

      this.loading = true
      this.error = null

      try {
        const response = await api.recipes.getRecipeById(id)

        // 处理不同返回格式
        if (response && response.data) {
          this.recipe = response.data
        } else if (response && response.id) {
          this.recipe = response
        } else {
          this.recipe = null
        }
      } catch (err) {
        console.error('获取菜谱详情失败:', err)
        this.error = err.message || '获取菜谱详情失败，请稍后重试'

        // 显示通知
        if (this.$notify) {
          this.$notify({
            title: '错误',
            message: this.error,
            type: 'error'
          })
        }
      } finally {
        this.loading = false
      }
    },

    // 获取完整图片 URL
    getImageUrl(imageUrl) {
      if (!imageUrl) return ''

      if (imageUrl.startsWith('http')) {
        return imageUrl
      }

      return `${api.baseURL}${imageUrl.startsWith('/') ? '' : '/'}${imageUrl}`
    },

    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return ''

      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('zh-CN', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })
      } catch {
        return dateString
      }
    },

    // 确认删除
    confirmDelete() {
      if (!confirm('确定要删除这个菜谱吗？此操作不可恢复。')) {
        return
      }

      this.deleteRecipe()
    },

    // 删除菜谱
    async deleteRecipe() {
      if (!this.recipe?.id) return

      try {
        await api.recipes.deleteRecipe(this.recipe.id)

        // 显示成功消息
        if (this.$notify) {
          this.$notify({
            title: '成功',
            message: '菜谱已删除',
            type: 'success'
          })
        }

        // 返回首页
        this.$router.push('/')
      } catch (err) {
        console.error('删除失败:', err)

        if (this.$notify) {
          this.$notify({
            title: '错误',
            message: err.message || '删除失败，请稍后重试',
            type: 'error'
          })
        } else {
          alert('删除失败: ' + (err.message || '请稍后重试'))
        }
      }
    }
  }
}
</script>

<style scoped lang="scss">
.recipe-detail {
  min-height: calc(100vh - 200px);
  padding: 20px 0;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 15px;
}

.recipe-image {
  width: 100%;
  max-height: 400px;
  overflow: hidden;
  border-radius: 8px;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.recipe-info {
  .badge {
    font-size: 1rem;
    padding: 8px 12px;
  }
}

.list-group-item {
  border: 1px solid #e9ecef;
  padding: 12px 15px;

  &:hover {
    background-color: #f8f9fa;
  }
}

.recipe-content {
  h5 {
    color: #333;
    font-weight: 600;

    i {
      color: #0d6efd;
    }
  }
}

@media (max-width: 768px) {
  .recipe-detail {
    padding: 10px 0;
  }

  .container {
    padding: 0 10px;
  }

  .recipe-image {
    max-height: 250px;
  }
}
</style>