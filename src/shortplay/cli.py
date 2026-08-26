"""
cli.py

短剧创作命令行工具。
提供便捷的命令行接口来生成剧本。
"""

import argparse
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.shortplay.batch import BatchGenerator


def main():
    parser = argparse.ArgumentParser(description="AI 剧本工厂 - 短剧正文创作工具")
    
    # 输入文件参数
    parser.add_argument("--outline", "-o", required=True, 
                        help="集纲文件路径")
    parser.add_argument("--character", "-c", required=True,
                        help="人设文件路径")
    parser.add_argument("--output", "-out", required=True,
                        help="输出目录")
    
    # 生成范围参数
    parser.add_argument("--start", type=int, default=1,
                        help="开始集数（默认1）")
    parser.add_argument("--end", type=int, default=None,
                        help="结束集数（默认全部）")
    
    # 单集生成
    parser.add_argument("--single", type=int, default=None,
                        help="只生成指定集数")
    
    args = parser.parse_args()
    
    # 验证输入文件
    outline_path = Path(args.outline)
    character_path = Path(args.character)
    output_dir = Path(args.output)
    
    if not outline_path.exists():
        print(f"错误：集纲文件不存在 - {outline_path}")
        sys.exit(1)
    
    if not character_path.exists():
        print(f"错误：人设文件不存在 - {character_path}")
        sys.exit(1)
    
    try:
        # 创建批量生成器
        generator = BatchGenerator(
            outline_file=outline_path,
            character_file=character_path,
            output_dir=output_dir
        )
        
        if args.single:
            # 生成单集
            print(f"正在生成第 {args.single} 集...")
            output_path = generator.generate_single(args.single)
            print(f"✅ 第 {args.single} 集已生成：{output_path}")
        else:
            # 批量生成
            print(f"正在生成第 {args.start} - {args.end or '全部'} 集...")
            output_files = generator.generate_all(args.start, args.end)
            print(f"✅ 批量生成完成，共生成 {len(output_files)} 集剧本")
            for file in output_files:
                print(f"  - {file}")
    
    except Exception as e:
        print(f"❌ 生成失败：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()