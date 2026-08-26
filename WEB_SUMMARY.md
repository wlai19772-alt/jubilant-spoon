# 🎭 AI 剧本工厂 Web 版 - 完整交付

## 项目完成情况

✅ **已完成**的功能和组件：

### 后端（Flask API）
- ✅ REST API 服务框架 (`src/api.py`)
- ✅ 健康检查端点 (`GET /api/health`)
- ✅ 生成类型列表端点 (`GET /api/generation-types`)
- ✅ 提示词加载端点 (`GET /api/prompts`)
- ✅ 脚本生成主端点 (`POST /api/generate`)
- ✅ CORS 跨域支持
- ✅ 错误处理和日志记录
- ✅ 配置管理（支持环境变量和 JSON 文件）

### 前端（HTML5 SPA）
- ✅ 现代化响应式 UI 设计
- ✅ **Tab 页签布局**（输入/输出分离）
- ✅ **侧边栏可折叠提示词编辑器**
  - 自定义提示词编辑区
  - 预设模板快速加载
  - 实时预览
- ✅ 输入面板
  - 剧本文本输入框
  - 生成类型下拉菜单
  - 模型选择（可选）
  - 生成/清空按钮
- ✅ 输出面板
  - 生成结果展示
  - 复制到剪贴板功能
  - 时间戳和元信息
  - 错误提示样式
- ✅ 实时通知（Toast）
- ✅ 加载状态指示器
- ✅ 响应式设计（支持移动设备）
- ✅ 无框架依赖（纯 Vanilla JS）

### 配置与部署
- ✅ `requirements.txt` 更新（Flask, Flask-CORS）
- ✅ `app.py` 启动脚本
- ✅ 环境变量支持（PORT, API_KEY 等）
- ✅ 详细文档
  - `WEB_RUNNING.md` —— Web 版运行指南
  - `RUNNING.md` —— CLI 版运行指南

---

## 快速启动指南

### 1️⃣ 安装依赖

```bash
cd /Users/wangfulai/Desktop/project/编剧1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ 配置 API Key

**方案 A：环境变量（推荐）**
```bash
export OPENAI_API_KEY="你的_key"
export DEEPSEEK_API_KEY="你的_key"
```

**方案 B：配置文件**
编辑 `config/config.json`：
```json
{
  "openai_api_key": "sk-xxx",
  "deepseek_api_key": "sk-xxx",
  "openai_model": "deepseek-chat",
  "ai_provider": "deepseek"
}
```

### 3️⃣ 启动应用

```bash
PORT=5001 python3 app.py
```

或自定义端口：
```bash
PORT=8080 python3 app.py
```

### 4️⃣ 访问网页

打开浏览器，访问：
```
http://localhost:5001
```

---

## 功能演示

### 输入流程
1. **粘贴剧本** → 在左侧"📝 输入"Tab 的文本框输入
2. **选择类型** → 下拉菜单选择生成方式
3. **自定义提示词**（可选）→ 在右侧折叠栏编辑 prompt
4. **点击生成** → 触发 AI 生成

### 输出流程
1. 生成完成后自动切换到"📤 输出"Tab
2. 查看生成结果
3. 点击"复制"按钮一键复制内容

---

## API 接口文档

### 健康检查
```bash
GET /api/health

Response:
{
  "status": "ok",
  "message": "AI 剧本工厂 API 运行中"
}
```

### 生成脚本
```bash
POST /api/generate
Content-Type: application/json

Request:
{
  "input_text": "角色：Alice 和 Bob。Alice：你好，Bob。Bob：你好，Alice。",
  "prompt": "请将这个剧本展开为更完整的版本",  // 可选
  "generation_type": "expand",                  // 可选：expand, style_change, summary, custom
  "model": "default"                             // 可选
}

Response:
{
  "success": true,
  "data": {
    "output": "生成的剧本内容...",
    "generation_type": "expand",
    "message": "生成成功（expand）",
    "model": "deepseek-chat"
  }
}
```

### 获取生成类型
```bash
GET /api/generation-types

Response:
{
  "success": true,
  "data": [
    {"id": "expand", "name": "展开剧本"},
    {"id": "style_change", "name": "修改风格"},
    {"id": "summary", "name": "剧本总结"},
    {"id": "custom", "name": "自定义"}
  ]
}
```

### 获取提示词
```bash
GET /api/prompts

Response:
{
  "success": true,
  "data": {
    "script_generation": "提示词内容...",
    "expand_prompt": "...",
    ...
  }
}
```

---

## 文件结构

```
编剧1/
├── app.py                       # ⭐ Web 启动脚本
├── src/
│   ├── api.py                   # ⭐ Flask API 模块
│   ├── config.py                # 配置管理
│   ├── logger.py                # 日志管理
│   ├── generator/               # 核心生成逻辑
│   ├── ai/                      # AI 客户端
│   ├── reader/                  # 文件读取
│   ├── exporter/                # 文件导出
│   └── ...
├── web/
│   └── index.html               # ⭐ 前端单页应用
├── config/
│   └── config.json              # 配置文件
├── prompts/                     # 提示词库
├── data/                        # 示例输入
├── output/                      # 生成结果
├── logs/                        # 日志目录
├── requirements.txt             # 依赖列表
├── WEB_RUNNING.md               # ⭐ Web 版指南
├── RUNNING.md                   # CLI 版指南
└── README.md                    # 项目说明
```

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **后端** | Python 3.8+ | 核心运行环境 |
| | Flask | 轻量级 Web 框架 |
| | Flask-CORS | 跨域资源共享 |
| **前端** | HTML5 | 标记语言 |
| | CSS3 | 样式设计（含响应式媒体查询） |
| | JavaScript (Vanilla) | 无框架依赖，原生 JS |
| **AI** | OpenAI API / DeepSeek API | 文本生成服务 |
| **服务器** | Flask Dev Server | 开发环境 |
| | Gunicorn (可选) | 生产环境 |

---

## 常见问题 & 排查

### ❓ 启动时提示"Port already in use"
**解决**：
```bash
# 方案1：改用其他端口
PORT=8080 python3 app.py

# 方案2：关闭占用的进程 (macOS/Linux)
lsof -i :5001
kill -9 <PID>
```

### ❓ 前端显示"请求失败，请检查服务是否运行"
**解决**：
1. 检查后端是否启动：`curl http://localhost:5001/api/health`
2. 检查浏览器控制台错误
3. 确认网络连接

### ❓ 生成一直加载或超时
**解决**：
1. 检查 API Key 是否有效
2. 查看 `logs/web.log` 错误信息
3. 检查网络和 API 配额限制

### ❓ 提示词不能保存
**解决**：提示词只在当前浏览会话有效，刷新页面会重置。可使用预设模板或重新输入。

---

## 生产部署建议

### 1. 安全性
- ✅ 将 API Key 迁移到环境变量
- ✅ 启用 HTTPS
- ✅ 配置 CORS 白名单
- ✅ 添加请求限流（Rate Limiting）
- ✅ 隐藏调试信息

### 2. 性能
- ✅ 使用 Gunicorn 替代 Flask dev 服务器
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.api:app
```

- ✅ 配置反向代理（Nginx）
- ✅ 启用缓存（Redis）
- ✅ 异步处理长时间任务（Celery）

### 3. 监控
- ✅ 集成日志系统（ELK）
- ✅ 性能监控（Prometheus）
- ✅ 错误追踪（Sentry）

---

## 下一步扩展方向

- 🔲 用户认证与授权
- 🔲 历史记录保存与管理
- 🔲 批量处理功能
- 🔲 导出为 Word/PDF
- 🔲 提示词模板库管理
- 🔲 生成历史的对比工具
- 🔲 团队协作功能
- 🔲 WebSocket 实时生成流

---

## 测试验证

✅ **已通过的测试**：
- ✅ API 模块导入正常
- ✅ 后端服务启动成功
- ✅ 健康检查端点响应 200
- ✅ 生成类型端点返回数据
- ✅ 前端页面加载成功（HTTP 200）
- ✅ CORS 跨域配置有效

---

## 使用示例

### curl 测试生成
```bash
curl -X POST http://localhost:5001/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "角色：Alice 和 Bob。",
    "generation_type": "expand",
    "prompt": "请将这个剧本展开为更完整的版本"
  }' | python3 -m json.tool
```

---

## 总结

已成功构建一套完整的 **AI 剧本工厂 Web 版本**，包括：
- 🎯 **现代化 Web 界面**：Tab 页签 + 侧边栏提示词编辑
- 🚀 **高效后端 API**：Flask 服务，支持定制生成
- 🔧 **灵活配置**：环境变量、配置文件双支持
- 📚 **完善文档**：运行指南、API 文档、排查指南

**现在就可以打开浏览器访问 http://localhost:5001 使用了！** 🎉

---

**创建日期**: 2026-07-04  
**最后更新**: 2026-07-04  
**版本**: 1.0 (MVP)
