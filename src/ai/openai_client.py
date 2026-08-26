"""
openai_client.py

这个模块负责与 DeepSeek / OpenAI API 交互。
默认配置切换为 DeepSeek，兼容 OpenAI 风格接口。
"""

from openai import OpenAI

from src.errors import AIError


class OpenAIClient:
    """兼容 DeepSeek 的客户端。"""

    def __init__(self, api_key: str, model: str, base_url: str = "https://api.deepseek.com"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, prompt: str) -> str:
        """调用 DeepSeek / OpenAI 风格的 Chat Completions API。"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            # SDK 异常类型在不同版本中不完全一致；统一转换为业务异常，
            # 同时避免让原始服务端错误泄露给调用方。
            raise AIError(
                "调用 AI 服务失败。请检查 API Key、模型、服务地址、网络与账户状态，详细错误请查看日志。"
            ) from exc
