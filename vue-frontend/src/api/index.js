import axios from 'axios';

// 配置
const API_BASE_URL = 'http://localhost:8000';
const API_TIMEOUT = 30000; // 30秒超时

// 订单状态枚举（与后端保持一致）
export const OrderStatus = {
  PENDING: 'pending',      // 待确认
  CONFIRMED: 'confirmed',  // 已确认
  PREPARING: 'preparing',  // 准备中
  READY: 'ready',         // 已备好
  SERVED: 'served',       // 已上菜
  CANCELLED: 'cancelled', // 已取消
  COMPLETED: 'completed', // 已完成
};

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加 token 等
    // config.headers.Authorization = `Bearer ${getToken()}`;

    // 如果是 FormData，删除 Content-Type 头，让浏览器自动设置
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    // 统一处理成功响应
    return response.data;
  },
  (error) => {
    // 统一处理错误响应
    const errorMessage = getErrorMessage(error);
    console.error('API Error:', errorMessage);

    // 可以在这里添加全局错误处理，如显示通知
    if (error.response?.status === 401) {
      // 处理未授权
      // router.push('/login');
    }

    return Promise.reject({
      status: error.response?.status,
      message: errorMessage,
      data: error.response?.data,
      originalError: error,
    });
  }
);

// 错误消息处理函数
function getErrorMessage(error) {
  if (error.response) {
    // 服务器返回了错误状态码
    switch (error.response.status) {
      case 400:
        return error.response.data?.detail || '请求数据格式不正确';
      case 401:
        return '未授权，请重新登录';
      case 403:
        return '权限不足';
      case 404:
        return '请求的资源不存在';
      case 413:
        return '文件大小超过限制';
      case 415:
        return '不支持的图片格式';
      case 422:
        return '数据验证失败';
      case 500:
        return '服务器内部错误';
      case 502:
      case 503:
      case 504:
        return '服务器暂时不可用，请稍后重试';
      default:
        return `请求失败: ${error.response.status}`;
    }
  } else if (error.request) {
    // 请求已发送但没有收到响应
    return '无法连接到服务器，请检查网络连接';
  } else {
    // 请求设置时出错
    return error.message || '未知错误';
  }
}

// 菜谱相关 API
const recipeApi = {
  // 获取所有菜谱
  getAllRecipes(params = {}) {
    return apiClient.get('/api/recipes', { params });
  },

  // 获取单个菜谱
  getRecipeById(id) {
    return apiClient.get(`/api/recipes/${id}`);
  },

  // 创建菜谱
  createRecipe(recipeData) {
    const formData = new FormData();

    // 添加文本字段
    Object.keys(recipeData).forEach(key => {
      if (key === 'image' && recipeData[key] instanceof File) {
        // 图片文件单独处理
        formData.append('image', recipeData[key]);
      } else if (recipeData[key] !== null && recipeData[key] !== undefined) {
        // 其他字段
        const value = recipeData[key];

        // 处理数组类型字段（如 ingredients, steps, tags）
        if (Array.isArray(value)) {
          if (key === 'ingredients' || key === 'steps') {
            // 每行一个的形式
            formData.append(key, value.join('\n'));
          } else if (key === 'tags') {
            // 逗号分隔的形式
            formData.append(key, value.join(','));
          } else {
            formData.append(key, JSON.stringify(value));
          }
        } else {
          formData.append(key, value);
        }
      }
    });

    return apiClient.post('/api/recipes', formData);
  },

  // 更新菜谱
  updateRecipe(id, recipeData) {
    const formData = new FormData();

    // 添加文本字段
    Object.keys(recipeData).forEach(key => {
      if (key === 'image' && recipeData[key] instanceof File) {
        // 图片文件单独处理
        formData.append('image', recipeData[key]);
      } else if (recipeData[key] !== null && recipeData[key] !== undefined) {
        // 其他字段
        const value = recipeData[key];

        // 处理数组类型字段（如 ingredients, steps, tags）
        if (Array.isArray(value)) {
          if (key === 'ingredients' || key === 'steps') {
            // 每行一个的形式
            formData.append(key, value.join('\n'));
          } else if (key === 'tags') {
            // 逗号分隔的形式
            formData.append(key, value.join(','));
          } else {
            formData.append(key, JSON.stringify(value));
          }
        } else {
          formData.append(key, value);
        }
      }
    });

    return apiClient.put(`/api/recipes/${id}`, formData);
  },

  // 删除菜谱
  deleteRecipe(id) {
    return apiClient.delete(`/api/recipes/${id}`);
  },

  // 搜索菜谱
  searchRecipes(keyword, searchIn = 'all') {
    return apiClient.get('/api/search', {
      params: { keyword, search_in: searchIn }
    });
  },
};

// 点餐相关 API
const orderApi = {
  // 获取所有点餐
  getAllOrders(params = {}) {
    return apiClient.get('/api/orders', { params });
  },

  // 获取单个点餐详情
  getOrderById(id) {
    return apiClient.get(`/api/orders/${id}`);
  },

  // 创建点餐
  createOrder(orderData) {
    const formData = new FormData();

    Object.keys(orderData).forEach(key => {
      if (orderData[key] !== null && orderData[key] !== undefined) {
        formData.append(key, orderData[key]);
      }
    });

    return apiClient.post('/api/orders', formData);
  },

  // 更新点餐
  updateOrder(id, orderData) {
    const formData = new FormData();

    Object.keys(orderData).forEach(key => {
      if (orderData[key] !== null && orderData[key] !== undefined) {
        formData.append(key, orderData[key]);
      }
    });

    return apiClient.put(`/api/orders/${id}`, formData);
  },

  // 删除点餐
  deleteOrder(id) {
    return apiClient.delete(`/api/orders/${id}`);
  },

  // 添加菜谱到点餐
  addOrderItem(orderId, itemData) {
    const formData = new FormData();

    Object.keys(itemData).forEach(key => {
      if (itemData[key] !== null && itemData[key] !== undefined) {
        formData.append(key, itemData[key]);
      }
    });

    return apiClient.post(`/api/orders/${orderId}/items`, formData);
  },

  // 从点餐中移除菜谱项目
  removeOrderItem(orderId, itemId) {
    return apiClient.delete(`/api/orders/${orderId}/items/${itemId}`);
  },

  // 更新点餐项目（如修改数量）
  updateOrderItem(orderId, itemId, itemData) {
    const formData = new FormData();

    Object.keys(itemData).forEach(key => {
      if (itemData[key] !== null && itemData[key] !== undefined) {
        formData.append(key, itemData[key]);
      }
    });

    return apiClient.put(`/api/orders/${orderId}/items/${itemId}`, formData);
  },

  // 搜索点餐
  searchOrders(keyword, searchIn = 'customer_name') {
    return apiClient.get('/api/orders/search', {
      params: { keyword, search_in: searchIn }
    });
  },
};

// 分类相关 API
const categoryApi = {
  // 获取所有分类
  getAllCategories() {
    return apiClient.get('/api/categories');
  },
};

// 文件上传相关 API
const uploadApi = {
  // 上传图片
  uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);

    return apiClient.post('/api/upload', formData);
  },
};

// 统计相关 API
const statisticsApi = {
  // 获取系统统计
  getStatistics() {
    return apiClient.get('/api/statistics');
  },

  // 获取今日点餐统计
  getTodayOrderStatistics() {
    return apiClient.get('/api/orders/statistics/today');
  },

  // 获取点餐状态统计
  getOrderStatusStatistics() {
    return apiClient.get('/api/orders/statistics/status');
  },

  // 健康检查
  healthCheck() {
    return apiClient.get('/api/health');
  },
};

// 点餐状态管理 API
const orderStatusApi = {
  // 确认点餐
  confirmOrder(orderId) {
    return apiClient.put(`/api/orders/${orderId}`, {
      status: OrderStatus.CONFIRMED
    });
  },

  // 开始准备
  startPreparing(orderId) {
    return apiClient.put(`/api/orders/${orderId}`, {
      status: OrderStatus.PREPARING
    });
  },

  // 标记为已备好
  markAsReady(orderId) {
    return apiClient.put(`/api/orders/${orderId}`, {
      status: OrderStatus.READY
    });
  },

  // 标记为已上菜
  markAsServed(orderId) {
    return apiClient.put(`/api/orders/${orderId}`, {
      status: OrderStatus.SERVED
    });
  },

  // 取消点餐
  cancelOrder(orderId) {
    return apiClient.put(`/api/orders/${orderId}`, {
      status: OrderStatus.CANCELLED
    });
  },

  // 完成点餐
  completeOrder(orderId) {
    return apiClient.put(`/api/orders/${orderId}`, {
      status: OrderStatus.COMPLETED
    });
  },
};

// 辅助函数
export const helpers = {
  // 格式化用餐时间
  formatDiningTime(diningTime) {
    if (!diningTime) return '';

    try {
      const date = new Date(diningTime);
      if (isNaN(date.getTime())) {
        return diningTime;
      }
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      });
    } catch (error) {
      return diningTime;
    }
  },


  // 获取订单状态标签和颜色
  getOrderStatusInfo(status) {
    const statusMap = {
      [OrderStatus.PENDING]: {
        label: '待确认',
        color: '#FF9800',
        bgColor: '#FFF3E0'
      },
      [OrderStatus.CONFIRMED]: {
        label: '已确认',
        color: '#2196F3',
        bgColor: '#E3F2FD'
      },
      [OrderStatus.PREPARING]: {
        label: '准备中',
        color: '#9C27B0',
        bgColor: '#F3E5F5'
      },
      [OrderStatus.READY]: {
        label: '已备好',
        color: '#673AB7',
        bgColor: '#EDE7F6'
      },
      [OrderStatus.SERVED]: {
        label: '已上菜',
        color: '#4CAF50',
        bgColor: '#E8F5E9'
      },
      [OrderStatus.CANCELLED]: {
        label: '已取消',
        color: '#F44336',
        bgColor: '#FFEBEE'
      },
      [OrderStatus.COMPLETED]: {
        label: '已完成',
        color: '#607D8B',
        bgColor: '#ECEFF1'
      }
    };

    return statusMap[status] || {
      label: status || '未知',
      color: '#9E9E9E',
      bgColor: '#FAFAFA'
    };
  },

  // 验证菜谱数据
  validateRecipeData(recipeData) {
    const errors = [];

    if (!recipeData.name || recipeData.name.trim().length === 0) {
      errors.push('菜谱名称不能为空');
    }

    if (recipeData.prep_time < 0) {
      errors.push('准备时间不能为负数');
    }

    if (recipeData.price < 0) {
      errors.push('价格不能为负数');
    }

    return errors;
  },

  // 验证点餐数据
  validateOrderData(orderData) {
    const errors = [];

    if (!orderData.customer_name || orderData.customer_name.trim().length === 0) {
      errors.push('客户名称不能为空');
    }

    if (!orderData.people_count || orderData.people_count < 1) {
      errors.push('用餐人数至少为1人');
    }

    if (!orderData.dining_time) {
      errors.push('用餐时间不能为空');
    } else {
      try {
        const diningTime = new Date(orderData.dining_time);
        const now = new Date();

        if (diningTime < now) {
          errors.push('用餐时间不能是过去时间');
        }
      } catch (error) {
        errors.push('用餐时间格式不正确');
      }
    }

    return errors;
  },

  // 生成菜谱选择的选项
  generateRecipeOptions(recipes) {
    if (!recipes || !Array.isArray(recipes)) return [];

    return recipes.map(recipe => ({
      value: recipe.id,
      label: recipe.name,
      price: recipe.price || 0,
      prepTime: recipe.prep_time || 0,
      category: recipe.category || '未分类'
    }));
  },

  // 导出订单数据（用于Excel等）
  exportOrderData(orders) {
    return orders.map(order => ({
      '订单ID': order.id,
      '客户名称': order.customer_name,
      '桌号': order.table_number || '',
      '用餐人数': order.people_count,
      '用餐时间': this.formatDiningTime(order.dining_time),
      '订单状态': this.getOrderStatusInfo(order.status).label,
      '菜品数量': order.total_items || (order.items ? order.items.length : 0),
      '创建时间': this.formatDiningTime(order.created_at),
      '备注': order.notes || ''
    }));
  },

  // 获取完整的图片URL
  getFullImageUrl(imagePath) {
    if (!imagePath) return null;
    if (imagePath.startsWith('http')) return imagePath;
    return `${API_BASE_URL}${imagePath}`;
  },

  // 格式化价格
  formatPrice(price) {
    if (typeof price !== 'number') {
      price = parseFloat(price) || 0;
    }
    return `¥${price.toFixed(2)}`;
  },

  // 格式化时间
  formatTime(timestamp) {
    if (!timestamp) return '';

    try {
      const date = new Date(timestamp);
      if (isNaN(date.getTime())) {
        return timestamp;
      }

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
          year: 'numeric',
          month: '2-digit',
          day: '2-digit'
        });
      }
    } catch (error) {
      return timestamp;
    }
  }
};

// 导出单个 API 对象（方便直接导入）
export {
  recipeApi,
  orderApi,
  categoryApi,
  uploadApi,
  statisticsApi,
  orderStatusApi,
  apiClient,
};

// 默认导出主 API 对象
const api = {
  // API 客户端
  client: apiClient,

  // 基础 URL（可用于图片显示）
  baseURL: API_BASE_URL,

  // API 分组
  recipes: recipeApi,
  orders: orderApi,
  categories: categoryApi,
  upload: uploadApi,
  statistics: statisticsApi,
  orderStatus: orderStatusApi,

  // 常量
  OrderStatus,

  // 辅助函数
  helpers,
};

export default api;