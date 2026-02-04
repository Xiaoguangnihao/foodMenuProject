<template>
  <div class="home">
    <div class="nav-tabs mb-4">
      <div class="tab-container">
        <router-link to="/" class="tab-item" :class="{ active: $route.path === '/' }">
          <i class="bi bi-journal-text"></i>
          <span>菜谱库</span>
        </router-link>
        <router-link to="/orders" class="tab-item" :class="{ active: $route.path.startsWith('/order') }">
          <i class="bi bi-receipt"></i>
          <span>点餐</span>
          <span v-if="pendingOrderCount > 0" class="badge">{{ pendingOrderCount }}</span>
        </router-link>
      </div>
    </div>
    <!-- 搜索栏 -->
    <div class="search-section mb-4">
      <div class="input-group">
        <input
          type="text"
          class="form-control"
          placeholder="搜索菜谱..."
          v-model="searchKeyword"
          @input="handleSearch"
        >
        <button
          v-if="searchKeyword"
          class="btn btn-outline-secondary"
          type="button"
          @click="clearSearch"
        >
          <i class="bi bi-x"></i>
        </button>
        <button class="btn btn-primary" type="button" @click="search">
          <i class="bi bi-search"></i>
        </button>
      </div>
    </div>

    <!-- 分类筛选 -->
    <div class="category-filter mb-4">
      <div class="category-scroll">
        <button
          v-for="category in categories"
          :key="category"
          class="category-btn"
          :class="{ active: selectedCategory === category }"
          @click="selectCategory(category)"
        >
          {{ category }}
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="sr-only">加载中...</span>
      </div>
      <p class="mt-2 text-muted">正在加载菜谱...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="alert alert-danger rounded-4">
      {{ error }}
    </div>

    <!-- 空状态 -->
    <div v-else-if="filteredRecipes.length === 0" class="text-center py-5">
      <div class="empty-icon mb-3">
        <i class="bi bi-journal-x" style="font-size: 4rem; color: #dee2e6;"></i>
      </div>
      <h5 class="text-muted">还没有菜谱</h5>
      <p class="text-muted mb-4">点击下方按钮添加第一个菜谱吧</p>
      <router-link to="/add" class="btn btn-primary rounded-pill">
        <i class="bi bi-plus-circle me-2"></i>添加菜谱
      </router-link>
    </div>

    <!-- 菜谱列表 - 一行2个 -->
    <div v-else class="recipe-grid">
      <div
        v-for="recipe in filteredRecipes"
        :key="recipe.id"
        class="recipe-item"
        @click="viewRecipe(recipe.id)"
      >
        <div class="recipe-card">
          <!-- 图片区域 -->
          <div v-if="recipe.image_url" class="recipe-image-wrapper">
            <img
              :src="getImageUrl(recipe.image_url)"
              class="recipe-image"
              :alt="recipe.name"
              loading="lazy"
            >
          </div>
          <div v-else class="recipe-image-wrapper no-image">
            <i class="bi bi-image text-muted" style="font-size: 2.5rem;"></i>
          </div>

          <!-- 内容区域 -->
          <div class="recipe-content">
            <h5 class="recipe-title">{{ recipe.name }}</h5>

            <div class="recipe-meta">
              <span class="badge bg-soft-primary text-primary">
                {{ recipe.category }}
              </span>
              <span class="text-muted small">
                <i class="bi bi-clock me-1"></i>{{ recipe.prep_time }}分钟
              </span>
            </div>

            <div v-if="parsedTags(recipe.tags).length > 0" class="recipe-tags">
              <span
                v-for="tag in parsedTags(recipe.tags).slice(0, 2)"
                :key="tag"
                class="tag-item"
              >
                {{ tag }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加按钮 -->
    <div class="add-button">
      <router-link to="/add" class="btn btn-primary btn-lg rounded-circle shadow-lg">
        <i class="bi bi-plus" style="font-size: 1.5rem;"></i>
      </router-link>
    </div>
  </div>
</template>

<script>
import api from '@/api';

export default {
  name: 'Home',

  data() {
    return {
      searchKeyword: '',
      selectedCategory: '全部',
      categories: ['全部', '家常菜', '甜品', '主食', '汤类'],
      recipes: [],
      loading: false,
      error: null,
      pendingOrderCount: 0
    }
  },

  computed: {
    filteredRecipes() {
      let filtered = this.recipes

      if (this.selectedCategory !== '全部') {
        filtered = filtered.filter(recipe => recipe.category === this.selectedCategory)
      }

      if (this.searchKeyword.trim()) {
        const keyword = this.searchKeyword.toLowerCase().trim()
        filtered = filtered.filter(recipe =>
          recipe.name?.toLowerCase().includes(keyword) ||
          recipe.category?.toLowerCase().includes(keyword) ||
          (recipe.tags || []).some(tag => {
            const tagStr = typeof tag === 'string' ? tag : String(tag)
            return tagStr.toLowerCase().includes(keyword)
          })
        )
      }

      return filtered
    }
  },

  mounted() {
    this.fetchRecipes(),
    this.fetchPendingOrders()
  },

  methods: {
    async fetchRecipes() {
      this.loading = true
      this.error = null

      try {
        const response = await api.recipes.getAllRecipes()

        if (response && response.data) {
          this.recipes = response.data
        } else if (Array.isArray(response)) {
          this.recipes = response
        } else {
          this.recipes = []
        }
      } catch (err) {
        console.error('获取菜谱失败:', err)
        this.error = err.message || '获取菜谱失败，请检查网络连接'

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

    getImageUrl(imageUrl) {
      if (!imageUrl) return ''
      if (imageUrl.startsWith('http')) return imageUrl
      return `${api.baseURL}${imageUrl.startsWith('/') ? '' : '/'}${imageUrl}`
    },

    parsedTags(tags) {
      if (!tags) return []
      if (Array.isArray(tags)) return tags
      if (typeof tags === 'string') {
        return tags.split(',').map(t => t.trim()).filter(t => t)
      }
      return []
    },

    viewRecipe(id) {
      this.$router.push(`/recipe/${id}`)
    },

    selectCategory(category) {
      this.selectedCategory = category
    },
    async fetchPendingOrders() {
      try {
        const response = await api.orders.getAllOrders({ status: 'pending' });
        const orders = response.data || response || [];
        this.pendingOrderCount = orders.length;
      } catch (err) {
        console.error('获取待处理订单失败:', err);
      }
    },
    handleSearch() {
      // 实时搜索
    },

    clearSearch() {
      this.searchKeyword = ''
    },

    search() {
      // 搜索按钮点击
    }
  }
}
</script>

<style scoped lang="scss">
.home {
  min-height: calc(100vh - 200px);
  padding: 16px;
  background-color: #f5f5f7;
}

// 搜索栏样式
.search-section {
  padding: 0 4px;

  .input-group {
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    background: white;

    .form-control {
      border: none;
      padding: 14px 18px;
      font-size: 16px;

      &:focus {
        box-shadow: none;
      }
    }

    .btn {
      border: none;
      padding: 14px 18px;

      &.btn-outline-secondary {
        color: #6c757d;
        background: transparent;
      }

      &.btn-primary {
        padding: 14px 24px;
      }
    }
  }
}

// 分类筛选
.category-filter {
  padding: 0 4px;

  .category-scroll {
    display: flex;
    overflow-x: auto;
    gap: 10px;
    padding: 4px 0 12px;
    -webkit-overflow-scrolling: touch;

    &::-webkit-scrollbar {
      display: none;
    }
  }

  .category-btn {
    white-space: nowrap;
    padding: 10px 20px;
    border-radius: 24px;
    border: none;
    background: white;
    color: #666;
    font-weight: 500;
    font-size: 14px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

    &.active {
      background: #0d6efd;
      color: white;
      box-shadow: 0 4px 12px rgba(13, 110, 253, 0.3);
    }

    &:active {
      transform: scale(0.95);
    }
  }
}

// 菜谱网格布局 - 一行2个
.recipe-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 0 4px;
}

.recipe-item {
  width: 100%;
}

// 菜谱卡片 - 圆角设计
.recipe-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  height: 100%;
  display: flex;
  flex-direction: column;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }

  &:active {
    transform: scale(0.98);
  }
}

// 图片区域
.recipe-image-wrapper {
  width: 100%;
  aspect-ratio: 4 / 3;
  overflow: hidden;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;

  &.no-image {
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  }
}

.recipe-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.recipe-card:hover .recipe-image {
  transform: scale(1.05);
}

// 内容区域
.recipe-content {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.recipe-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 10px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 42px;
}

.recipe-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;

  .badge {
    font-size: 12px;
    padding: 6px 10px;
    border-radius: 12px;
    font-weight: 500;
  }

  .bg-soft-primary {
    background-color: rgba(13, 110, 253, 0.1) !important;
  }
}

.recipe-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: auto;
}

.tag-item {
  font-size: 11px;
  padding: 4px 10px;
  background: #f0f0f0;
  color: #666;
  border-radius: 10px;
  font-weight: 500;
}

// 添加按钮
.add-button {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;

  .btn {
    width: 56px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;

    &:hover {
      transform: scale(1.1);
    }
  }
}

// 空状态
.empty-icon {
  font-size: 4rem;
  color: #dee2e6;
}

// 响应式适配
@media (max-width: 375px) {
  .home {
    padding: 12px;
  }

  .recipe-grid {
    gap: 10px;
  }

  .recipe-content {
    padding: 12px;
  }

  .recipe-title {
    font-size: 14px;
  }
}

@media (min-width: 768px) {
  .home {
    padding: 24px;
    max-width: 1200px;
    margin: 0 auto;
  }

  .recipe-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }

  .recipe-title {
    font-size: 16px;
  }
}

@media (min-width: 1024px) {
  .recipe-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
.nav-tabs {
  padding: 0 4px;

  .tab-container {
    display: flex;
    background: white;
    border-radius: 16px;
    padding: 4px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  }

  .tab-item {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 12px;
    border-radius: 12px;
    color: #666;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.3s;
    position: relative;

    i {
      font-size: 18px;
    }

    .badge {
      position: absolute;
      top: 8px;
      right: 8px;
      background: #dc3545;
      color: white;
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 10px;
      min-width: 18px;
      text-align: center;
    }

    &.active {
      background: #0d6efd;
      color: white;
    }
  }
}
</style>