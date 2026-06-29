from typing import Literal

from .database.models import CS2Bind
from .error_reply import UID_HINT

Platform = Literal["pf", "5e", "gf"]

_PLATFORM_KEYWORDS: list[tuple[Platform, tuple[str, ...]]] = [
    ("5e", ("5e", "5E")),
    ("gf", ("官匹", "gp", "gf", "国服")),
    ("pf", ("pf", "完美", "wanmei")),
]


def detect_platform(text: str) -> Platform | None:
    """从用户输入文本中解析目标平台。

    返回 ``"pf"`` (完美) / ``"5e"`` (5E) / ``"gf"`` (官匹国服) 之一,
    无法识别返回 ``None``。
    """
    upper = text.upper()
    for platform, keywords in _PLATFORM_KEYWORDS:
        for kw in keywords:
            if kw.upper() in upper:
                return platform
    return None


async def resolve_uid_and_platform(
    bot,
    ev,
    user_id: str,
    text: str,
) -> tuple[str | None, Platform | None, str | None]:
    """根据文本解析 (uid, platform, season)。

    解析失败时返回 ``(None, None, error_msg)``; ``error_msg`` 为面向用户的提示。
    """
    from gsuid_core.utils.database.api import get_uid

    platform = detect_platform(text)
    season = _parse_s_value(text)
    parts = text.split()

    if platform == "5e":
        uid = parts[1].strip() if len(parts) > 1 else None
        if not uid:
            domain = await CS2Bind.get_domain(user_id)
            if domain:
                uid = domain.replace("5e", "").replace("5E", "").strip()
        if not uid:
            uid = await CS2Bind.get_uid_by_game(user_id, ev.bot_id)
        if not uid:
            return None, None, UID_HINT
        return uid, "5e", season

    if platform == "gf":
        uid = parts[1].strip() if len(parts) > 1 else None
        if not uid:
            domain = await CS2Bind.get_domain(user_id)
            if domain:
                uid = domain
        if not uid:
            uid = await CS2Bind.get_uid_by_game(user_id, ev.bot_id)
        if not uid:
            return None, None, UID_HINT
        return uid, "gf", season

    uid = await get_uid(bot, ev, CS2Bind)
    if not uid:
        return None, None, UID_HINT

    bound_platform = await CS2Bind.get_platform(user_id)
    return uid, bound_platform or "pf", season


def _parse_s_value(text: str) -> str:
    """提取 ``s<数字>`` 形式的赛季参数。"""
    lowered = text.lower()
    if "s" not in lowered:
        return ""
    after_s = lowered.split("s")[-1]
    if after_s.isdigit() or (
        after_s.startswith(("+", "-")) and after_s[1:].isdigit()
    ):
        return after_s
    i = 0
    while i < len(after_s) and after_s[i].isdigit():
        i += 1
    return after_s[:i] if i > 0 else ""
