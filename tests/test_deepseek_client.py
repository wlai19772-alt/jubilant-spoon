from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.config import Config


def test_config_uses_deepseek_defaults(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text('{"openai_api_key": "demo-key"}', encoding="utf-8")

    config = Config(config_path)

    assert config.get("deepseek_api_key") == "demo-key"
    assert config.get("openai_model") == "deepseek-chat"
