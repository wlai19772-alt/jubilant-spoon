"""
parser.py

集纲解析模块。
负责解析集纲文档，提取每集的剧情内容。
"""

from pathlib import Path
from typing import Dict, List, Optional
import re


class OutlineParser:
    """集纲解析器。"""

    def __init__(self, outline_file: Path):
        self.outline_file = outline_file

    def parse(self) -> List[Dict[str, str]]:
        """解析集纲文件，返回每集的剧情列表。"""
        if not self.outline_file.exists():
            raise FileNotFoundError(f"集纲文件不存在：{self.outline_file}")

        with open(self.outline_file, "r", encoding="utf-8") as f:
            content = f.read()

        episodes = []
        current_episode = None
        current_content = []

        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            
            # 检测集数标记
            match = re.match(r"^第\s*(\d+)\s*集(?:[：:：\s]|$)", line)
            if match:
                # 保存上一集
                if current_episode:
                    episodes.append({
                        "episode": current_episode,
                        "content": "\n".join(current_content).strip()
                    })
                
                # 开始新一集
                current_episode = match.group(1)
                current_content = []
            elif current_episode:
                current_content.append(line)
        
        # 保存最后一集
        if current_episode:
            episodes.append({
                "episode": current_episode,
                "content": "\n".join(current_content).strip()
            })

        return episodes

    def get_episode(self, episode_num: int) -> Optional[str]:
        """获取指定集数的集纲内容。"""
        episodes = self.parse()
        for ep in episodes:
            if str(episode_num) == ep["episode"]:
                return ep["content"]
        return None


class CharacterParser:
    """人设解析器。"""

    def __init__(self, character_file: Path):
        self.character_file = character_file

    def parse(self) -> Dict[str, str]:
        """解析人设文件，返回人物字典。"""
        if not self.character_file.exists():
            raise FileNotFoundError(f"人设文件不存在：{self.character_file}")

        characters = {}
        current_character = None
        current_description = []

        with open(self.character_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                
                # 检测人物名称（以冒号结尾）
                if line.endswith("：") or line.endswith(":"):
                    # 保存上一个人物
                    if current_character:
                        characters[current_character] = "\n".join(current_description).strip()
                    
                    # 开始新人物
                    current_character = line[:-1].strip()
                    current_description = []
                elif current_character:
                    current_description.append(line)
        
        # 保存最后一个人物
        if current_character:
            characters[current_character] = "\n".join(current_description).strip()

        return characters

    def get_character_bio(self, character_name: str) -> Optional[str]:
        """获取指定人物的人设描述。"""
        characters = self.parse()
        return characters.get(character_name)

    def get_all_characters(self) -> List[str]:
        """获取所有人物名称列表。"""
        characters = self.parse()
        return list(characters.keys())

    def format_for_prompt(self) -> str:
        """将人设格式化为适合提示词的字符串。"""
        characters = self.parse()
        lines = []
        for name, desc in characters.items():
            lines.append(f"{name}：{desc}")
        return "\n".join(lines)
