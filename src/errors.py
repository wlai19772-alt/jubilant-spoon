"""
errors.py

这个模块负责定义项目中的错误类型。
客户端代码通过捕获这些异常来给用户友好提示。
"""

class ScriptFactoryError(Exception):
    """基础错误类型。"""
    pass


class ConfigError(ScriptFactoryError):
    """配置加载错误。"""
    pass


class PromptError(ScriptFactoryError):
    """Prompt 加载错误。"""
    pass


class ReadError(ScriptFactoryError):
    """读取文件错误。"""
    pass


class AIError(ScriptFactoryError):
    """AI 调用错误。"""
    pass


class ExportError(ScriptFactoryError):
    """导出文件错误。"""
    pass
