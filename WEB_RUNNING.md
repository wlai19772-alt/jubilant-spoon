# Web 版运行说明

本文件说明如何启动并使用 AI 剧本工厂的 Web 界面版本。

## 架构概述

- **后端**：Flask REST API (`src/api.py` + `app.py`)
- **前端**：纯 HTML5/CSS3/JavaScript SPA (`web/index.html`)
- **通信**：HTTP JSON
- **无需额外依赖**：后端只需 Flask 和 Flask-CORS；前端完全客户端渲染

## 快速启动

### 1. 准备环境

确保已安装依赖（包括新增的 Flask）：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置 API Key

设置环境变量或在 `config/config.json` 中填写：

```bash
export OPENAI_API_KEY="你的_key"
export DEEPSEEK_API_KEY="你的_key"
```

### 3. 启动 Web 应用

在项目根目录运行：

```bash
python app.py
```

或：

```bash
python -m flask --app src.api run
```

### 4. 访问网页

打开浏览器，访问：

```
http://localhost:8080
```

## Web 界面功能

### 输入面板（📝 输入 Tab）

- **剧本文本框**：粘贴或输入你要处理的剧本
- **生成类型下拉**：选择生成方式（展开剧本、修改风格、生成总结、自定义）
- **模型选择**：可选，留空使用默认配置
- **生成按钮**：触发 AI 生成
- **清空按钮**：清除所有输入

### 输出面板（📤 输出 Tab）

- 显示生成结果
- **复制按钮**：一键复制输出内容
- 包含生成时间戳和类型标记

### 提示词编辑器（侧边栏）

- **自定义提示词区域**：编写或粘贴自定义 prompt
- **预设模板按钮**：快速加载常用提示词
- **实时预览**：显示当前使用的提示词

## API 端点

### 健康检查

```bash
GET /api/v1/health
```

返回：`{"status": "ok", "message": "..."}`

### 获取生成类型

```bash
GET /api/v1/generation-types
```

返回：

```json
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

### 获取所有提示词

```bash
GET /api/v1/prompts
```

### 生成脚本

```bash
POST /api/v1/generate
Content-Type: application/json

{
  "input_text": "剧本文本",
  "prompt": "自定义提示词（可选）",
  "generation_type": "expand",
  "model": "default"
}
```

返回：

```json
{
  "success": true,
  "data": {
    "output": "生成的内容...",
    "generation_type": "expand",
    "message": "生成成功（expand）",
    "model": "deepseek-chat"
  }
}
```

## 常见问题

### 问：打不开网页

**答**：
1. 确认服务已启动：检查终端是否显示 `Running on`
2. 检查防火墙：确保本地端口 5000 未被占用
3. 尝试刷新浏览器

### 问：生成一直加载或超时

**答**：
1. 检查 API Key 是否有效
2. 查看后端控制台错误日志
3. 检查网络和 API 配额

### 问：提示词编辑器不保存

**答**：提示词只在当前浏览会话有效，页面刷新会重置。可在侧边栏下方使用"预设模板"快速恢复。

### 问：如何部署到服务器

**答**：
1. 将 `.venv` 和 `config/config.json` 中的密钥迁移到环境变量
2. 使用生产服务器（如 Gunicorn）：
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 src.api:app
   ```
3. 配置反向代理（Nginx/Apache）
4. 启用 HTTPS

## 日志与调试

- **后端日志**：`logs/web.log`
- **前端日志**：浏览器开发者工具 → Console
- **调试模式**：默认已启用（`debug=True`），生产环境请改为 `False`

## 文件结构

```
编剧1/
├── app.py                    # Web 启动脚本
├── src/
│   ├── api.py               # Flask API 模块
│   ├── generator/           # 核心生成逻辑
│   ├── ai/                  # AI 客户端
│   └── ...
├── web/
│   └── index.html           # 前端单页应用
├── config/
│   └── config.json          # 配置文件
├── prompts/                 # 提示词库
├── data/                    # 输入示例
├── output/                  # 生成结果
└── logs/                    # 日志目录
```

## 下一步

- 自定义样式：编辑 `web/index.html` 中的 `<style>` 部分
- 扩展功能：在 `src/api.py` 中添加新接口
- 部署优化：使用生产级服务器和数据库存储

## 技术栈

- **后端**：Python 3.8+, Flask, Flask-CORS
- **前端**：HTML5, CSS3, Vanilla JavaScript (无框架依赖)
- **AI**：OpenAI API / DeepSeek API
- **服务器**：Flask 开发服务器 / Gunicorn (生产)
