🍳 菜谱与点餐管理系统
一个完整的菜谱管理和点餐系统，包含前后端完整实现。系统支持菜谱的增删改查、图片上传、分类管理，以及点餐的创建、管理和状态跟踪。

🌟 功能特性
菜谱管理
✅ 菜谱的增删改查（CRUD操作）

✅ 图片上传和管理（支持多种格式）

✅ 分类和标签管理

✅ 全文搜索功能（支持多字段搜索）

✅ 食材清单和制作步骤管理

点餐管理
✅ 创建和管理点餐订单

✅ 添加/移除菜谱到点餐

✅ 用餐时间、人数、桌号管理

✅ 完整的订单状态管理（待确认、已确认、准备中、已备好、已上菜、已取消、已完成）

✅ 订单搜索功能

✅ 实时统计和分析

系统特性
✅ 响应式前端界面（Vue 3 + Element Plus）

✅ RESTful API 设计（FastAPI）

✅ 本地JSON文件存储（无需数据库）

✅ 完整的错误处理和数据验证

✅ 跨域支持（CORS）

✅ 自动数据备份和恢复

✅ 健康检查和系统监控

📁 项目结构

food-menu-system/
├── backend/                 # FastAPI后端
│   ├── main.py            # 主应用文件（包含所有API）
│   ├── uploads/           # 图片上传目录
│   └── data/             # 数据文件目录
│       ├── recipes.json   # 菜谱数据
│       └── orders.json    # 点餐数据
└── frontend/              # Vue 3前端
    ├── src/
    │   ├── api/          # API接口封装
    │   ├── components/   # Vue组件
    │   ├── views/        # 页面视图
    │   └── router/       # 路由配置
    └── package.json      # 依赖配置

🚀 快速开始
环境要求
Python 3.8+

Node.js 16+

npm 或 yarn

后端启动
进入后端目录

bash
cd backend
安装依赖

bash
pip install fastapi uvicorn python-multipart
启动服务器

bash
python main.py
或者直接运行：

bash
cd backend && python main.py
后端将在 http://localhost:8000 启动，并提供以下访问地址：

API 文档：http://localhost:8000/docs (Swagger UI)

交互文档：http://localhost:8000/redoc (ReDoc)

API 首页：http://localhost:8000

前端启动
进入前端目录

bash
cd frontend
安装依赖

bash
npm install
# 或使用 yarn
yarn install
启动开发服务器

bash
npm run serve
# 或
yarn serve
前端将在 http://localhost:8080 启动。

🔧 配置说明
后端配置
后端配置文件在 main.py 开头部分：

python
# 配置常量
UPLOAD_DIR = "uploads"         # 图片上传目录
DATA_FILE = "data/recipes.json" # 菜谱数据文件
ORDERS_FILE = "data/orders.json" # 点餐数据文件
前端配置
前端API配置在 src/api/index.js：

javascript
const API_BASE_URL = 'http://localhost:8000'; // 后端API地址
const API_TIMEOUT = 30000; // 请求超时时间

![img.png](img%2Fimg.png)
![img_1.png](img%2Fimg_1.png)
![img_2.png](img%2Fimg_2.png)