"""
script_generator.py

这个模块负责主流程：读取剧本、加载 Prompt、调用 AI、保存结果。
它把核心业务逻辑集中在一个模块里，方便后续扩展。
"""

from pathlib import Path

from src.config import Config
from src.prompt_manager import PromptManager
from src.reader.txt_reader import TxtReader
from src.ai.openai_client import OpenAIClient
from src.exporter.word_exporter import WordExporter
from src.logger import create_logger
from src.errors import ConfigError, PromptError, ReadError, AIError, ExportError


class ScriptGenerator:
    """AI 剧本生成主流程。"""

    def __init__(
        self,
        config_path: Path,
        prompt_dir: Path,
        input_file: Path,
        output_dir: Path,
        log_file: Path,
    ):
        self.config = Config(config_path)
        self.prompt_manager = PromptManager(prompt_dir)
        self.input_file = input_file
        self.output_dir = output_dir
        self.logger = create_logger(log_file)

    def _build_fallback_content(self, script_text: str) -> str:
        """在 AI 不可用时生成一个可读的基础版剧本。"""
        lines = ["# 生成版剧本", ""]
        lines.append("根据输入内容整理出的基础剧本：")
        lines.append("")
        for line in script_text.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("角色"):
                lines.append(line)
            elif "：" in line:
                lines.append(line)
            else:
                lines.append(f"场景说明：{line}")
        lines.append("")
        lines.append("说明：当前未连接到 AI 服务，已使用离线模板生成基础版本。")
        return "\n".join(lines)

    def run(self):
        """执行从读取到导出的完整流程。"""
        self.logger.info("启动剧本生成流程")
        self.logger.info(f"读取文件：{self.input_file}")

        # 1) 读取输入文件
        try:
            reader = TxtReader(self.input_file)
            script_text = reader.read()
        except Exception as exc:
            self.logger.exception("读取剧本文件失败")
            raise ReadError(
                f"读取文件 {self.input_file} 失败：{exc}. 请检查文件是否存在且为 UTF-8 文本。"
            ) from exc

        # 2) 加载 Prompt
        try:
            prompt = self.prompt_manager.load_prompt("script_generation")
            prompt = prompt.replace("{script}", script_text)
        except FileNotFoundError as exc:
            self.logger.exception("Prompt 未找到")
            raise PromptError(
                "未找到名为 'script_generation' 的 Prompt 文件。请在 prompts/ 目录下添加 script_generation.txt。"
            ) from exc
        except Exception as exc:
            self.logger.exception("加载 Prompt 失败")
            raise PromptError(
                f"加载 Prompt 失败：{exc}. 请检查 prompts 目录和文件权限。"
            ) from exc

        # 3) 调用 AI
        api_key = self.config.get("deepseek_api_key") or self.config.get("openai_api_key")
        model = self.config.get("openai_model")
        provider = self.config.get("ai_provider", "deepseek")
        try:
            if not api_key:
                raise AIError("未配置 DeepSeek API Key")
            ai_client = OpenAIClient(api_key, model)
            self.logger.info(f"调用 {provider} 生成内容")
            result = ai_client.generate(prompt)
        except AIError as exc:
            self.logger.warning(f"AI 调用失败，使用离线兜底内容：{exc}")
            result = self._build_fallback_content(script_text)
        except Exception as exc:
            self.logger.exception("AI 调用出现未知错误")
            result = self._build_fallback_content(script_text)

        # 4) 导出结果
        try:
            exporter = WordExporter(self.output_dir)
            output_file = exporter.export(result, "generated_script")
            self.logger.info(f"生成文件：{output_file}")
            self.logger.info("剧本生成完成")
            return output_file
        except Exception as exc:
            self.logger.exception("导出文件失败")
            raise ExportError(
                f"导出文件失败：{exc}. 请检查输出目录权限与磁盘空间。"
            ) from exc
