"""
prompt_manager.py

这个模块负责读取 prompts/ 目录中的 prompt 文本。
Prompt 文本独立保存，后续增加新 prompt 不需要改代码。
"""

from pathlib import Path
import json
from typing import Dict, Optional, List


class _SafeDict(dict):
    def __missing__(self, key):
        # 如果变量不存在，保留原占位符，避免 KeyError
        return "{" + key + "}"


class PromptManager:
    """Prompt 管理类。

    功能：
    - 列出可用的 prompt 名称（`list_prompts()`）
    - 加载指定 prompt（`load_prompt(name, variables)`），支持占位符替换
    - 读取可选的 prompt 元数据（`{name}.meta.json`）

    设计理由：Prompt 文本与元数据独立存放，便于非程序员直接编辑和版本控制。
    """

    def __init__(self, prompt_dir: Path):
        self.prompt_dir = Path(prompt_dir)

    def list_prompts(self) -> List[str]:
        """返回 prompts 目录下所有可用 prompt 名称（不含扩展名）。"""
        prompts = []
        if not self.prompt_dir.exists():
            return prompts
        for p in self.prompt_dir.iterdir():
            if p.suffix == ".txt":
                prompts.append(p.stem)
        return sorted(prompts)

    def _meta_path(self, name: str) -> Path:
        return self.prompt_dir / f"{name}.meta.json"

    def get_metadata(self, name: str) -> Optional[Dict]:
        """如果存在 `{name}.meta.json`，返回解析后的元数据字典，否则返回 None。"""
        meta_path = self._meta_path(name)
        if not meta_path.exists():
            return None
        try:
            with meta_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def load_prompt(self, name: str, variables: Optional[Dict] = None) -> str:
        """读取指定名称的 prompt 文件内容并返回。

        - `variables`：可选字典，用于替换 prompt 中的占位符 `{var}`。
        - 未提供的占位符会被保留为原样，避免 KeyError。
        """
        prompt_path = self.prompt_dir / f"{name}.txt"
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt 文件不存在：{prompt_path}")

        with prompt_path.open("r", encoding="utf-8") as file:
            content = file.read()

        if variables:
            try:
                content = content.format_map(_SafeDict(variables))
            except Exception:
                # 如果格式替换失败，返回原始内容并让上层决定如何处理
                return content

        return content
