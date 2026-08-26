"""
main.py

程序入口模块。
支持两种模式：
1. 传统剧本生成模式
2. 短剧正文创作模式
"""

import sys
import argparse
from pathlib import Path

project_root = Path(__file__).resolve().parent
project_root_parent = project_root.parent
if str(project_root_parent) not in sys.path:
    sys.path.insert(0, str(project_root_parent))

from src.generator.script_generator import ScriptGenerator
from src.shortplay.batch import BatchGenerator
from src.logger import create_logger
from src.errors import (
    ConfigError,
    PromptError,
    ReadError,
    AIError,
    ExportError,
)


def run_traditional_mode(args):
    """运行传统剧本生成模式。"""
    config_path = project_root_parent / "config" / "config.json"
    prompt_dir = project_root_parent / "prompts"
    input_file = Path(args.input) if args.input else project_root_parent / "data" / "example.txt"
    output_dir = Path(args.output) if args.output else project_root_parent / "output"
    log_file = project_root_parent / "logs" / "app.log"

    logger = create_logger(log_file)

    try:
        generator = ScriptGenerator(
            config_path=config_path,
            prompt_dir=prompt_dir,
            input_file=input_file,
            output_dir=output_dir,
            log_file=log_file,
        )
        generator.run()
        print(f"✅ 剧本生成完成，输出目录：{output_dir}")

    except ConfigError as exc:
        logger.exception("配置错误")
        print("错误：配置读取失败。")
        print("为什么：", exc)
        print("怎么解决：请在 config/config.json 中填写正确的配置，或者设置相应的环境变量（例如 OPENAI_API_KEY）。")

    except PromptError as exc:
        logger.exception("Prompt 错误")
        print("错误：Prompt 加载失败。")
        print("为什么：", exc)
        print("怎么解决：检查 prompts/ 目录下是否存在所需的 prompt 文件，例如 script_generation.txt。")

    except ReadError as exc:
        logger.exception("读取文件错误")
        print("错误：读取输入文件失败。")
        print("为什么：", exc)
        print("怎么解决：确认输入文件存在且为 UTF-8 编码文本，路径正确。")

    except AIError as exc:
        logger.exception("AI 调用错误")
        print("错误：AI 服务调用失败。")
        print("为什么：", exc)
        print("怎么解决：检查网络连接、API Key、模型配置，或稍后重试。")

    except ExportError as exc:
        logger.exception("导出错误")
        print("错误：导出文件失败。")
        print("为什么：", exc)
        print("怎么解决：检查输出目录权限和磁盘空间。")

    except Exception as exc:
        logger.exception("未知错误")
        print("发生未知错误：", exc)
        print("请查看 logs/app.log 获取详细信息。")


def run_shortplay_mode(args):
    """运行短剧正文创作模式。"""
    outline_path = Path(args.outline)
    character_path = Path(args.character)
    output_dir = Path(args.output)

    try:
        generator = BatchGenerator(
            outline_file=outline_path,
            character_file=character_path,
            output_dir=output_dir
        )

        if args.single:
            print(f"正在生成第 {args.single} 集...")
            output_path = generator.generate_single(args.single)
            print(f"✅ 第 {args.single} 集已生成：{output_path}")
        else:
            start = args.start or 1
            end = args.end
            print(f"正在生成第 {start} - {end or '全部'} 集...")
            output_files = generator.generate_all(start, end)
            print(f"✅ 批量生成完成，共生成 {len(output_files)} 集剧本")

    except FileNotFoundError as e:
        print(f"❌ 错误：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 生成失败：{e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="AI 剧本工厂")
    subparsers = parser.add_subparsers(dest="mode", help="运行模式")

    # 传统模式
    traditional_parser = subparsers.add_parser("traditional", help="传统剧本生成模式")
    traditional_parser.add_argument("--input", "-i", help="输入文件路径")
    traditional_parser.add_argument("--output", "-o", help="输出目录")

    # 短剧模式
    shortplay_parser = subparsers.add_parser("shortplay", help="短剧正文创作模式")
    shortplay_parser.add_argument("--outline", "-ol", required=True, help="集纲文件路径")
    shortplay_parser.add_argument("--character", "-ch", required=True, help="人设文件路径")
    shortplay_parser.add_argument("--output", "-o", required=True, help="输出目录")
    shortplay_parser.add_argument("--start", type=int, default=1, help="开始集数")
    shortplay_parser.add_argument("--end", type=int, default=None, help="结束集数")
    shortplay_parser.add_argument("--single", type=int, default=None, help="只生成指定集数")

    args = parser.parse_args()

    if args.mode == "shortplay":
        run_shortplay_mode(args)
    elif args.mode == "traditional":
        run_traditional_mode(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()