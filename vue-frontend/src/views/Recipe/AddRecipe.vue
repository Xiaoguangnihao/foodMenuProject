<!-- src/views/AddRecipe.vue -->
<template>
  <div class="add-recipe">
    <div class="container">
      <h2 class="mb-4">添加新菜谱</h2>

      <form @submit.prevent="submitForm">
        <!-- 表单字段保持不变 -->
        <div class="mb-3">
          <label class="form-label">菜谱名称 *</label>
          <input
            type="text"
            class="form-control"
            v-model="form.name"
            required
            placeholder="请输入菜谱名称"
            :disabled="loading"
          >
          <div v-if="errors.name" class="text-danger small mt-1">
            {{ errors.name }}
          </div>
        </div>

        <div class="row">
          <div class="col-md-6 mb-3">
            <label class="form-label">分类</label>
            <select class="form-select" v-model="form.category" :disabled="loading">
              <option value="家常菜">家常菜</option>
              <option value="甜品">甜品</option>
              <option value="主食">主食</option>
              <option value="汤类">汤类</option>
              <option value="未分类">未分类</option>
            </select>
          </div>
          <div class="col-md-6 mb-3">
            <label class="form-label">准备时间(分钟)</label>
            <input
              type="number"
              class="form-control"
              v-model.number="form.prep_time"
              min="0"
              placeholder="例如：30"
              :disabled="loading"
            >
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label">食材(每行一个)</label>
          <textarea
            class="form-control"
            v-model="form.ingredients"
            rows="3"
            placeholder="鸡蛋 2个&#10;番茄 1个&#10;盐 适量"
            :disabled="loading"
          ></textarea>
        </div>

        <div class="mb-3">
          <label class="form-label">制作步骤(每行一步)</label>
          <textarea
            class="form-control"
            v-model="form.steps"
            rows="4"
            placeholder="1. 准备食材&#10;2. 热锅加油&#10;3. 先炒鸡蛋&#10;4. 加入番茄翻炒"
            :disabled="loading"
          ></textarea>
        </div>

        <div class="mb-3">
          <label class="form-label">标签(用逗号分隔)</label>
          <input
            type="text"
            class="form-control"
            v-model="form.tags"
            placeholder="例如：简单,快捷,健康"
            :disabled="loading"
          >
        </div>

        <div class="mb-3">
          <label class="form-label">菜谱图片</label>
          <div
            class="image-upload"
            @click="!loading && $refs.fileInput.click()"
            :class="{ 'disabled': loading }"
          >
            <i class="bi bi-camera" style="font-size: 2rem; color: #6c757d;"></i>
            <p class="mt-2 mb-1">点击上传图片</p>
            <small class="text-muted">支持 JPG, PNG, GIF, WebP, BMP 格式</small>
            <input
              type="file"
              ref="fileInput"
              class="d-none"
              accept="image/*"
              @change="handleImageUpload"
              :disabled="loading"
            >
          </div>
          <img
            v-if="imagePreview"
            :src="imagePreview"
            class="image-preview mt-3"
            alt="图片预览"
          >
          <div v-if="imageUploading" class="text-info mt-2">
            <span class="spinner-border spinner-border-sm me-2"></span>
            正在上传图片...
          </div>
          <div v-if="errors.image" class="text-danger small mt-2">
            {{ errors.image }}
          </div>
        </div>

        <div class="d-flex gap-2 mt-4">
          <button
            type="button"
            class="btn btn-secondary"
            @click="cancel"
            :disabled="loading"
          >
            取消
          </button>
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="loading || imageUploading"
          >
            <span v-if="loading">
              <span class="spinner-border spinner-border-sm me-2"></span>
              保存中...
            </span>
            <span v-else>保存菜谱</span>
          </button>
        </div>

        <!-- 错误提示 -->
        <div v-if="submitError" class="alert alert-danger mt-3">
          {{ submitError }}
        </div>
      </form>
    </div>
  </div>
</template>

<script>
// 导入 API 模块
import api from '@/api';

export default {
  name: 'AddRecipe',

  data() {
    return {
      form: {
        name: '',
        category: '家常菜',
        prep_time: 0,
        ingredients: '',
        steps: '',
        tags: '',
        image: null
      },
      imagePreview: '',
      loading: false,
      imageUploading: false,
      errors: {
        name: '',
        image: ''
      },
      submitError: ''
    };
  },

  methods: {
    // 验证图片文件
    validateImage(file) {
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'];
      const maxSize = 5 * 1024 * 1024; // 5MB

      if (!validTypes.includes(file.type)) {
        return '不支持的图片格式，请使用 JPG、PNG、GIF、WebP、BMP 格式';
      }

      if (file.size > maxSize) {
        return '图片文件太大，请选择小于 5MB 的图片';
      }

      return null;
    },

    // 处理图片上传
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      // 清空之前的错误
      this.errors.image = '';
      this.submitError = '';

      // 验证图片
      const validationError = this.validateImage(file);
      if (validationError) {
        this.errors.image = validationError;
        event.target.value = '';
        return;
      }

      this.form.image = file;

      // 创建预览
      const reader = new FileReader();
      reader.onload = (e) => {
        this.imagePreview = e.target.result;
      };
      reader.onerror = () => {
        this.errors.image = '图片读取失败，请选择其他图片';
        event.target.value = '';
        this.form.image = null;
        this.imagePreview = '';
      };
      reader.readAsDataURL(file);
    },

    // 验证表单
    validateForm() {
      this.errors = { name: '', image: '' };
      let isValid = true;

      // 验证名称
      if (!this.form.name.trim()) {
        this.errors.name = '菜谱名称不能为空';
        isValid = false;
      }

      // 验证图片（如果已选择）
      if (this.form.image) {
        const validationError = this.validateImage(this.form.image);
        if (validationError) {
          this.errors.image = validationError;
          isValid = false;
        }
      }

      return isValid;
    },

    // 提交表单
    async submitForm() {
      // 验证表单
      if (!this.validateForm()) {
        return;
      }

      this.loading = true;
      this.submitError = '';

      try {
        // 使用 api.recipes.createRecipe 创建菜谱（支持图片文件上传）
        const response = await api.recipes.createRecipe(this.form);

        if (response && response.success) {
          // 显示成功消息
          this.showSuccess('菜谱添加成功！');

          // 更新 Vuex store（如果存在）
          if (this.$store) {
            this.$store.dispatch('addRecipe', response.data);
          }

          // 跳转到首页
          this.$router.push('/');
        } else {
          throw new Error(response?.message || '保存失败');
        }
      } catch (error) {
        console.error('保存失败:', error);
        this.handleSubmitError(error);
      } finally {
        this.loading = false;
      }
    },

    // 处理提交错误
    handleSubmitError(error) {
      let errorMessage = '';

      if (error.message) {
        // 来自 API 的错误消息
        errorMessage = error.message;
      } else if (error.status) {
        // HTTP 状态码错误
        switch (error.status) {
          case 400:
            errorMessage = '请求数据格式不正确，请检查填写的内容';
            break;
          case 413:
            errorMessage = '图片文件太大，请选择小于5MB的图片';
            break;
          case 415:
            errorMessage = '不支持的图片格式，请使用 JPG、PNG 等常见格式';
            break;
          case 500:
            errorMessage = '服务器内部错误，请稍后重试';
            break;
          default:
            errorMessage = `保存失败: ${error.status}`;
        }
      } else {
        // 网络或其他错误
        errorMessage = '无法连接到服务器，请检查网络连接并确保后端服务已启动';
      }

      this.submitError = errorMessage;

      // 滚动到错误位置
      this.$nextTick(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    },

    // 取消操作
    cancel() {
      if (this.form.name || this.form.ingredients || this.form.steps) {
        if (confirm('您有未保存的内容，确定要离开吗？')) {
          this.$router.back();
        }
      } else {
        this.$router.back();
      }
    },

    // 显示成功消息
    showSuccess(message) {
      if (this.$notify) {
        this.$notify({
          title: '成功',
          message,
          type: 'success'
        });
      } else {
        alert(message);
      }
    }
  },

  // 组件销毁前清理
  beforeUnmount() {
    // 清理图片预览的 Blob URL
    if (this.imagePreview && this.imagePreview.startsWith('blob:')) {
      URL.revokeObjectURL(this.imagePreview);
    }
  },

  // 离开页面提醒
  beforeRouteLeave(to, from, next) {
    if (this.form.name && !this.loading) {
      if (confirm('您有未保存的内容，确定要离开吗？')) {
        next();
      } else {
        next(false);
      }
    } else {
      next();
    }
  }
};
</script>

<style scoped>
.add-recipe {
  padding: 2rem 0;
}

.image-upload {
  border: 2px dashed #dee2e6;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.image-upload:hover:not(.disabled) {
  border-color: #0d6efd;
  background-color: #f8f9fa;
}

.image-upload.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.image-preview {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.container {
  max-width: 800px;
}
</style>