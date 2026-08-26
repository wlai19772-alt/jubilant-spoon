"""
txt_reader.py

这个模块负责读取 TXT 文件内容。
当前只支持 TXT，将来可以在这个目录下增加 Word、PDF 阅读器。
"""

from pathlib import Path


class TxtReader:
    """TXT 文件读取类。"""

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def read(self) -> str:
        """读取 TXT 文件并返回文本内容。"""
        with self.file_path.open("r", encoding="utf-8") as file:
            return file.read()
