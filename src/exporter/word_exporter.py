"""
word_exporter.py

这个模块负责将生成结果导出成 Word 文档。
当前实现简单导出，未来可以增加 PDF、Excel 等导出方式。
"""

from pathlib import Path
from docx import Document


class WordExporter:
    """Word 导出类。"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def export(self, content: str, file_name: str) -> Path:
        """将文本内容保存为 Word 文件，并返回文件路径。"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.output_dir / f"{file_name}.docx"
        document = Document()
        document.add_paragraph(content)
        document.save(file_path)
        return file_path
