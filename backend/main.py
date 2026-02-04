# main.py - 完整的菜谱和点餐管理系统
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.openapi.utils import get_openapi
import json
import os
import uuid
from datetime import datetime, time
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

# ==================== 配置和初始化 ====================

# 配置常量
UPLOAD_DIR = "uploads"
DATA_FILE = "data/recipes.json"
ORDERS_FILE = "data/orders.json"


# 确保目录存在
def init_directories():
    """初始化目录结构"""
    directories = ["uploads", "data"]
    for dir_path in directories:
        Path(dir_path).mkdir(exist_ok=True)
        print(f"✓ 创建目录: {dir_path}")

    # 初始化数据文件
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print(f"✓ 创建菜谱数据文件: {DATA_FILE}")

    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print(f"✓ 创建点餐数据文件: {ORDERS_FILE}")


# 初始化目录
init_directories()


# ==================== 数据模型 ====================

class OrderStatus(str, Enum):
    """点餐状态枚举"""
    PENDING = "pending"  # 待确认
    CONFIRMED = "confirmed"  # 已确认
    PREPARING = "preparing"  # 准备中
    READY = "ready"  # 已备好
    SERVED = "served"  # 已上菜
    CANCELLED = "cancelled"  # 已取消
    COMPLETED = "completed"  # 已完成


class OrderItem(BaseModel):
    """点餐项目"""
    recipe_id: str
    recipe_name: str
    quantity: int = Field(ge=1, default=1)
    notes: Optional[str] = None
    price: Optional[float] = Field(ge=0, default=0)


# ==================== 创建FastAPI应用 ====================

app = FastAPI(
    title="菜谱与点餐管理系统 API",
    description="""
    🍳 一个完整的菜谱和点餐管理API系统

    ## 功能特色
    ### 菜谱管理
    - ✅ 菜谱的增删改查（CRUD）
    - ✅ 图片上传和管理
    - ✅ 分类和标签管理  
    - ✅ 全文搜索功能

    ### 点餐管理
    - ✅ 创建和管理点餐
    - ✅ 添加/移除菜谱到点餐
    - ✅ 更新点餐状态
    - ✅ 用餐时间和人数管理
    - ✅ 点餐统计和分析

    ## 数据存储
    - 菜谱数据: `data/recipes.json`
    - 点餐数据: `data/orders.json`
    - 上传图片: `uploads/` 目录

    ## 使用说明
    1. 启动服务器后访问 http://localhost:8000/docs 查看API文档
    2. 使用Swagger UI可以直接测试所有API接口
    3. 所有接口都支持跨域请求
    """,
    version="2.0.0",
    terms_of_service="http://localhost:8000/terms/",
    contact={
        "name": "菜谱与点餐管理系统",
        "url": "http://localhost:8000",
        "email": "support@recipe-order.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)


# 自定义OpenAPI文档
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # 添加标签分类
    openapi_schema["tags"] = [
        {
            "name": "首页",
            "description": "API首页和基本信息"
        },
        {
            "name": "菜谱管理",
            "description": "菜谱的增删改查操作"
        },
        {
            "name": "点餐管理",
            "description": "点餐的创建和管理"
        },
        {
            "name": "分类管理",
            "description": "菜谱分类相关操作"
        },
        {
            "name": "搜索功能",
            "description": "菜谱和点餐搜索"
        },
        {
            "name": "文件上传",
            "description": "图片上传和管理"
        },
        {
            "name": "统计功能",
            "description": "系统统计和健康检查"
        }
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ==================== 数据操作函数 ====================

def load_recipes() -> List[dict]:
    """加载菜谱数据"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_recipes(recipes: List[dict]):
    """保存菜谱数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)


def load_orders() -> List[dict]:
    """加载点餐数据"""
    try:
        with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_orders(orders: List[dict]):
    """保存点餐数据"""
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)


async def save_uploaded_image(file: UploadFile) -> str:
    """保存上传的图片文件"""
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型 {file_extension}。支持的类型: {', '.join(allowed_extensions)}"
        )

    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        contents = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
        return f"/uploads/{unique_filename}"
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"文件保存失败: {str(e)}"
        )


def delete_recipe_image(image_url: Optional[str]):
    """删除菜谱图片"""
    if image_url and image_url.startswith("/uploads/"):
        filename = image_url.replace("/uploads/", "")
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    return False


def get_recipe_by_id(recipe_id: str) -> Optional[dict]:
    """根据ID获取菜谱"""
    recipes = load_recipes()
    for recipe in recipes:
        if recipe.get("id") == recipe_id:
            return recipe
    return None


# ==================== API端点定义 ====================

@app.get("/", tags=["首页"], response_class=HTMLResponse)
async def root():
    """API首页"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>菜谱与点餐管理系统 API</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <styles>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                max-width: 1000px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                border-radius: 15px;
                margin-bottom: 30px;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .header h1 {
                margin: 0;
                font-size: 2.8em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .header p {
                margin: 15px 0 0;
                opacity: 0.95;
                font-size: 1.2em;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .stat-card {
                background: white;
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                transition: transform 0.3s, box-shadow 0.3s;
            }
            .stat-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            }
            .stat-value {
                font-size: 2.5em;
                font-weight: bold;
                color: #4CAF50;
                margin: 15px 0;
                text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
            }
            .docs-links {
                display: flex;
                gap: 20px;
                margin: 30px 0;
            }
            .docs-links a {
                flex: 1;
                padding: 20px;
                text-align: center;
                background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
                color: white;
                text-decoration: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 1.1em;
                transition: all 0.3s;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .docs-links a:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            }
            .api-section {
                background: white;
                padding: 30px;
                border-radius: 15px;
                margin-bottom: 30px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .endpoint {
                background: linear-gradient(to right, #f8f9fa, #e9ecef);
                padding: 20px;
                margin: 15px 0;
                border-radius: 10px;
                border-left: 6px solid;
                transition: all 0.3s;
            }
            .endpoint:hover {
                background: linear-gradient(to right, #e9ecef, #dee2e6);
            }
            .method {
                display: inline-block;
                padding: 8px 15px;
                border-radius: 8px;
                font-weight: bold;
                margin-right: 15px;
                font-size: 1em;
                color: white;
                min-width: 80px;
                text-align: center;
                box-shadow: 0 3px 6px rgba(0,0,0,0.1);
            }
            .get { background: linear-gradient(135deg, #2196F3 0%, #0D47A1 100%); }
            .post { background: linear-gradient(135deg, #4CAF50 0%, #1B5E20 100%); }
            .put { background: linear-gradient(135deg, #FF9800 0%, #E65100 100%); }
            .delete { background: linear-gradient(135deg, #F44336 0%, #B71C1C 100%); }
            footer {
                text-align: center;
                margin-top: 50px;
                padding: 25px;
                background: rgba(255,255,255,0.9);
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .system-status {
                display: inline-flex;
                align-items: center;
                gap: 10px;
                padding: 10px 20px;
                background: #4CAF50;
                color: white;
                border-radius: 25px;
                font-weight: bold;
            }
            .status-dot {
                width: 12px;
                height: 12px;
                background: white;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
        </styles>
    </head>
    <body>
        <div class="header">
            <h1>🍳 菜谱与点餐管理系统 API</h1>
            <p>完整的菜谱管理和点餐系统后端服务</p>
        </div>

        <div class="stats-grid" id="statsGrid">
            <!-- 统计数据会动态加载 -->
        </div>

        <div class="api-section">
            <h2>📚 API文档入口</h2>
            <p>完整、交互式的API文档，支持在线测试所有接口：</p>
            <div class="docs-links">
                <a href="/docs" target="_blank">Swagger UI 文档</a>
                <a href="/redoc" target="_blank">ReDoc 文档</a>
                <a href="/openapi.json" target="_blank">OpenAPI 规范</a>
            </div>
        </div>

        <div class="api-section">
            <h2>🍽️ 点餐管理接口</h2>
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/orders</strong>
                <p>创建新点餐（包括用餐时间、人数等信息）</p>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/orders</strong>
                <p>获取点餐列表，支持状态筛选和分页</p>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/orders/{order_id}/items</strong>
                <p>向点餐中添加菜谱项目</p>
            </div>
            <div class="endpoint">
                <span class="method delete">DELETE</span>
                <strong>/api/orders/{order_id}/items/{item_id}</strong>
                <p>从点餐中移除菜谱项目</p>
            </div>
        </div>

        <div class="api-section">
            <h2>📦 菜谱管理接口</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/recipes</strong>
                <p>获取菜谱列表，支持分类和分页</p>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/recipes</strong>
                <p>创建新菜谱（支持图片上传）</p>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/categories</strong>
                <p>获取菜谱分类统计</p>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/search</strong>
                <p>搜索菜谱（多字段搜索）</p>
            </div>
        </div>

        <div class="api-section">
            <h2>📊 统计接口</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/statistics</strong>
                <p>获取系统综合统计数据</p>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/orders/statistics</strong>
                <p>获取点餐相关统计</p>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/health</strong>
                <p>系统健康检查</p>
            </div>
        </div>

        <footer>
            <div class="system-status">
                <div class="status-dot"></div>
                <span>系统运行正常</span>
            </div>
            <p>菜谱与点餐管理系统 API v2.0.0 | 本地存储方案 | 快速启动，易于部署</p>
            <p>当前时间: <span id="currentTime"></span></p>
        </footer>

        <script>
            // 动态加载统计数据
            async function loadStats() {
                try {
                    const statsGrid = document.getElementById('statsGrid');

                    // 获取菜谱数量
                    const recipesRes = await fetch('/api/recipes');
                    const recipesData = await recipesRes.json();
                    const recipeCount = recipesData.count || 0;

                    // 获取点餐数量
                    const ordersRes = await fetch('/api/orders?limit=1');
                    const ordersData = await ordersRes.json();
                    const orderCount = ordersData.count || 0;

                    // 获取分类数量
                    const catsRes = await fetch('/api/categories');
                    const catsData = await catsRes.json();
                    const categoryCount = catsData.count || 0;

                    // 获取今日点餐
                    const todayRes = await fetch('/api/orders/statistics/today');
                    let todayOrders = 0;
                    try {
                        const todayData = await todayRes.json();
                        todayOrders = todayData.today_orders || 0;
                    } catch (e) {
                        console.log('今日统计接口可能未实现');
                    }

                    // 更新统计网格
                    statsGrid.innerHTML = `
                        <div class="stat-card">
                            <div>总菜谱数</div>
                            <div class="stat-value">${recipeCount}</div>
                            <div>个菜谱</div>
                        </div>
                        <div class="stat-card">
                            <div>总点餐数</div>
                            <div class="stat-value">${orderCount}</div>
                            <div>个订单</div>
                        </div>
                        <div class="stat-card">
                            <div>分类数量</div>
                            <div class="stat-value">${categoryCount}</div>
                            <div>个分类</div>
                        </div>
                        <div class="stat-card">
                            <div>今日点餐</div>
                            <div class="stat-value">${todayOrders}</div>
                            <div>个订单</div>
                        </div>
                    `;
                } catch (error) {
                    console.log('加载统计数据失败:', error);
                }
            }

            // 更新时间显示
            function updateTime() {
                const now = new Date();
                const timeStr = now.toLocaleString('zh-CN', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: false
                });
                document.getElementById('currentTime').textContent = timeStr;
            }

            // 页面加载时初始化
            document.addEventListener('DOMContentLoaded', () => {
                loadStats();
                updateTime();
                setInterval(updateTime, 1000);
                setInterval(loadStats, 30000);
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# ==================== 菜谱管理接口 ====================

@app.get("/api/recipes", tags=["菜谱管理"])
async def get_all_recipes(
        category: Optional[str] = Query(None, description="按分类筛选"),
        page: int = Query(1, ge=1, description="页码，从1开始"),
        limit: int = Query(20, ge=1, le=100, description="每页数量，最大100")
):
    """获取菜谱列表"""
    recipes = load_recipes()

    if category:
        recipes = [r for r in recipes if r.get("category") == category]

    total = len(recipes)
    start = (page - 1) * limit
    end = start + limit
    paginated_recipes = recipes[start:end]

    return {
        "success": True,
        "data": paginated_recipes,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        },
        "count": total
    }


@app.get("/api/recipes/{recipe_id}", tags=["菜谱管理"])
async def get_single_recipe(recipe_id: str):
    """获取单个菜谱详情"""
    recipe = get_recipe_by_id(recipe_id)
    if recipe:
        return {"success": True, "data": recipe}
    raise HTTPException(status_code=404, detail=f"菜谱ID '{recipe_id}' 不存在")


@app.post("/api/recipes", tags=["菜谱管理"])
async def create_new_recipe(
        name: str = Form(..., description="菜谱名称（必填）"),
        category: str = Form("未分类", description="菜谱分类"),
        prep_time: int = Form(0, ge=0, description="准备时间（分钟）"),
        ingredients: str = Form("", description="食材清单，每行一个"),
        steps: str = Form("", description="制作步骤，每行一步"),
        tags: str = Form("", description="标签，用逗号分隔"),
        price: float = Form(0, ge=0, description="价格"),
        image: UploadFile = File(None, description="菜谱图片（可选）")
):
    """创建新菜谱"""
    image_url = None
    if image and image.filename:
        try:
            image_url = await save_uploaded_image(image)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"图片处理失败: {str(e)}")

    recipe_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    recipe = {
        "id": recipe_id,
        "name": name.strip(),
        "category": category.strip() or "未分类",
        "prep_time": prep_time,
        "ingredients": [i.strip() for i in ingredients.split("\n") if i.strip()],
        "steps": [s.strip() for s in steps.split("\n") if s.strip()],
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "price": price,
        "image_url": image_url,
        "created_at": timestamp,
        "updated_at": timestamp
    }

    recipes = load_recipes()
    recipes.append(recipe)
    save_recipes(recipes)

    return {
        "success": True,
        "message": "菜谱创建成功",
        "data": recipe
    }


@app.put("/api/recipes/{recipe_id}", tags=["菜谱管理"])
async def update_existing_recipe(
        recipe_id: str,
        name: Optional[str] = Form(None, description="菜谱名称"),
        category: Optional[str] = Form(None, description="菜谱分类"),
        prep_time: Optional[int] = Form(None, ge=0, description="准备时间（分钟）"),
        ingredients: Optional[str] = Form(None, description="食材清单"),
        steps: Optional[str] = Form(None, description="制作步骤"),
        tags: Optional[str] = Form(None, description="标签"),
        price: Optional[float] = Form(None, ge=0, description="价格"),
        image: Optional[UploadFile] = File(None, description="菜谱图片")
):
    """更新菜谱"""
    recipes = load_recipes()

    for i, recipe in enumerate(recipes):
        if recipe.get("id") == recipe_id:
            if name is not None:
                recipes[i]["name"] = name.strip()
            if category is not None:
                recipes[i]["category"] = category.strip()
            if prep_time is not None:
                recipes[i]["prep_time"] = prep_time
            if ingredients is not None:
                recipes[i]["ingredients"] = [i.strip() for i in ingredients.split("\n") if i.strip()]
            if steps is not None:
                recipes[i]["steps"] = [s.strip() for s in steps.split("\n") if s.strip()]
            if tags is not None:
                recipes[i]["tags"] = [t.strip() for t in tags.split(",") if t.strip()]
            if price is not None:
                recipes[i]["price"] = price

            if image and image.filename:
                delete_recipe_image(recipes[i].get("image_url"))
                try:
                    image_url = await save_uploaded_image(image)
                    recipes[i]["image_url"] = image_url
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"图片更新失败: {str(e)}")

            recipes[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_recipes(recipes)
            return {
                "success": True,
                "message": "菜谱更新成功",
                "data": recipes[i]
            }

    raise HTTPException(status_code=404, detail=f"菜谱ID '{recipe_id}' 不存在")


@app.delete("/api/recipes/{recipe_id}", tags=["菜谱管理"])
async def delete_recipe(recipe_id: str):
    """删除菜谱"""
    recipes = load_recipes()

    for i, recipe in enumerate(recipes):
        if recipe.get("id") == recipe_id:
            delete_recipe_image(recipe.get("image_url"))
            deleted_recipe = recipes.pop(i)
            save_recipes(recipes)
            return {
                "success": True,
                "message": "菜谱删除成功",
                "data": deleted_recipe
            }

    raise HTTPException(status_code=404, detail=f"菜谱ID '{recipe_id}' 不存在")


# ==================== 点餐管理接口 ====================

@app.get("/api/orders", tags=["点餐管理"])
async def get_all_orders(
        status: Optional[str] = Query(None, description="按状态筛选"),
        customer_name: Optional[str] = Query(None, description="按客户名筛选"),
        page: int = Query(1, ge=1, description="页码"),
        limit: int = Query(20, ge=1, le=100, description="每页数量")
):
    """获取点餐列表"""
    orders = load_orders()

    # 筛选
    if status:
        orders = [o for o in orders if o.get("status") == status]
    if customer_name:
        orders = [o for o in orders if customer_name.lower() in o.get("customer_name", "").lower()]

    # 按创建时间倒序排序
    orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    # 分页
    total = len(orders)
    start = (page - 1) * limit
    end = start + limit
    paginated_orders = orders[start:end]

    return {
        "success": True,
        "data": paginated_orders,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        },
        "count": total
    }


@app.get("/api/orders/{order_id}", tags=["点餐管理"])
async def get_single_order(order_id: str):
    """获取单个点餐详情"""
    orders = load_orders()
    for order in orders:
        if order.get("id") == order_id:
            return {"success": True, "data": order}

    raise HTTPException(status_code=404, detail=f"点餐ID '{order_id}' 不存在")


@app.post("/api/orders", tags=["点餐管理"])
async def create_new_order(
        customer_name: str = Form(..., description="客户名称（必填）"),
        table_number: Optional[str] = Form(None, description="桌号"),
        people_count: int = Form(..., ge=1, description="用餐人数"),
        dining_time: str = Form(..., description="用餐时间，格式：YYYY-MM-DD HH:MM"),
        notes: Optional[str] = Form(None, description="备注信息")
):
    """创建新点餐"""
    try:
        # 验证用餐时间格式
        dining_datetime = datetime.strptime(dining_time, "%Y-%m-%d %H:%M")
        if dining_datetime < datetime.now():
            raise HTTPException(status_code=400, detail="用餐时间不能是过去时间")
    except ValueError:
        raise HTTPException(status_code=400, detail="用餐时间格式错误，请使用 YYYY-MM-DD HH:MM 格式")

    order_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    order = {
        "id": order_id,
        "customer_name": customer_name.strip(),
        "table_number": table_number.strip() if table_number else None,
        "people_count": people_count,
        "dining_time": dining_time,
        "status": OrderStatus.PENDING.value,
        "notes": notes.strip() if notes else None,
        "items": [],  # 点餐项目列表
        "total_price": 0,
        "total_items": 0,
        "created_at": timestamp,
        "updated_at": timestamp
    }

    orders = load_orders()
    orders.append(order)
    save_orders(orders)

    return {
        "success": True,
        "message": "点餐创建成功",
        "data": order
    }


@app.put("/api/orders/{order_id}", tags=["点餐管理"])
async def update_order(
        order_id: str,
        customer_name: Optional[str] = Form(None, description="客户名称"),
        table_number: Optional[str] = Form(None, description="桌号"),
        people_count: Optional[int] = Form(None, ge=1, description="用餐人数"),
        dining_time: Optional[str] = Form(None, description="用餐时间"),
        status: Optional[str] = Form(None, description="订单状态"),
        notes: Optional[str] = Form(None, description="备注")
):
    """更新点餐信息"""
    orders = load_orders()

    for i, order in enumerate(orders):
        if order.get("id") == order_id:
            if customer_name is not None:
                orders[i]["customer_name"] = customer_name.strip()
            if table_number is not None:
                orders[i]["table_number"] = table_number.strip() if table_number else None
            if people_count is not None:
                orders[i]["people_count"] = people_count
            if dining_time is not None:
                try:
                    datetime.strptime(dining_time, "%Y-%m-%d %H:%M")
                    orders[i]["dining_time"] = dining_time
                except ValueError:
                    raise HTTPException(status_code=400, detail="用餐时间格式错误")
            if status is not None:
                if status in [s.value for s in OrderStatus]:
                    orders[i]["status"] = status
                else:
                    raise HTTPException(status_code=400, detail="无效的状态值")
            if notes is not None:
                orders[i]["notes"] = notes.strip() if notes else None

            orders[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_orders(orders)
            return {
                "success": True,
                "message": "点餐更新成功",
                "data": orders[i]
            }

    raise HTTPException(status_code=404, detail=f"点餐ID '{order_id}' 不存在")


@app.delete("/api/orders/{order_id}", tags=["点餐管理"])
async def delete_order(order_id: str):
    """删除点餐"""
    orders = load_orders()

    for i, order in enumerate(orders):
        if order.get("id") == order_id:
            deleted_order = orders.pop(i)
            save_orders(orders)
            return {
                "success": True,
                "message": "点餐删除成功",
                "data": deleted_order
            }

    raise HTTPException(status_code=404, detail=f"点餐ID '{order_id}' 不存在")


@app.post("/api/orders/{order_id}/items", tags=["点餐管理"])
async def add_order_item(
        order_id: str,
        recipe_id: str = Form(..., description="菜谱ID"),
        quantity: int = Form(1, ge=1, description="数量"),
        notes: Optional[str] = Form(None, description="备注")
):
    """向点餐中添加菜谱项目"""
    # 验证菜谱是否存在
    recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail=f"菜谱ID '{recipe_id}' 不存在")

    orders = load_orders()
    order_found = False

    for i, order in enumerate(orders):
        if order.get("id") == order_id:
            order_found = True

            # 检查是否已存在相同菜谱
            item_id = str(uuid.uuid4())
            for item in orders[i]["items"]:
                if item.get("recipe_id") == recipe_id:
                    # 如果已存在，增加数量
                    item["quantity"] += quantity
                    if notes:
                        item["notes"] = notes

                    # 更新总价和总项目数
                    orders[i]["total_price"] = sum(item.get("price", 0) * item.get("quantity", 1)
                                                   for item in orders[i]["items"])
                    orders[i]["total_items"] = sum(item.get("quantity", 1)
                                                   for item in orders[i]["items"])
                    orders[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    save_orders(orders)
                    return {
                        "success": True,
                        "message": "菜谱数量已更新",
                        "data": orders[i]
                    }

            # 如果不存在，添加新项目
            new_item = {
                "id": item_id,
                "recipe_id": recipe_id,
                "recipe_name": recipe.get("name"),
                "quantity": quantity,
                "notes": notes.strip() if notes else None,
                "price": recipe.get("price", 0),
                "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            orders[i]["items"].append(new_item)
            orders[i]["total_price"] = sum(item.get("price", 0) * item.get("quantity", 1)
                                           for item in orders[i]["items"])
            orders[i]["total_items"] = sum(item.get("quantity", 1)
                                           for item in orders[i]["items"])
            orders[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            save_orders(orders)
            return {
                "success": True,
                "message": "菜谱已添加到点餐",
                "data": new_item
            }

    if not order_found:
        raise HTTPException(status_code=404, detail=f"点餐ID '{order_id}' 不存在")


@app.delete("/api/orders/{order_id}/items/{item_id}", tags=["点餐管理"])
async def remove_order_item(order_id: str, item_id: str):
    """从点餐中移除菜谱项目"""
    orders = load_orders()

    for i, order in enumerate(orders):
        if order.get("id") == order_id:
            for j, item in enumerate(orders[i]["items"]):
                if item.get("id") == item_id:
                    removed_item = orders[i]["items"].pop(j)

                    # 更新总价和总项目数
                    orders[i]["total_price"] = sum(item.get("price", 0) * item.get("quantity", 1)
                                                   for item in orders[i]["items"])
                    orders[i]["total_items"] = sum(item.get("quantity", 1)
                                                   for item in orders[i]["items"])
                    orders[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    save_orders(orders)
                    return {
                        "success": True,
                        "message": "菜谱项目已移除",
                        "data": removed_item
                    }

            raise HTTPException(status_code=404, detail=f"项目ID '{item_id}' 不存在")

    raise HTTPException(status_code=404, detail=f"点餐ID '{order_id}' 不存在")


@app.put("/api/orders/{order_id}/items/{item_id}", tags=["点餐管理"])
async def update_order_item(
        order_id: str,
        item_id: str,
        quantity: Optional[int] = Form(None, ge=1, description="数量"),
        notes: Optional[str] = Form(None, description="备注")
):
    """更新点餐项目的数量或备注"""
    orders = load_orders()

    for i, order in enumerate(orders):
        if order.get("id") == order_id:
            for j, item in enumerate(orders[i]["items"]):
                if item.get("id") == item_id:
                    if quantity is not None:
                        orders[i]["items"][j]["quantity"] = quantity
                    if notes is not None:
                        orders[i]["items"][j]["notes"] = notes.strip() if notes else None

                    # 更新总价和总项目数
                    orders[i]["total_price"] = sum(item.get("price", 0) * item.get("quantity", 1)
                                                   for item in orders[i]["items"])
                    orders[i]["total_items"] = sum(item.get("quantity", 1)
                                                   for item in orders[i]["items"])
                    orders[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    save_orders(orders)
                    return {
                        "success": True,
                        "message": "项目更新成功",
                        "data": orders[i]["items"][j]
                    }

            raise HTTPException(status_code=404, detail=f"项目ID '{item_id}' 不存在")

    raise HTTPException(status_code=404, detail=f"点餐ID '{order_id}' 不存在")


# ==================== 其他功能接口 ====================

@app.get("/api/categories", tags=["分类管理"])
async def get_all_categories():
    """获取所有分类及统计"""
    recipes = load_recipes()

    categories = {}
    for recipe in recipes:
        category = recipe.get("category", "未分类")
        categories[category] = categories.get(category, 0) + 1

    return {
        "success": True,
        "data": categories,
        "count": len(categories)
    }


@app.get("/api/search", tags=["搜索功能"])
async def search_recipes(
        keyword: str = Query(..., description="搜索关键词"),
        search_in: str = Query("all", description="搜索范围：all, name, category, ingredients, steps")
):
    """搜索菜谱"""
    recipes = load_recipes()
    keyword_lower = keyword.lower().strip()

    if not keyword_lower:
        return {
            "success": True,
            "data": recipes,
            "count": len(recipes)
        }

    results = []
    for recipe in recipes:
        should_include = False

        if search_in == "all":
            name_match = keyword_lower in recipe.get("name", "").lower()
            category_match = keyword_lower in recipe.get("category", "").lower()
            tags_match = any(keyword_lower in tag.lower() for tag in recipe.get("tags", []))
            ingredients_match = any(keyword_lower in ingredient.lower() for ingredient in recipe.get("ingredients", []))
            steps_match = any(keyword_lower in step.lower() for step in recipe.get("steps", []))
            should_include = name_match or category_match or tags_match or ingredients_match or steps_match
        elif search_in == "name":
            should_include = keyword_lower in recipe.get("name", "").lower()
        elif search_in == "category":
            should_include = keyword_lower in recipe.get("category", "").lower()
        elif search_in == "ingredients":
            should_include = any(keyword_lower in ingredient.lower() for ingredient in recipe.get("ingredients", []))
        elif search_in == "steps":
            should_include = any(keyword_lower in step.lower() for step in recipe.get("steps", []))

        if should_include:
            results.append(recipe)

    return {
        "success": True,
        "data": results,
        "count": len(results),
        "keyword": keyword,
        "search_in": search_in
    }


@app.get("/api/orders/search", tags=["搜索功能"])
async def search_orders(
        keyword: str = Query(..., description="搜索关键词"),
        search_in: str = Query("customer_name", description="搜索范围：customer_name, table_number, notes")
):
    """搜索点餐"""
    orders = load_orders()
    keyword_lower = keyword.lower().strip()

    if not keyword_lower:
        return {
            "success": True,
            "data": orders,
            "count": len(orders)
        }

    results = []
    for order in orders:
        should_include = False

        if search_in == "customer_name":
            should_include = keyword_lower in order.get("customer_name", "").lower()
        elif search_in == "table_number":
            table_num = order.get("table_number", "")
            if table_num:
                should_include = keyword_lower in table_num.lower()
        elif search_in == "notes":
            notes = order.get("notes", "")
            if notes:
                should_include = keyword_lower in notes.lower()

        if should_include:
            results.append(order)

    return {
        "success": True,
        "data": results,
        "count": len(results),
        "keyword": keyword,
        "search_in": search_in
    }


@app.get("/api/statistics", tags=["统计功能"])
async def get_system_statistics():
    """获取系统统计数据"""
    recipes = load_recipes()
    orders = load_orders()

    # 菜谱统计
    total_recipes = len(recipes)
    categories = {}
    total_prep_time = 0
    with_images = 0

    for recipe in recipes:
        category = recipe.get("category", "未分类")
        categories[category] = categories.get(category, 0) + 1
        total_prep_time += recipe.get("prep_time", 0)
        if recipe.get("image_url"):
            with_images += 1

    # 点餐统计
    total_orders = len(orders)
    order_statuses = {}
    total_revenue = 0
    total_people = 0

    for order in orders:
        status = order.get("status", "unknown")
        order_statuses[status] = order_statuses.get(status, 0) + 1
        total_revenue += order.get("total_price", 0)
        total_people += order.get("people_count", 0)

    # 今日统计
    today = datetime.now().strftime("%Y-%m-%d")
    today_orders = [o for o in orders if o.get("created_at", "").startswith(today)]
    today_revenue = sum(o.get("total_price", 0) for o in today_orders)

    return {
        "success": True,
        "data": {
            "recipes": {
                "total": total_recipes,
                "categories": categories,
                "category_count": len(categories),
                "average_prep_time": round(total_prep_time / total_recipes, 1) if total_recipes > 0 else 0,
                "with_images": with_images,
                "without_images": total_recipes - with_images,
                "image_percentage": round(with_images / total_recipes * 100, 1) if total_recipes > 0 else 0,
            },
            "orders": {
                "total": total_orders,
                "status_distribution": order_statuses,
                "total_revenue": round(total_revenue, 2),
                "average_revenue": round(total_revenue / total_orders, 2) if total_orders > 0 else 0,
                "total_people": total_people,
                "average_people": round(total_people / total_orders, 1) if total_orders > 0 else 0,
                "today_orders": len(today_orders),
                "today_revenue": round(today_revenue, 2)
            },
            "system": {
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_files": {
                    "recipes": DATA_FILE,
                    "orders": ORDERS_FILE
                },
                "upload_dir": UPLOAD_DIR
            }
        }
    }


@app.get("/api/orders/statistics/today", tags=["统计功能"])
async def get_today_order_statistics():
    """获取今日点餐统计"""
    orders = load_orders()
    today = datetime.now().strftime("%Y-%m-%d")

    today_orders = [o for o in orders if o.get("created_at", "").startswith(today)]
    today_revenue = sum(o.get("total_price", 0) for o in today_orders)

    return {
        "success": True,
        "data": {
            "today": today,
            "order_count": len(today_orders),
            "total_revenue": round(today_revenue, 2),
            "average_revenue": round(today_revenue / len(today_orders), 2) if today_orders else 0,
            "orders": today_orders
        }
    }


@app.get("/api/orders/statistics/status", tags=["统计功能"])
async def get_order_status_statistics():
    """获取点餐状态统计"""
    orders = load_orders()

    status_stats = {}
    for order in orders:
        status = order.get("status", "unknown")
        status_stats[status] = status_stats.get(status, 0) + 1

    return {
        "success": True,
        "data": status_stats,
        "total": len(orders)
    }


@app.get("/api/health", tags=["统计功能"])
async def health_check():
    """健康检查"""
    try:
        recipes = load_recipes()
        orders = load_orders()

        return {
            "status": "healthy",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stats": {
                "recipes": len(recipes),
                "orders": len(orders),
                "data_files": {
                    "recipes": os.path.exists(DATA_FILE),
                    "orders": os.path.exists(ORDERS_FILE)
                },
                "upload_dir": os.path.exists(UPLOAD_DIR)
            },
            "message": "系统运行正常"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )


# ==================== 启动服务器 ====================

if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("🚀 菜谱与点餐管理系统 API")
    print("=" * 70)
    print(f"📁 菜谱数据: {os.path.abspath(DATA_FILE)}")
    print(f"📁 点餐数据: {os.path.abspath(ORDERS_FILE)}")
    print(f"🖼️  上传目录: {os.path.abspath(UPLOAD_DIR)}")
    print("=" * 70)
    print("🌐 访问地址:")
    print("  http://localhost:8000")
    print("  http://localhost:8000/docs  (Swagger UI)")
    print("  http://localhost:8000/redoc (ReDoc)")
    print("=" * 70)
    print("⚡ 启动服务器...")
    print("=" * 70)

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )