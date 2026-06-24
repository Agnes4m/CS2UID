"""API 响应日志工具 — 自动脱敏 token/cookie 等敏感字段。"""

import json as _json
from typing import Any

_SENSITIVE_KEYS = (
    "token",
    "access_token",
    "accesstoken",
    "accessToken",
    "cookie",
    "stoken",
    "Authorization",
    "password",
)


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            if any(s in k for s in _SENSITIVE_KEYS):
                out[k] = "***REDACTED***" if v else v
            else:
                out[k] = _redact(v)
        return out
    if isinstance(value, list):
        return [_redact(v) for v in value]
    return value


def safe_log_response(resp_text: str, max_len: int = 500) -> str:
    """把响应体解析为 JSON 后脱敏,失败则截断原文本。"""
    try:
        data = _json.loads(resp_text)
        text = _json.dumps(_redact(data), ensure_ascii=False, default=str)
    except (ValueError, TypeError):
        text = resp_text

    if len(text) > max_len:
        text = text[:max_len] + "...(truncated)"
    return text
