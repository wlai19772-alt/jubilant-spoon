#!/usr/bin/env python3
"""
app.py

Web 应用启动脚本。
在项目根目录运行：python app.py
"""

import sys
from pathlib import Path

# 项目路径设置
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.api import app

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    print(f"""
    ╔════════════════════════════════════════════╗
    ║      🎭 AI 剧本工厂 Web 版启动中...      ║
    ╠════════════════════════════════════════════╣
    ║ 🌐 访问地址: http://localhost:{port}        ║
    ║ 📝 API 根路径: http://localhost:{port}/api/v1║
    ║ 🩺 健康检查: http://localhost:{port}/api/v1/health║
    ║                                            ║
    ║ 按 Ctrl+C 停止服务                        ║
    ╚════════════════════════════════════════════╝
    """)
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=port)
