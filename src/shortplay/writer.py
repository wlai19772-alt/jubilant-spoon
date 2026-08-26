"""
writer.py

正文创作模块。
负责根据集纲和人设创作单集剧本正文。
"""

from pathlib import Path
from typing import Dict, Optional
import sys

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.ai.openai_client import OpenAIClient
from src.prompt_manager import PromptManager
from src.config import Config
from src.logger import create_logger


class ScriptWriter:
    """剧本正文创作器。"""

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = project_root / "config" / "config.json"
        
        self.config = Config(config_path)
        self.prompt_manager = PromptManager(project_root / "prompts")
        self.logger = create_logger(project_root / "logs" / "shortplay.log")
        
        # 初始化 AI 客户端
        api_key = self.config.get("deepseek_api_key") or self.config.get("openai_api_key")
        model = self.config.get("openai_model", "deepseek-chat")
        self.ai_client = OpenAIClient(api_key, model)

    def write_episode(self, outline: str, character_bio: str, episode_num: int = 1,
                      previous_episode_content: str = "") -> str:
        """
        根据集纲和人设创作单集剧本正文。
        
        Args:
            outline: 集纲内容
            character_bio: 人物小传
            episode_num: 集数
        
        Returns:
            剧本正文
        """
        try:
            # 加载提示词模板
            prompt_text = self.prompt_manager.load_prompt("script_generation")
            
            # 替换占位符
            prompt_text = prompt_text.replace("{script}", outline)
            prompt_text = prompt_text.replace("{character_bio}", character_bio)
            if previous_episode_content:
                prompt_text += (
                    "\n\n【上一集结尾与已发生剧情】\n"
                    f"{previous_episode_content[-3000:]}"
                    "\n【衔接要求】\n承接上一集结尾，不重复已发生事件，保持人物关系与信息一致。"
                )
            
            # 调用 AI 生成
            self.logger.info(f"开始创作第 {episode_num} 集剧本")
            result = self.ai_client.generate(prompt_text)
            
            # 添加集数标题
            result = f"第{episode_num}集\n{result}"
            
            self.logger.info(f"第 {episode_num} 集剧本创作完成")
            return result
        
        except Exception as e:
            self.logger.exception(f"创作第 {episode_num} 集时发生错误")
            raise

    def save_episode(self, content: str, output_dir: Path, episode_num: int):
        """
        保存单集剧本到文件。
        
        Args:
            content: 剧本内容
            output_dir: 输出目录
            episode_num: 集数
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir / f"第{episode_num}集正文.txt"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info(f"第 {episode_num} 集剧本已保存到 {file_path}")
