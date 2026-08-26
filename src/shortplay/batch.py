"""
batch.py

批量生成模块。
负责批量处理多集剧本的创作流程。
"""

from pathlib import Path
from typing import List, Dict, Optional
import sys

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.shortplay.parser import OutlineParser, CharacterParser
from src.shortplay.writer import ScriptWriter
from src.logger import create_logger


class BatchGenerator:
    """批量剧本生成器。"""

    def __init__(self, 
                 outline_file: Path, 
                 character_file: Path,
                 output_dir: Path,
                 config_path: Optional[Path] = None):
        """
        初始化批量生成器。
        
        Args:
            outline_file: 集纲文件路径
            character_file: 人设文件路径
            output_dir: 输出目录
            config_path: 配置文件路径（可选）
        """
        self.outline_file = outline_file
        self.character_file = character_file
        self.output_dir = output_dir
        self.logger = create_logger(project_root / "logs" / "batch.log")
        
        # 初始化解析器和创作器
        self.outline_parser = OutlineParser(outline_file)
        self.character_parser = CharacterParser(character_file)
        self.writer = ScriptWriter(config_path)
        
        # 缓存上一集内容用于剧情衔接
        self.last_episode_content = ""

    def _validate_files(self) -> bool:
        """验证必要文件是否存在。"""
        missing_files = []
        
        if not self.outline_file.exists():
            missing_files.append(str(self.outline_file))
        if not self.character_file.exists():
            missing_files.append(str(self.character_file))
        
        if missing_files:
            self.logger.error(f"缺少必要文件: {', '.join(missing_files)}")
            return False
        
        return True

    def generate_all(self, start_episode: int = 1, end_episode: Optional[int] = None) -> List[str]:
        """
        批量生成多集剧本。
        
        Args:
            start_episode: 开始集数
            end_episode: 结束集数（None 表示生成全部）
        
        Returns:
            生成的剧本文件路径列表
        """
        if not self._validate_files():
            return []
        
        try:
            # 解析集纲
            episodes = self.outline_parser.parse()
            self.logger.info(f"共解析到 {len(episodes)} 集集纲")
            
            # 解析人设
            character_bio = self.character_parser.format_for_prompt()
            self.logger.info(f"已加载 {len(self.character_parser.get_all_characters())} 个人物")
            
            # 创建输出目录
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成每一集
            output_files = []
            for episode in episodes:
                episode_num = int(episode["episode"])
                # 检查是否在指定范围内
                if episode_num < start_episode:
                    continue
                if end_episode and episode_num > end_episode:
                    break
                outline = episode["content"]
                
                self.logger.info(f"开始处理第 {episode_num} 集")
                
                # 创作剧本
                script_content = self.writer.write_episode(
                    outline=outline,
                    character_bio=character_bio,
                    episode_num=episode_num,
                    previous_episode_content=self.last_episode_content,
                )
                
                # 保存剧本
                output_path = self.output_dir / f"第{episode_num}集正文.txt"
                self.writer.save_episode(script_content, self.output_dir, episode_num)
                output_files.append(str(output_path))
                
                # 保存上一集内容用于衔接
                self.last_episode_content = script_content
                
                self.logger.info(f"第 {episode_num} 集处理完成")
            
            self.logger.info(f"批量生成完成，共生成 {len(output_files)} 集剧本")
            return output_files
        
        except Exception as e:
            self.logger.exception("批量生成过程中发生错误")
            raise

    def generate_single(self, episode_num: int) -> str:
        """
        生成单集剧本。
        
        Args:
            episode_num: 集数
        
        Returns:
            生成的剧本文件路径
        """
        if not self._validate_files():
            raise FileNotFoundError("缺少必要的集纲或人设文件")
        
        try:
            # 获取集纲
            outline = self.outline_parser.get_episode(episode_num)
            if not outline:
                raise ValueError(f"未找到第 {episode_num} 集的集纲")
            
            # 获取人设
            character_bio = self.character_parser.format_for_prompt()
            
            # 创作剧本
            script_content = self.writer.write_episode(
                outline=outline,
                character_bio=character_bio,
                episode_num=episode_num,
                previous_episode_content=self.last_episode_content,
            )
            
            # 保存剧本
            self.output_dir.mkdir(parents=True, exist_ok=True)
            output_path = self.output_dir / f"第{episode_num}集正文.txt"
            self.writer.save_episode(script_content, self.output_dir, episode_num)
            
            return str(output_path)
        
        except Exception as e:
            self.logger.exception(f"生成第 {episode_num} 集时发生错误")
            raise
