"""Snowpark Session経由でSnowflake Cortex LLMを呼び出すカスタムLM。"""

import json
import time
from typing import Any

import dspy


class SnowflakeCortexLM(dspy.BaseLM):
    """Snowpark SQLのSNOWFLAKE.CORTEX.COMPLETEを使うDSPy LM。"""

    def __init__(self, session, model: str = "mistral-large2", **kwargs):
        super().__init__(model=model, **kwargs)
        self.session = session

    def forward(self, prompt=None, messages=None, **kwargs):
        """メッセージをSnowflake Cortex COMPLETEに送信し、OpenAI互換レスポンスを返す。"""
        if messages:
            text = "\n".join(
                f"{m['role']}: {m['content']}" for m in messages
            )
        elif prompt:
            text = prompt
        else:
            text = ""

        # シングルクォートのエスケープ
        escaped = text.replace("\\", "\\\\").replace("'", "\\'")

        sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{self.model}', '{escaped}') AS response"
        result = self.session.sql(sql).collect()
        content = result[0]["RESPONSE"] if result else ""

        # OpenAI互換のレスポンスオブジェクトを構築
        response = _build_response(content, self.model)
        return response


class _Message:
    def __init__(self, content):
        self.content = content
        self.tool_calls = None


class _Choice:
    def __init__(self, content):
        self.message = _Message(content)


class _Usage:
    def __init__(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0

    def __iter__(self):
        yield "prompt_tokens", self.prompt_tokens
        yield "completion_tokens", self.completion_tokens
        yield "total_tokens", self.total_tokens


class _Response:
    def __init__(self, content, model):
        self.choices = [_Choice(content)]
        self.usage = _Usage()
        self.model = model
        self._hidden_params = {}


def _build_response(content: str, model: str) -> _Response:
    return _Response(content, model)
