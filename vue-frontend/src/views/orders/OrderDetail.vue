<!-- src/views/orders/OrderDetail.vue -->
<template>
  <div class="order-detail">
    <div class="container">
      <!-- 头部 -->
      <div class="header mb-4">
        <button class="btn btn-light rounded-pill" @click="$router.back()">
          <i class="bi bi-arrow-left me-2"></i>返回
        </button>
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
        <p class="mt-2 text-muted">加载中...</p>
      </div>

      <!-- 内容 -->
      <div v-else-if="order" class="content-wrapper">
        <!-- 订单信息卡片 -->
        <div class="info-card mb-4">
          <div class="info-header">
            <div class="d-flex justify-content-between align-items-start">
              <div class="flex-fill">
                <h4 class="mb-1">{{ order.customer_name || '未命名' }}</h4>
                <p class="location mb-0">
                  <i class="bi bi-geo-alt me-1"></i>{{ order.table_number || '未指定位置' }}
                </p>
              </div>
              <button class="btn btn-light btn-sm rounded-circle" @click="showEdit = true">
                <i class="bi bi-pencil"></i>
              </button>
            </div>
          </div>

          <div class="info-body">
            <div class="info-grid">
              <div class="info-item">
                <i class="bi bi-people"></i>
                <span>{{ order.people_count || '-' }}人用餐</span>
              </div>
              <div class="info-item">
                <i class="bi bi-clock"></i>
                <span>{{ formatTime(order.dining_time) }}</span>
              </div>
            </div>

            <div v-if="order.remark" class="remark mt-3">
              <small class="text-muted"><i class="bi bi-journal-text me-1"></i>{{ order.remark }}</small>
            </div>
          </div>
        </div>

        <!-- 操作按钮 - 只保留加菜 -->
        <div class="action-bar mb-4">
          <button class="btn btn-primary rounded-pill w-100" @click="showAddItem = true">
            <i class="bi bi-plus-lg me-2"></i>添加菜品
          </button>
        </div>

        <!-- 菜品列表 -->
        <div class="items-section">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="section-title mb-0">已点菜品</h5>
            <span class="badge bg-primary rounded-pill">{{ orderItems.length }} 道</span>
          </div>

          <div v-if="itemsLoading" class="text-center py-4">
            <div class="spinner-border spinner-border-sm text-primary"></div>
            <p class="text-muted small mt-2">加载菜品...</p>
          </div>

          <div v-else-if="orderItems.length === 0" class="empty-state text-center py-4">
            <i class="bi bi-cart-x" style="font-size: 3rem; color: #dee2e6;"></i>
            <p class="text-muted mt-2">还没有点菜</p>
            <button class="btn btn-primary rounded-pill mt-2" @click="showAddItem = true">
              <i class="bi bi-plus-lg me-2"></i>去点菜
            </button>
          </div>

          <div v-else class="item-list">
            <div
              v-for="item in orderItems"
              :key="item.id"
              class="item-card"
            >
              <div class="d-flex align-items-center gap-3">
                <!-- 菜品图片 -->
                <div class="item-image">
                  <img
                    v-if="item.recipeDetails?.image_url"
                    :src="getImageUrl(item.recipeDetails.image_url)"
                    :alt="item.recipe_name"
                  >
                  <div v-else class="no-image">
                    <i class="bi bi-image text-muted"></i>
                  </div>
                </div>

                <!-- 菜品信息 -->
                <div class="flex-fill">
                  <h6 class="item-name mb-1">{{ item.recipe_name }}</h6>
                  <small class="text-muted">{{ item.quantity }} 份</small>
                </div>

                <!-- 操作按钮 -->
                <div class="d-flex align-items-center gap-2">
                  <div class="quantity-control">
                    <button
                      class="btn btn-sm btn-light rounded-circle"
                      @click="updateQuantity(item, -1)"
                      :disabled="item.quantity <= 1 || updating"
                    >
                      <i class="bi bi-dash"></i>
                    </button>
                    <span class="quantity">{{ item.quantity }}</span>
                    <button
                      class="btn btn-sm btn-light rounded-circle"
                      @click="updateQuantity(item, 1)"
                      :disabled="updating"
                    >
                      <i class="bi bi-plus"></i>
                    </button>
                  </div>
                  <button
                    class="btn btn-sm btn-outline-danger rounded-circle"
                    @click="removeItem(item.id)"
                    :disabled="updating"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 统计 -->
          <div v-if="orderItems.length > 0" class="total-section mt-4">
            <div class="d-flex justify-content-between align-items-center">
              <span class="text-muted">共 {{ orderItems.length }} 道菜，{{ totalQuantity }} 份</span>
            </div>
          </div>
        </div>

        <!-- 底部操作栏：开始制作 + 取消订单 -->
        <div class="bottom-actions mt-4">
          <button
            v-if="order.status === 'pending'"
            class="btn btn-warning rounded-pill flex-fill"
            @click="updateStatus('preparing')"
            :disabled="updating"
          >
            <i class="bi bi-fire me-2"></i>开始制作
          </button>
          <button
            v-else-if="order.status === 'preparing'"
            class="btn btn-info rounded-pill flex-fill text-white"
            @click="updateStatus('ready')"
            :disabled="updating"
          >
            <i class="bi bi-check-circle me-2"></i>制作完成
          </button>
          <button
            v-else-if="order.status === 'ready'"
            class="btn btn-success rounded-pill flex-fill"
            @click="updateStatus('served')"
            :disabled="updating"
          >
            <i class="bi bi-basket me-2"></i>确认上菜
          </button>
          <button
            v-else-if="order.status === 'served'"
            class="btn btn-secondary rounded-pill flex-fill"
            @click="updateStatus('completed')"
            :disabled="updating"
          >
            <i class="bi bi-check-all me-2"></i>完成订单
          </button>
          <button
            v-else-if="order.status === 'completed'"
            class="btn btn-outline-secondary rounded-pill flex-fill"
            disabled
          >
            <i class="bi bi-check-circle-fill me-2"></i>已完成
          </button>

          <button
            v-if="!['completed', 'cancelled'].includes(order.status)"
            class="btn btn-outline-danger rounded-pill"
            @click="cancelOrder"
            :disabled="updating"
          >
            <i class="bi bi-x-circle"></i>取消
          </button>

          <button
            v-else-if="order.status === 'cancelled'"
            class="btn btn-outline-secondary rounded-pill flex-fill"
            disabled
          >
            <i class="bi bi-x-circle-fill me-2"></i>已取消
          </button>
        </div>
      </div>

      <!-- 不存在 -->
      <div v-else class="text-center py-5">
        <i class="bi bi-receipt-cutoff" style="font-size: 4rem; color: #dee2e6;"></i>
        <h5 class="text-muted mt-3">点餐不存在</h5>
        <router-link to="/orders" class="btn btn-primary rounded-pill mt-3">
          返回列表
        </router-link>
      </div>
    </div>

    <!-- 添加菜品弹窗 -->
    <AddOrderItem
      v-if="showAddItem"
      :order-id="orderId"
      @close="showAddItem = false"
      @added="onItemAdded"
    />

    <!-- 编辑订单弹窗 -->
    <div v-if="showEdit" class="modal-overlay" @click.self="showEdit = false">
      <div class="modal-content rounded-4">
        <div class="modal-header">
          <h5 class="modal-title">编辑点餐信息</h5>
          <button type="button" class="btn-close" @click="showEdit = false"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="updateOrder">
            <div class="mb-3">
              <label class="form-label">用餐名称</label>
              <input type="text" class="form-control rounded-3" v-model="editForm.customer_name" placeholder="例如：家庭聚餐">
            </div>
            <div class="mb-3">
              <label class="form-label">位置</label>
              <input type="text" class="form-control rounded-3" v-model="editForm.table_number" placeholder="例如：大厅A1">
            </div>
            <div class="mb-3">
              <label class="form-label">用餐人数</label>
              <input type="number" class="form-control rounded-3" v-model.number="editForm.people_count" min="1">
            </div>
            <div class="mb-3">
              <label class="form-label">用餐时间</label>
              <input type="datetime-local" class="form-control rounded-3" v-model="editForm.dining_time">
            </div>
            <div class="mb-3">
              <label class="form-label">备注</label>
              <textarea class="form-control rounded-3" v-model="editForm.remark" rows="2"></textarea>
            </div>
            <div class="d-flex gap-2">
              <button type="button" class="btn btn-light flex-fill rounded-3" @click="showEdit = false">取消</button>
              <button type="submit" class="btn btn-primary flex-fill rounded-3" :disabled="updating">
                <span v-if="updating" class="spinner-border spinner-border-sm me-2"></span>
                保存
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
import AddOrderItem from './AddOrderItem.vue';

export default {
  name: 'OrderDetail',

  components: {
    AddOrderItem
  },

  data() {
    return {
      order: null,
      orderItems: [],
      loading: false,
      itemsLoading: false,
      updating: false,
      showAddItem: false,
      showEdit: false,
      editForm: {}
    }
  },

  computed: {
    orderId() {
      return this.$route.params.id;
    },

    totalQuantity() {
      return this.orderItems.reduce((sum, item) => sum + item.quantity, 0);
    }
  },

  mounted() {
    this.fetchOrderDetail();
  },

  methods: {
    async fetchOrderDetail() {
      this.loading = true;

      try {
        const response = await api.orders.getOrderById(this.orderId);
        console.log('Order detail:', response);

        if (response && (response.data || response.id)) {
          this.order = response.data || response;
          this.editForm = { ...this.order };

          // 处理时间格式用于datetime-local输入框
          if (this.order.dining_time) {
            const date = new Date(this.order.dining_time);
            if (!isNaN(date.getTime())) {
              date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
              this.editForm.dining_time = date.toISOString().slice(0, 16);
            }
          }

          // 获取订单菜品列表（包含图片）
          await this.fetchOrderItemsWithImages();
        } else {
          this.order = null;
        }
      } catch (err) {
        console.error('获取点餐详情失败:', err);
        this.$notify?.({
          title: '错误',
          message: '获取详情失败: ' + (err.message || '未知错误'),
          type: 'error'
        });
      } finally {
        this.loading = false;
      }
    },

    async fetchOrderItemsWithImages() {
      this.itemsLoading = true;

      try {
        let items = [];

        // 首先获取订单菜品列表
        try {
          const response = await api.orders.getOrderItems(this.orderId);
          console.log('Order items from API:', response);
          items = response.data || response || [];
        } catch (apiErr) {
          console.warn('getOrderItems API 失败，尝试从订单数据获取:', apiErr);
          items = this.order?.items || [];
        }

        // 为每个菜品获取详细信息（包括图片）
        const itemsWithDetails = await Promise.all(
          items.map(async (item) => {
            try {
              // 调用 getRecipeById 获取菜谱详情
              const recipeResponse = await api.recipes.getRecipeById(item.recipe_id);
              const recipeDetails = recipeResponse.data || recipeResponse || {};

              return {
                ...item,
                recipeDetails: recipeDetails
              };
            } catch (err) {
              console.warn(`获取菜谱 ${item.recipe_id} 详情失败:`, err);
              // 如果获取失败，返回原始数据
              return {
                ...item,
                recipeDetails: null
              };
            }
          })
        );

        this.orderItems = itemsWithDetails;
        console.log('Order items with details:', itemsWithDetails);

      } catch (err) {
        console.error('获取菜品列表失败:', err);
        this.orderItems = [];
      } finally {
        this.itemsLoading = false;
      }
    },

    // 获取图片URL
    getImageUrl(imageUrl) {
      if (!imageUrl) return '';
      if (imageUrl.startsWith('http')) return imageUrl;
      return `${api.baseURL}${imageUrl.startsWith('/') ? '' : '/'}${imageUrl}`;
    },

    async updateStatus(status) {
      this.updating = true;

      try {
        const response = await api.orders.updateOrder(this.orderId, { status });
        console.log('Update status response:', response);

        this.order.status = status;

        this.$notify?.({
          title: '成功',
          message: '状态更新成功',
          type: 'success'
        });
      } catch (err) {
        console.error('更新状态失败:', err);
        this.$notify?.({
          title: '错误',
          message: '更新失败: ' + (err.message || '请稍后重试'),
          type: 'error'
        });
      } finally {
        this.updating = false;
      }
    },

    async cancelOrder() {
      if (!confirm('确定要取消这个订单吗？')) return;

      this.updating = true;

      try {
        await api.orders.updateOrder(this.orderId, { status: 'cancelled' });
        this.order.status = 'cancelled';

        this.$notify?.({
          title: '成功',
          message: '订单已取消',
          type: 'success'
        });
      } catch (err) {
        this.$notify?.({
          title: '错误',
          message: '取消失败: ' + err.message,
          type: 'error'
        });
      } finally {
        this.updating = false;
      }
    },

    async updateOrder() {
      this.updating = true;

      try {
        // 处理时间格式
        const submitData = { ...this.editForm };
        if (submitData.dining_time) {
          const date = new Date(submitData.dining_time);
          if (!isNaN(date.getTime())) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            submitData.dining_time = `${year}-${month}-${day} ${hours}:${minutes}`;
          }
        }

        const response = await api.orders.updateOrder(this.orderId, submitData);
        console.log('Update order response:', response);

        this.order = { ...this.order, ...submitData };
        this.showEdit = false;

        this.$notify?.({
          title: '成功',
          message: '信息更新成功',
          type: 'success'
        });
      } catch (err) {
        console.error('更新订单失败:', err);
        this.$notify?.({
          title: '错误',
          message: '更新失败: ' + (err.message || '请稍后重试'),
          type: 'error'
        });
      } finally {
        this.updating = false;
      }
    },

    async updateQuantity(item, delta) {
      const newQuantity = item.quantity + delta;
      if (newQuantity < 1) return;

      this.updating = true;

      try {
        await api.orders.updateOrderItem(this.orderId, item.id, {
          quantity: newQuantity
        });

        item.quantity = newQuantity;

        this.$notify?.({
          title: '成功',
          message: '数量已更新',
          type: 'success'
        });
      } catch (err) {
        console.error('更新数量失败:', err);
        this.$notify?.({
          title: '错误',
          message: '更新失败: ' + err.message,
          type: 'error'
        });
      } finally {
        this.updating = false;
      }
    },

    async removeItem(itemId) {
      if (!confirm('确定要移除这道菜吗？')) return;

      this.updating = true;

      try {
        await api.orders.removeOrderItem(this.orderId, itemId);
        this.orderItems = this.orderItems.filter(item => item.id !== itemId);

        this.$notify?.({
          title: '成功',
          message: '已移除菜品',
          type: 'success'
        });
      } catch (err) {
        console.error('移除菜品失败:', err);
        this.$notify?.({
          title: '错误',
          message: '删除失败: ' + err.message,
          type: 'error'
        });
      } finally {
        this.updating = false;
      }
    },

    onItemAdded() {
      this.showAddItem = false;
      // 刷新菜品列表（包含图片）
      this.fetchOrderItemsWithImages();
    },

    formatTime(dateString) {
      if (!dateString) return '未指定';
      try {
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      } catch {
        return dateString;
      }
    }
  }
};
</script>

<style scoped lang="scss">
.order-detail {
  min-height: 100vh;
  background: #f5f5f7;
  padding-bottom: 100px;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 16px;
}

.header {
  padding-top: 8px;
}

.content-wrapper {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

// 信息卡片
.info-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);

  .info-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;

    h4 {
      font-weight: 600;
      margin-bottom: 4px;
    }

    .location {
      font-size: 14px;
      opacity: 0.9;

      i {
        font-size: 12px;
      }
    }

    .btn-light {
      width: 36px;
      height: 36px;
      padding: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }

  .info-body {
    padding: 20px;
  }
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;

  .info-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: #666;

    i {
      color: #0d6efd;
    }
  }
}

.remark {
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;

  i {
    color: #6c757d;
  }
}

// 操作栏
.action-bar {
  .btn {
    padding: 14px 24px;
    font-weight: 500;
  }
}

// 菜品区域
.items-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);

  .section-title {
    font-weight: 600;
    color: #1a1a1a;
  }
}

.item-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item-card {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 16px;
  border: 1px solid #e9ecef;
  transition: all 0.2s;

  &:hover {
    background: #e9ecef;
  }

  .item-image {
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

  .item-name {
    font-weight: 600;
    color: #1a1a1a;
    font-size: 15px;
  }

  .quantity-control {
    display: flex;
    align-items: center;
    gap: 8px;

    .btn {
      width: 28px;
      height: 28px;
      padding: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
    }

    .quantity {
      font-weight: 600;
      min-width: 24px;
      text-align: center;
      font-size: 14px;
    }
  }
}

.total-section {
  padding-top: 16px;
  border-top: 2px dashed #dee2e6;
  color: #666;
  font-size: 14px;
}

// 底部操作栏
.bottom-actions {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);

  .btn {
    padding: 12px 20px;
    font-weight: 500;

    &.flex-fill {
      flex: 1;
    }
  }
}

// 弹窗
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
  border-radius: 20px;
  animation: slideUp 0.3s ease;
  max-height: 90vh;
  overflow-y: auto;
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

// 空状态
.empty-state {
  i {
    display: block;
  }
}
</style>