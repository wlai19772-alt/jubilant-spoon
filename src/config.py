"""
config.py

这个模块负责读取和提供项目的配置。
配置包括：API key、模型、目录路径、日志文件名等。
将配置独立出来，避免业务代码中写死参数。
"""

from pathlib import Path
import json
import os

from src.errors import ConfigError


class Config:
    """配置管理类。"""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.project_root = config_path.parent.parent
        self.data = self._load_config()
        self._apply_env_overrides()
        self._normalize_paths()
        self._validate()

    def _load_config(self) -> dict:
        """读取 JSON 配置文件并返回配置字典。"""
        if not self.config_path.exists():
            raise ConfigError(f"配置文件不存在：{self.config_path}")

        try:
            with self.config_path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as exc:
            raise ConfigError(
                f"配置文件 {self.config_path} 不是合法的 JSON: {exc}"
            ) from exc

    def _apply_env_overrides(self):
        """支持使用环境变量覆盖配置。"""
        env_mapping = {
            "openai_api_key": "OPENAI_API_KEY",
            "deepseek_api_key": "DEEPSEEK_API_KEY",
            "openai_model": "OPENAI_MODEL",
            "ai_provider": "AI_PROVIDER",
            "ai_base_url": "AI_BASE_URL",
            "prompt_dir": "PROMPT_DIR",
            "data_dir": "DATA_DIR",
            "output_dir": "OUTPUT_DIR",
            "log_dir": "LOG_DIR",
        }
        for key, env_name in env_mapping.items():
            env_value = os.getenv(env_name)
            # 环境变量应始终优先于文件配置，避免生产密钥被提交的配置覆盖。
            if env_value:
                self.data[key] = env_value

        if not self.data.get("deepseek_api_key") and self.data.get("openai_api_key"):
            self.data["deepseek_api_key"] = self.data["openai_api_key"]

    def _normalize_paths(self):
        """将目录配置规范为绝对路径。"""
        path_keys = {
            "prompt_dir": "prompts",
            "data_dir": "data",
            "output_dir": "output",
            "log_dir": "logs",
        }
        for key, default in path_keys.items():
            raw_value = self.data.get(key, default)
            path = Path(raw_value)
            if not path.is_absolute():
                path = self.project_root / path
            self.data[key] = str(path)

    def _validate(self):
        """校验关键配置项是否存在。"""
        if not self.get("deepseek_api_key") and self.get("openai_api_key"):
            self.data["deepseek_api_key"] = self.get("openai_api_key")
        if not self.get("deepseek_api_key") and not self.get("openai_api_key"):
            self.data["deepseek_api_key"] = ""
        if not self.get("ai_provider"):
            self.data["ai_provider"] = "deepseek"
        if not self.get("ai_base_url"):
            self.data["ai_base_url"] = (
                "https://api.openai.com/v1"
                if self.get("ai_provider") == "openai"
                else "https://api.deepseek.com"
            )
        if not self.get("openai_model"):
            self.data["openai_model"] = "deepseek-chat"

    def get(self, key: str, default=None):
        """根据 key 获取配置值，如果不存在则返回默认值。"""
        return self.data.get(key, default)

    def get_path(self, key: str, default=None) -> Path:
        """获取目录配置并返回 Path 对象。"""
        value = self.get(key, default)
        return Path(value) if value is not None else None
