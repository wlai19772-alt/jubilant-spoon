from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.prompt_manager import PromptManager
from src.generator.script_generator import ScriptGenerator


def run():
    pm = PromptManager(project_root / "prompts")
    print("Available prompts:", pm.list_prompts())
    content = pm.load_prompt("script_generation", {"script": "测试剧本文本"})
    print("Loaded prompt content:\n", content)
    meta = pm.get_metadata("script_generation")
    print("Metadata:", meta)


def test_script_generator_can_fallback_without_api_key(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text('{"openai_api_key": "", "openai_model": "gpt-3.5-turbo"}', encoding="utf-8")

    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    (prompt_dir / "script_generation.txt").write_text(
        "请改写这个剧本：{script}",
        encoding="utf-8",
    )

    input_file = tmp_path / "input.txt"
    input_file.write_text("角色：Alice 和 Bob。\nAlice：你好。", encoding="utf-8")

    output_dir = tmp_path / "output"
    log_file = tmp_path / "app.log"

    generator = ScriptGenerator(
        config_path=config_path,
        prompt_dir=prompt_dir,
        input_file=input_file,
        output_dir=output_dir,
        log_file=log_file,
    )

    output_file = generator.run()

    assert output_file.exists()
    assert output_file.suffix == ".docx"


if __name__ == '__main__':
    run()
