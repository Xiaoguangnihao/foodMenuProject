<!-- src/views/orders/AddOrderItem.vue -->
<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content rounded-4">
      <div class="modal-header">
        <h5 class="modal-title">添加菜品</h5>
        <button type="button" class="btn-close" @click="$emit('close')"></button>
      </div>

      <div class="modal-body">
        <!-- 搜索菜谱 -->
        <div class="search-box mb-3">
          <input
            type="text"
            class="form-control rounded-pill"
            placeholder="搜索菜谱..."
            v-model="searchKeyword"
            @input="searchRecipes"
          >
        </div>

        <!-- 菜谱列表 -->
        <div class="recipe-list">
          <div v-if="loading" class="text-center py-3">
            <div class="spinner-border spinner-border-sm text-primary"></div>
          </div>

          <div v-else-if="recipes.length === 0" class="text-center py-3 text-muted">
            没有找到菜谱
          </div>

          <div
            v-for="recipe in filteredRecipes"
            :key="recipe.id"
            class="recipe-option"
            :class="{ selected: selectedRecipe?.id === recipe.id }"
            @click="selectRecipe(recipe)"
          >
            <div class="d-flex align-items-center gap-3">
              <!-- 菜谱图片 -->
              <div class="recipe-image">
                <img
                  v-if="recipe.image_url"
                  :src="getImageUrl(recipe.image_url)"
                  :alt="recipe.name"
                >
                <div v-else class="no-image">
                  <i class="bi bi-image text-muted"></i>
                </div>
              </div>

              <div class="flex-fill">
                <h6 class="mb-0">{{ recipe.name }}</h6>
                <small class="text-muted">{{ recipe.category }}</small>
              </div>
            </div>
          </div>
        </div>

        <!-- 数量选择 -->
        <div v-if="selectedRecipe" class="quantity-section mt-4">
          <div class="d-flex align-items-center gap-3 mb-3">
            <!-- 选中菜品的图片预览 -->
            <div class="selected-image">
              <img
                v-if="selectedRecipe.image_url"
                :src="getImageUrl(selectedRecipe.image_url)"
                :alt="selectedRecipe.name"
              >
              <div v-else class="no-image">
                <i class="bi bi-image text-muted"></i>
              </div>
            </div>
            <div>
              <h6 class="mb-0">{{ selectedRecipe.name }}</h6>
              <small class="text-muted">{{ selectedRecipe.category }}</small>
            </div>
          </div>

          <label class="form-label">数量</label>
          <div class="d-flex align-items-center gap-3">
            <button
              class="btn btn-outline-secondary rounded-circle"
              @click="quantity > 1 && quantity--"
              :disabled="adding"
            >
              <i class="bi bi-dash"></i>
            </button>
            <span class="quantity-display">{{ quantity }}</span>
            <button
              class="btn btn-outline-secondary rounded-circle"
              @click="quantity++"
              :disabled="adding"
            >
              <i class="bi bi-plus"></i>
            </button>
          </div>
        </div>

        <!-- 错误提示 -->
        <div v-if="errorMessage" class="alert alert-danger rounded-3 mt-3 mb-0">
          <small>{{ errorMessage }}</small>
        </div>

        <!-- 按钮 -->
        <div class="d-flex gap-2 mt-4">
          <button
            class="btn btn-light flex-fill rounded-3"
            @click="$emit('close')"
            :disabled="adding"
          >
            取消
          </button>
          <button
            class="btn btn-primary flex-fill rounded-3"
            :disabled="!selectedRecipe || adding"
            @click="addItem"
          >
            <span v-if="adding" class="spinner-border spinner-border-sm me-2"></span>
            添加 {{ quantity }} 份
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/api';

export default {
  name: 'AddOrderItem',

  props: {
    orderId: {
      type: [String, Number],
      required: true
    }
  },

  data() {
    return {
      recipes: [],
      loading: false,
      searchKeyword: '',
      selectedRecipe: null,
      quantity: 1,
      adding: false,
      errorMessage: '',
      searchTimeout: null
    }
  },

  computed: {
    filteredRecipes() {
      if (!this.searchKeyword.trim()) {
        return this.recipes;
      }

      const keyword = this.searchKeyword.toLowerCase().trim();
      return this.recipes.filter(recipe =>
        recipe.name?.toLowerCase().includes(keyword) ||
        recipe.category?.toLowerCase().includes(keyword)
      );
    }
  },

  mounted() {
    this.fetchRecipes();
  },

  methods: {
    async fetchRecipes() {
      this.loading = true;
      this.errorMessage = '';

      try {
        const response = await api.recipes.getAllRecipes();
        console.log('Recipes response:', response);

        if (response && response.data) {
          this.recipes = Array.isArray(response.data) ? response.data : [];
        } else if (Array.isArray(response)) {
          this.recipes = response;
        } else {
          this.recipes = [];
        }
      } catch (err) {
        console.error('获取菜谱失败:', err);
        this.errorMessage = '获取菜谱失败: ' + (err.message || '请检查网络');
      } finally {
        this.loading = false;
      }
    },

    // 获取图片URL
    getImageUrl(imageUrl) {
      if (!imageUrl) return '';
      if (imageUrl.startsWith('http')) return imageUrl;
      return `${api.baseURL}${imageUrl.startsWith('/') ? '' : '/'}${imageUrl}`;
    },

    searchRecipes() {
      clearTimeout(this.searchTimeout);
      this.searchTimeout = setTimeout(() => {
        // 本地搜索
      }, 300);
    },

    selectRecipe(recipe) {
      this.selectedRecipe = recipe;
      this.quantity = 1;
      this.errorMessage = '';
    },

    async addItem() {
      if (!this.selectedRecipe) {
        this.errorMessage = '请先选择一个菜品';
        return;
      }

      if (!this.orderId) {
        this.errorMessage = '订单ID无效';
        return;
      }

      this.adding = true;
      this.errorMessage = '';

      try {
        const itemData = {
          recipe_id: String(this.selectedRecipe.id),
          recipe_name: String(this.selectedRecipe.name),
          quantity: Number(this.quantity),
          unit_price: Number(this.selectedRecipe.price || 0)
        };

        console.log('Adding item to order:', this.orderId, itemData);

        if (!api.orders || !api.orders.addOrderItem) {
          throw new Error('API 方法不存在，请检查 api/index.js 配置');
        }

        const response = await api.orders.addOrderItem(this.orderId, itemData);

        console.log('Add item response:', response);

        if (response && (response.success || response.id || response.data)) {
          this.$emit('added');
        } else {
          throw new Error(response?.message || '添加失败');
        }
      } catch (err) {
        console.error('添加菜品失败:', err);

        let errorMsg = '添加失败: ';

        if (err.status === 404) {
          errorMsg += '接口不存在，请检查后端是否实现了 POST /api/orders/{id}/items';
        } else if (err.status === 400) {
          errorMsg += err.message || '请求参数错误';
        } else if (err.status === 422) {
          errorMsg += '数据验证失败: ' + (err.data?.detail || err.message);
        } else if (err.message) {
          errorMsg += err.message;
        } else {
          errorMsg += '请稍后重试';
        }

        this.errorMessage = errorMsg;
      } finally {
        this.adding = false;
      }
    }
  }
};
</script>

<style scoped lang="scss">
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 3000;

  @media (min-width: 576px) {
    align-items: center;
  }
}

.modal-content {
  background: white;
  width: 100%;
  max-width: 500px;
  max-height: 80vh;
  border-radius: 24px 24px 0 0;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;

  @media (min-width: 576px) {
    border-radius: 24px;
    max-height: 90vh;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.modal-header {
  padding: 20px 20px 0;
  border: none;
  flex-shrink: 0;

  .modal-title {
    font-weight: 600;
  }
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.search-box {
  position: sticky;
  top: 0;
  background: white;
  z-index: 10;
  padding-bottom: 8px;

  input {
    padding: 12px 20px;
    border: 1px solid #e9ecef;

    &:focus {
      box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
      border-color: #0d6efd;
    }
  }
}

.recipe-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 320px;
  overflow-y: auto;
  padding-right: 4px;

  &::-webkit-scrollbar {
    width: 4px;
  }

  &::-webkit-scrollbar-thumb {
    background: #dee2e6;
    border-radius: 4px;
  }
}

.recipe-option {
  padding: 12px;
  border-radius: 16px;
  border: 2px solid transparent;
  background: #f8f9fa;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #e9ecef;
    transform: translateX(4px);
  }

  &.selected {
    border-color: #0d6efd;
    background: #f8f9ff;
  }

  .recipe-image {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    overflow: hidden;
    flex-shrink: 0;
    background: #e9ecef;
    display: flex;
    align-items: center;
    justify-content: center;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .no-image {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;

      i {
        font-size: 24px;
      }
    }
  }

  h6 {
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 4px;
  }
}

.quantity-section {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 16px;

  .selected-image {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    overflow: hidden;
    flex-shrink: 0;
    background: #e9ecef;
    display: flex;
    align-items: center;
    justify-content: center;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .no-image {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;

      i {
        font-size: 24px;
      }
    }
  }

  h6 {
    font-weight: 600;
    color: #1a1a1a;
  }

  .quantity-display {
    font-size: 20px;
    font-weight: 700;
    min-width: 40px;
    text-align: center;
  }

  .btn {
    width: 40px;
    height: 40px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;

    &:disabled {
      opacity: 0.5;
    }
  }
}

.alert {
  font-size: 13px;
  padding: 10px 12px;
}
</style>