"""
api.py

Flask Web API 服务模块。
提供 Web 界面与后端交互的接口。
参考 StoryPlay 架构：采用 /api/v1/ 前缀，统一响应格式。
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# 项目路径设置
project_root = Path(__file__).resolve().parent
project_root_parent = project_root.parent
if str(project_root_parent) not in sys.path:
    sys.path.insert(0, str(project_root_parent))

from src.config import Config
from src.ai.openai_client import OpenAIClient
from src.prompt_manager import PromptManager
from src.logger import create_logger
from src.errors import (
    ConfigError,
    PromptError,
    ReadError,
    AIError,
    ExportError,
)

app = Flask(__name__, static_folder=str(project_root_parent / "web"), static_url_path="")
CORS(app)

# 全局日志记录器
logger = create_logger(project_root_parent / "logs" / "web.log")

# API 版本
API_VERSION = "v1"


def json_response(success: bool, data=None, error=None, message=None, status_code=200):
    """统一的 JSON 响应格式"""
    response = {
        "success": success,
        "timestamp": datetime.now().isoformat(),
        "version": API_VERSION
    }
    if data is not None:
        response["data"] = data
    if error is not None:
        response["error"] = error
    if message is not None:
        response["message"] = message
    return jsonify(response), status_code


@app.route("/", methods=["GET"])
def index():
    """返回前端 HTML 页面"""
    return app.send_static_file("index.html")


@app.route(f"/api/{API_VERSION}/health", methods=["GET"])
def health_check():
    """健康检查接口"""
    return json_response(True, {
        "status": "healthy",
        "service": "AI Short Play Script Factory"
    })


@app.route(f"/api/{API_VERSION}/generation-types", methods=["GET"])
def get_generation_types():
    """获取可用的生成类型"""
    generation_types = [
        {"id": "extract_outline", "name": "提取核心梗概", "description": "提取小说IP核心梗概，包括男主动机、成长路线"},
        {"id": "analyze_script", "name": "拆剧分析", "description": "人工拆剧，记录分集reaction，AI整理集纲与节奏分析"},
        {"id": "extract_script", "name": "扒一卡剧本", "description": "详细分析一卡内容，生成带时间戳的剧本"},
        {"id": "inspiration", "name": "灵感创作", "description": "AI生成多个故事设定方案，确定框架"},
        {"id": "rewrite", "name": "仿写创作", "description": "仿照对标剧框架，创作出新的人设和大纲"},
        {"id": "generate_outline", "name": "集纲生成", "description": "根据大纲和人设生成集纲，每集结尾带钩子"},
        {"id": "generate_script", "name": "剧本正文", "description": "根据集纲生成专业剧本，台词带情绪，强视效冲突"},
        {"id": "expand", "name": "展开剧本", "description": "将简略的剧本内容展开丰富"},
        {"id": "style_change", "name": "修改风格", "description": "改变剧本的风格和语气"},
        {"id": "summary", "name": "剧本总结", "description": "对剧本进行总结和概述"},
        {"id": "custom", "name": "自定义", "description": "使用自定义提示词进行创作"},
    ]
    return json_response(True, generation_types)


@app.route(f"/api/{API_VERSION}/prompts", methods=["GET"])
def get_prompts():
    """获取所有可用的提示词文件"""
    prompts_dir = project_root_parent / "prompts"
    prompts = {}
    
    if prompts_dir.exists():
        for prompt_file in prompts_dir.glob("*.txt"):
            try:
                with open(prompt_file, "r", encoding="utf-8") as f:
                    prompts[prompt_file.stem] = f.read()
            except Exception as e:
                logger.warning(f"Failed to read prompt file {prompt_file}: {e}")
    
    return json_response(True, prompts)


@app.route(f"/api/{API_VERSION}/generate", methods=["POST"])
def generate():
    """
    生成脚本主接口。
    
    请求 JSON：
    {
        "input_text": "输入的剧本文本/集纲",
        "prompt": "自定义提示词（可选，若为空则用默认）",
        "generation_type": "生成类型",
        "model": "模型名称（可选，默认用 config 中的）",
        "character_bio": "人物小传/人设信息（可选，用于短剧创作）",
        "genre": "题材类型（可选）",
        "core_hook": "核心看点（可选）",
        "checkpoints": "卡点要求（可选，逗号分隔）"
    }
    """
    start_time = time.time()
    try:
        data = request.get_json() or {}
        
        input_text = data.get("input_text", "").strip()
        custom_prompt = data.get("prompt", "").strip()
        generation_type = data.get("generation_type", "expand")
        model_override = data.get("model", None)
        character_bio = data.get("character_bio", "").strip()
        genre = data.get("genre", "")
        core_hook = data.get("core_hook", "")
        checkpoints = data.get("checkpoints", "")
        options = data.get("options", {})
        if not isinstance(options, dict):
            return json_response(False, error="options 必须是对象", message="参数验证失败", status_code=400)
        
        # 验证必填参数
        if not input_text and not custom_prompt:
            return json_response(False, error="请提供输入内容或自定义提示词", message="参数验证失败", status_code=400)
        
        # 加载配置
        config_path = project_root_parent / "config" / "config.json"
        config = Config(config_path)
        
        # 确定使用的 API Key 和 Model
        api_key = config.get("deepseek_api_key") or config.get("openai_api_key")
        if not api_key:
            raise ConfigError("未配置 DeepSeek 或 OpenAI API Key")
        
        configured_model = config.get("openai_model")
        # 当前版本只允许使用服务端配置的模型，避免外部请求任意消耗账户额度。
        if model_override and model_override not in ("default", configured_model):
            return json_response(False, error="不允许使用未配置的模型", message="参数验证失败", status_code=400)
        model = configured_model
        
        # 加载 Prompt
        prompt_dir = project_root_parent / "prompts"
        prompt_manager = PromptManager(prompt_dir)
        
        # 使用自定义 prompt 或根据生成类型构建提示词
        if custom_prompt and generation_type == "custom":
            prompt_text = custom_prompt
        else:
            # 根据不同生成类型构建专用提示词
            prompt_text = build_prompt_by_type(
                generation_type, 
                input_text, 
                character_bio, 
                genre, 
                core_hook, 
                checkpoints,
                prompt_manager,
                custom_prompt,
                options,
            )
        
        # 调用 AI
        ai_client = OpenAIClient(api_key, model, config.get("ai_base_url"))
        logger.info(f"调用 AI 生成（类型={generation_type}，模型={model}）")
        result = ai_client.generate(prompt_text)
        
        # 计算耗时
        elapsed_time = round(time.time() - start_time, 2)
        
        return json_response(True, {
            "output": result,
            "generation_type": generation_type,
            "model": model,
            "elapsed_time": elapsed_time,
            "character_count": len(result)
        }, message=f"生成成功（{generation_type}）")
    
    except ConfigError as e:
        logger.exception("配置错误")
        return json_response(False, error=f"配置读取失败: {str(e)}", message="配置错误", status_code=500)
    
    except AIError as e:
        logger.exception("AI 调用错误")
        return json_response(False, error=f"AI 服务调用失败: {str(e)}", message="AI 服务错误", status_code=503)
    
    except Exception as e:
        logger.exception("未知错误")
        return json_response(False, error=f"发生错误: {str(e)}", message="服务器错误", status_code=500)


def build_prompt_by_type(generation_type, input_text, character_bio, genre, core_hook, checkpoints,
                         prompt_manager, custom_prompt="", options=None):
    """
    根据生成类型构建专用提示词
    """
    genre_text = genre if genre else "玄幻"
    hook_text = core_hook if core_hook else "复仇逆袭"
    checkpoint_text = checkpoints if checkpoints else "危机线、悬念线、大场面"
    
    options = options or {}
    prompts = {
        "extract_outline": f"""【指令：梳理IP梗概内容】
你是专业的小说IP拆解专家，请根据以下内容提取有效的核心梗概。

【原始文本】：
{input_text}

【题材类型】：{genre_text}
【核心看点】：{hook_text}

请按照以下格式输出：
【核心梗概】：
【男主核心动机】：
【男主成长路线】：
【男主升级路线】：
1. 觉醒期：
2. 成长期：
3. 爆发期：
4. 巅峰期：
【升级手段展现】：
【剧情节奏】：密集反转+强悬念+大场面

【要求】：
1. 节奏紧密，反转、悬念点、大场面足够多
2. 符合当前市面短剧内容要求
3. 男主升级路线极其明确，升级后的手段有足够视效内容
4. 每十集设置一个强卡点（危机线、悬念线、大场面、强期待、强噱头、大人物救场、暧昧）
5. 具备有效的起承转合、矛盾冲突、情绪转折""",
        
        "analyze_script": f"""【指令：阶段剧情分析】
根据以下分集Reaction整理集纲并进行深度分析，同时检测并解决以下问题：

【对标剧名称】：{options.get("reference_title") or "未指定"}
【集数】：{options.get("reference_episodes") or 80}集
【分集Reaction】：
{input_text}

【分析维度】：{options.get("analysis_focus") or "人物弧线、情节结构、节奏分析、爽点分布、钩子设计、反转设计"}

【检测与优化要求】：
1. 检测阶段剧情是否过于重复，确保男主反杀手段、卡点情绪多样化
2. 检测剧情是否偏离主线，确保核心世界观和修炼体系不变
3. 检测剧情是否假大空，要求具象化故事情节，强冲突、强情绪
4. 检测剧情走向是否单一重复，要求不同阶段有不同的反击手段
5. 确保前后文逻辑一致、人设统一
6. 确保系统奖励有效使用并由配角烘托其强大
7. 确保单集字数达到要求

【输出要求】：
1. 整理每集集纲（第1集：... 钩子：...）
2. 分析人物弧线、情节结构、节奏分布
3. 标注每10集一个强卡点位置（危机线、悬念线、大场面、强期待、强噱头、大人物救场、暧昧）
4. 给出优化建议和修改方案

格式清晰，内容详实，符合短剧创作要求。""",
        
        "extract_script": f"""【指令：扒一卡剧本】
根据视频分析生成剧本，带时间戳，严格忠实内容。

视频分析：{input_text}

输出格式（从第{options.get("start_episode") or 1}集开始，共{options.get("episode_count") or 1}集）：
第{options.get("start_episode") or 1}集
【时间戳】内容描述
...""",
        
        "professional_breakdown": f"""【指令：专业拆剧分析】
请根据以下短剧剧本内容，按照专业模版进行深度拆剧分析。

【剧本内容】：
{input_text}

【核心分析框架】：

请按照以下专业结构进行拆剧：

1. 分章节详细拆解（每3-12集为一个章节）
   - 章节剧情内容
   - 每集卡点设计（明确标注：期待/爽感/悬念）
   - 危机设计（内部危机/外部危机）
   - 人物关系进展
   - 金手指能力展示与升级

2. 核心结构分析
   - 观众视角设计（上帝视角/信息差利用）
   - 男主能力升级分析（内部诱因/外部诱因）
   - 爽点链路设计（男主方爽点/女主方爽点）
   - 节奏分布（快节奏/缓节奏交替）

3. 关键技术手法分析
   - 信息差的运用
   - 卡点设计逻辑
   - 打脸爽感设计
   - 情感升温路线
   - 身份升级路径

【输出格式要求】：

【章节分解】
X-X集：[章节主题]
   1、[单集内容]
      卡点：[卡点类型] - [具体描述]
      爽点：[爽点类型] - [爽点设计]
   ...

【总结分析】
观众视角：
男主能力升级：
   内部诱因：
   外部诱因：
爽点来源：
   男主方爽点链路：
   女主方爽点链路：
   人物情感发展：
关键技术手法：
   信息差运用：
   卡点设计：
   打脸设计：

格式清晰，分析深入，符合专业短剧剧本拆剧要求！""",
        
        "generate_outline": f"""【指令：生成标准集纲】
根据以下信息生成{options.get("total_episodes") or 80}集竖屏短剧集纲，本次仅输出第{options.get("outline_start") or 1}集至第{options.get("outline_end") or options.get("total_episodes") or 80}集。

【题材】：{genre_text}
【人物小传】：{character_bio}
【核心梗概】：{input_text}
【卡点要求】：{checkpoint_text}

【集纲情节优化要求】：
1. 自检前后文逻辑不一致的地方，确保行文逻辑一致性
2. 自检全文人设是否统一
3. 确保系统奖励有效使用，并有配角烘托其强大
4. 如遇前后文逻辑不一致可适当修改，但需保持故事一致性
5. 确保单集字数达到五百字以上

【集纲模板要求】：
1. 单集剧情充实，具备强视效冲突
2. 人物有明确的人设定位
3. 前后剧情关联性强，具备草蛇灰线
4. 包含矛盾冲突、搞笑点、伏笔、悬念、危机点
5. 单集内具备完整起承转合

【输出格式】：
第1集：
1. 场景描述+情节
2. 场景描述+情节
...
【危机卡点】

【要求】：
1. 每集结尾带钩子，具备留下用户的钩子
2. 每10集设置一个强卡点（危机线、悬念线、大场面、强期待、强噱头、大人物救场、暧昧）
3. 男主升级路线明确，升级手段有足够视效内容
4. 具备强情绪、强冲锋、强起伏
5. 符合短剧节奏要求，密集反转+强悬念+大场面""",
        
        "generate_script": f"""【指令：剧本正文创作】
你是顶级短剧编剧，请根据以下信息生成第{options.get("script_start") or 1}集至第{options.get("script_end") or 1}集的专业剧本（每集约1200-1400字，画面描述约占40%）。

【题材】：{genre_text}
【目标市场与风格】：{options.get("market_style") or "国内风格"}
【额外风格要求】：{options.get("style_options") or "台词带情绪、强羞辱感、人物反应"}
【人物小传】：{character_bio}
【集纲】：{input_text}

【剧本格式要求】：
第1集 1-1 场景名 日/夜 内景/外景
人物：XXX
▲画面描述（详细说明人物动作、画面氛围、空镜、转场）
角色名（情绪）：台词
▲画面描述
...

【情节扩充要求】：
1. 台词带情绪（拉仇恨、增加人物羁绊、拉前文剧情塑造人物）
2. 人物对台词给予足够的反应和回馈
3. 台词具备强有力的羞辱、情绪递进且具备推进剧情的效果
4. 开场进入矛盾，结尾留钩子
5. 零废笔、干净利落
6. 具备强视效冲突
7. 画面描述丰富连贯，角色调度清晰
8. 不用画面展示人物心理，使用OS或直白台词表达
9. 角色名字与台词独立一行

请严格按照格式和要求输出剧本。""",
        
        "inspiration": f"""【指令：灵感创作】
帮我构思80集竖屏短剧集纲，每集1-1.5分钟。

【题材】：{genre_text}
【故事主线】：{input_text}
【核心爽点】：{hook_text}

【输出格式】：
剧名：《XXX》
题材：
人物小传：
*女主：
*男主：
*配角：
*反派：
大纲：（2000字左右）

【要求】：
1. 具备强情绪、强冲锋、强起伏
2. 男主升级路线明确，升级手段有足够视效内容
3. 每十集设置一个强卡点
4. 符合当前市面短剧内容要求""",
        
        "rewrite": f"""【指令：仿写创作】
根据对标短剧仿写全新内容（约2000字）。

【对标内容】：{input_text}
【调整思路】：{character_bio}

【输出格式】：
剧名：《XXX》
题材：
人物小传：
*女主：
*男主：
*配角：
*反派：
大纲：

【要求】：
1. 保持核心框架但内容全新
2. 具备强情绪、强冲突
3. 符合短剧节奏要求""",
        
        "shortplay": f"""【指令：短剧正文创作】
你是顶级短剧编剧，请根据以下信息生成专业短剧剧本。

【题材】：{genre_text}
【人物小传】：{character_bio}
【集纲】：{input_text}

【剧本格式要求】：
第1集 1-1 场景名 日/夜 内景/外景
人物：XXX
▲画面描述
角色名（情绪）：台词
▲画面描述
...

【要求】：
1. 每集1-1.5分钟，约1200字
2. 台词带情绪，具备强有力的羞辱、情绪递进
3. 人物对台词给予足够的反应和回馈
4. 开场进入矛盾，结尾留钩子
5. 具备强视效冲突""",
        
        "expand": f"""【指令：展开剧本】
将以下简略的剧本内容展开丰富。

【原始内容】：
{input_text}

请展开成详细的剧本内容。""",
        
        "style_change": f"""【指令：修改风格】
改变以下剧本的风格和语气。

【原始内容】：
{input_text}

请修改成新的风格。""",
        
        "summary": f"""【指令：剧本总结】
对以下剧本进行总结和概述。

【原始内容】：
{input_text}

请提供总结。""",
        
        "custom": custom_prompt if custom_prompt else f"请处理以下内容：\n{input_text}",
    }
    
    return prompts.get(generation_type, f"请{generation_type}以下剧本：\n{input_text}")


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))
    logger.info(f"启动 Flask API 服务... (端口 {port})")
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=port)
