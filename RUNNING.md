# 运行说明

本文件说明如何在本地启动和运行该 AI 剧本工厂项目（MVP）。

## 前提
- macOS，已安装 Python 3.8+。
- 推荐使用虚拟环境隔离依赖。

## 快速开始（终端：zsh）

1. 在项目根目录下创建并激活虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 配置 API Key（推荐使用环境变量，避免将密钥提交到仓库）：

```bash
export OPENAI_API_KEY="你的_openai_key"
export DEEPSEEK_API_KEY="你的_deepseek_key"
```

或者可将密钥写入 [config/config.json](config/config.json)（不推荐在公共仓库中保留明文密钥）。

4. 运行程序：

```bash
python src/main.py
# 或
python -m src.main
```

## 默认路径说明
- 输入示例： [data/example.txt](data/example.txt)
- 输出目录： `output/`（生成的文件会写入此目录）
- 日志文件： [logs/app.log](logs/app.log)
- 配置文件： [config/config.json](config/config.json)
- Prompt 目录： [prompts/](prompts/)

## 常见问题与排查
- 配置读取失败：检查 [config/config.json](config/config.json) 或环境变量是否设置正确；详见 [logs/app.log](logs/app.log)。
- AI 服务调用失败：检查网络、API Key 是否有效、模型与配额限制。
- 输入文件读取错误：确认 [data/example.txt](data/example.txt) 存在且为 UTF-8 编码。

## 建议与安全
- 不要在版本控制中保留明文 API Key；使用环境变量或受保护的秘密管理方案。
- 若想将本项目部署到服务器，请先把 `config/config.json` 中的敏感信息迁移为环境变量或密钥管理服务。

## 下一步（可选）
- 我可以：
  - 将本次修改添加到 Git 提交（需要你授权执行 git 操作）。
  - 帮你运行一次示例（需要有效 API Key）。

