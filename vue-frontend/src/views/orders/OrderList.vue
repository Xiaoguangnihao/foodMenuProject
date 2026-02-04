<!-- src/views/orders/OrderList.vue -->
<template>
  <div class="order-list">
    <div class="header-section mb-4">
      <div class="d-flex justify-content-between align-items-center">
        <h4 class="mb-0">点餐管理</h4>
        <button class="btn btn-primary rounded-pill" @click="showAddModal = true">
          <i class="bi bi-plus-lg me-2"></i>新建点餐
        </button>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="search-section mb-4">
      <div class="input-group">
        <input
          type="text"
          class="form-control"
          placeholder="搜索用餐名称或位置..."
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

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="sr-only">加载中...</span>
      </div>
      <p class="mt-2 text-muted">正在加载点餐...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="alert alert-danger rounded-4">
      <div class="d-flex align-items-start">
        <i class="bi bi-exclamation-triangle-fill me-2 mt-1"></i>
        <div>
          <strong>加载失败</strong>
          <p class="mb-0 small">{{ error }}</p>
          <button class="btn btn-sm btn-outline-danger mt-2" @click="fetchOrders">
            <i class="bi bi-arrow-clockwise me-1"></i>重试
          </button>
        </div>
      </div>
    </div>

    <!-- API 未就绪提示 -->
    <div v-else-if="!apiReady" class="text-center py-5">
      <div class="empty-icon mb-3">
        <i class="bi bi-server" style="font-size: 4rem; color: #ffc107;"></i>
      </div>
      <h5 class="text-muted">后端服务未就绪</h5>
      <p class="text-muted mb-3">点餐功能需要后端 API 支持</p>
      <div class="alert alert-warning mx-3 rounded-3">
        <small>
          <strong>提示：</strong>请确保后端服务已启动，并且已实现以下接口：<br>
          <code>GET /api/orders</code><br>
          <code>POST /api/orders</code>
        </small>
      </div>
      <button class="btn btn-primary rounded-pill" @click="fetchOrders">
        <i class="bi bi-arrow-clockwise me-2"></i>重新检测
      </button>
    </div>

    <!-- 空状态 -->
    <div v-else-if="filteredOrders.length === 0" class="text-center py-5">
      <div class="empty-icon mb-3">
        <i class="bi bi-receipt" style="font-size: 4rem; color: #dee2e6;"></i>
      </div>
      <h5 class="text-muted">还没有点餐</h5>
      <p class="text-muted mb-4">点击上方按钮创建第一个点餐</p>
    </div>

    <!-- 点餐列表 -->
    <div v-else class="order-grid">
      <div
        v-for="order in filteredOrders"
        :key="order.id"
        class="order-item"
        @click="viewOrder(order.id)"
      >
        <div class="order-card">
          <div class="order-header">
            <div class="d-flex justify-content-between align-items-start">
              <div class="flex-fill">
                <h6 class="order-name">{{ order.customer_name || '未命名' }}</h6>
                <p class="order-location mb-0">
                  <i class="bi bi-geo-alt me-1"></i>{{ order.table_number || '未指定位置' }}
                </p>
              </div>
              <span class="order-time">{{ formatTime(order.created_at) }}</span>
            </div>
          </div>

          <div class="order-body">
            <div class="info-row">
              <i class="bi bi-people"></i>
              <span>{{ order.people_count || '-' }}人用餐</span>
            </div>
            <div class="info-row">
              <i class="bi bi-clock"></i>
              <span>用餐时间: {{ formatDiningTime(order.dining_time) }}</span>
            </div>
            <div v-if="order.remark" class="info-row">
              <i class="bi bi-journal-text"></i>
              <span class="text-truncate">{{ order.remark }}</span>
            </div>
          </div>

          <div class="order-footer">
            <span class="item-count">
              <i class="bi bi-menu-button-wide me-1"></i>{{ order.item_count || 0 }} 道菜
            </span>
            <i class="bi bi-chevron-right text-muted"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建点餐弹窗 -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content rounded-4">
        <div class="modal-header">
          <h5 class="modal-title">新建点餐</h5>
          <button type="button" class="btn-close" @click="closeModal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="createOrder">
            <div class="mb-3">
              <label class="form-label">用餐名称</label>
              <input
                type="text"
                class="form-control rounded-3"
                v-model="newOrder.customer_name"
                placeholder="例如：家庭聚餐、朋友聚会"
              >
            </div>
            <div class="mb-3">
              <label class="form-label">位置</label>
              <input
                type="text"
                class="form-control rounded-3"
                v-model="newOrder.table_number"
                placeholder="例如：大厅A1、包厢B2"
              >
            </div>
            <div class="mb-3">
              <label class="form-label">用餐人数</label>
              <input
                type="number"
                class="form-control rounded-3"
                v-model.number="newOrder.people_count"
                min="1"
                placeholder="2"
              >
            </div>
            <div class="mb-3">
              <label class="form-label">用餐时间</label>
              <input
                type="datetime-local"
                class="form-control rounded-3"
                v-model="newOrder.dining_time"
              >
            </div>
            <div class="mb-3">
              <label class="form-label">备注</label>
              <textarea
                class="form-control rounded-3"
                v-model="newOrder.remark"
                rows="2"
                placeholder="特殊要求..."
              ></textarea>
            </div>
            <div class="d-flex gap-2">
              <button type="button" class="btn btn-light flex-fill rounded-3" @click="closeModal">取消</button>
              <button type="submit" class="btn btn-primary flex-fill rounded-3" :disabled="creating">
                <span v-if="creating" class="spinner-border spinner-border-sm me-2"></span>
                创建
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import api from '@/api';

export default {
  name: 'OrderList',

  data() {
    return {
      orders: [],
      loading: false,
      error: null,
      apiReady: true,
      searchKeyword: '',
      showAddModal: false,
      creating: false,
      showDebug: false,
      debugInfo: '',
      newOrder: {
        customer_name: '',
        table_number: '',
        people_count: 2,
        dining_time: '',
        remark: ''
      }
    }
  },

  computed: {
    apiBaseUrl() {
      return api.baseURL || 'unknown';
    },

    filteredOrders() {
      let filtered = this.orders;

      // 按关键词搜索（用餐名称或位置）
      if (this.searchKeyword.trim()) {
        const keyword = this.searchKeyword.toLowerCase().trim();
        filtered = filtered.filter(order =>
          order.customer_name?.toLowerCase().includes(keyword) ||
          order.table_number?.toLowerCase().includes(keyword)
        );
      }

      return filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    }
  },

  mounted() {
    this.fetchOrders();
    if (process.env.NODE_ENV === 'development') {
      this.showDebug = true;
    }
  },

  methods: {
    async fetchOrders() {
      this.loading = true;
      this.error = null;
      this.apiReady = true;

      try {
        console.log('Fetching orders from:', `${this.apiBaseUrl}/api/orders`);

        const response = await api.orders.getAllOrders();

        console.log('API Response:', response);

        if (response && response.data) {
          this.orders = Array.isArray(response.data) ? response.data : [];
        } else if (Array.isArray(response)) {
          this.orders = response;
        } else {
          this.orders = [];
        }

        this.apiReady = true;

      } catch (err) {
        console.error('获取点餐失败:', err);

        this.debugInfo = JSON.stringify({
          status: err.status,
          message: err.message,
          data: err.data
        }, null, 2);

        if (err.status === 404) {
          this.apiReady = false;
          this.error = '点餐 API 端点不存在 (404)';
        } else {
          this.error = err.message || '获取点餐失败，请检查网络连接';
          this.apiReady = true;
        }

        this.orders = [];
      } finally {
        this.loading = false;
      }
    },

    async createOrder() {
      this.creating = true;

      try {
        // 设置默认用餐时间为当前时间（如果没有选择）
        let diningTime = this.newOrder.dining_time;
        if (!diningTime) {
          diningTime = new Date();
        }

        // 转换为后端要求的格式
        const formattedTime = this.formatDateTimeForBackend(diningTime);

        // 构建提交数据
        const submitData = {
          customer_name: this.newOrder.customer_name?.trim() || '未命名',
          table_number: this.newOrder.table_number?.trim() || '',
          people_count: this.newOrder.people_count || 2,
          dining_time: formattedTime,
          remark: this.newOrder.remark?.trim() || ''
        };

        console.log('Creating order with data:', submitData);

        const response = await api.orders.createOrder(submitData);

        console.log('Create response:', response);

        if (response && (response.success || response.id)) {
          // 创建成功后跳转到详情页添加菜品
          const orderId = response.data?.id || response.id;
          this.closeModal();
          this.$router.push(`/orders/${orderId}`);
        } else {
          throw new Error(response?.message || '创建失败');
        }
      } catch (err) {
        console.error('创建点餐失败:', err);

        if (err.status === 404) {
          alert('后端 API 未实现：POST /api/orders\n请先实现后端接口。');
        } else {
          alert('创建失败: ' + (err.message || '请稍后重试'));
        }
      } finally {
        this.creating = false;
      }
    },

    formatTime(dateString) {
      if (!dateString) return '';
      try {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMins < 1) {
          return '刚刚';
        } else if (diffMins < 60) {
          return `${diffMins}分钟前`;
        } else if (diffHours < 24) {
          return `${diffHours}小时前`;
        } else if (diffDays < 7) {
          return `${diffDays}天前`;
        } else {
          return date.toLocaleDateString('zh-CN', {
            month: 'short',
            day: 'numeric'
          });
        }
      } catch {
        return dateString;
      }
    },

    formatDiningTime(dateString) {
      if (!dateString) return '未指定';
      try {
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN', {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      } catch {
        return dateString;
      }
    },

    formatDateTimeForBackend(dateString) {
      if (!dateString) return '';

      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) {
          return '';
        }

        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');

        return `${year}-${month}-${day} ${hours}:${minutes}`;
      } catch (error) {
        console.error('日期格式化错误:', error);
        return '';
      }
    },

    viewOrder(id) {
      this.$router.push(`/orders/${id}`);
    },

    handleSearch() {
      // 实时搜索
    },

    clearSearch() {
      this.searchKeyword = '';
    },

    search() {
      // 搜索按钮
    },

    closeModal() {
      this.showAddModal = false;
      this.newOrder = {
        customer_name: '',
        table_number: '',
        people_count: 2,
        dining_time: '',
        remark: ''
      };
    }
  }
};
</script>

<style scoped lang="scss">
.order-list {
  min-height: calc(100vh - 200px);
  padding: 16px;
  background-color: #f5f5f7;
}

.header-section {
  padding: 0 4px;
}

// 搜索栏
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

      &:focus {
        box-shadow: none;
      }
    }

    .btn {
      border: none;
      padding: 14px 18px;
    }
  }
}

// 点餐网格 - 一行2个
.order-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 0 4px;
}

.order-item {
  width: 100%;
}

// 点餐卡片 - 去除状态颜色，统一风格
.order-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }

  &:active {
    transform: scale(0.98);
  }
}

.order-header {
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;

  .order-name {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 4px;
    word-break: break-all;
  }

  .order-location {
    font-size: 13px;
    opacity: 0.9;

    i {
      font-size: 12px;
    }
  }

  .order-time {
    font-size: 11px;
    opacity: 0.8;
    white-space: nowrap;
    margin-left: 8px;
  }
}

.order-body {
  padding: 12px 16px;

  .info-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    font-size: 13px;
    color: #666;

    &:last-child {
      margin-bottom: 0;
    }

    i {
      color: #0d6efd;
      font-size: 14px;
      width: 16px;
    }

    .text-truncate {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
}

.order-footer {
  padding: 12px 16px;
  background: #f8f9fa;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;

  .item-count {
    font-size: 13px;
    color: #666;

    i {
      color: #0d6efd;
    }
  }
}

// 弹窗样式
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 16px;
}

.modal-content {
  background: white;
  width: 100%;
  max-width: 400px;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  padding: 20px 20px 0;
  border: none;
  display: flex;
  justify-content: space-between;
  align-items: center;

  .modal-title {
    font-weight: 600;
  }
}

.modal-body {
  padding: 20px;
}

// 响应式
@media (min-width: 768px) {
  .order-list {
    padding: 24px;
    max-width: 1200px;
    margin: 0 auto;
  }

  .order-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }
}

@media (min-width: 1024px) {
  .order-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>