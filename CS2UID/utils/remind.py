"""比赛开始提醒 — 定时任务管理。"""

import contextlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from gsuid_core.aps import scheduler
from gsuid_core.data_store import get_res_path
from gsuid_core.gss import gss
from gsuid_core.logger import logger

from ..utils.api.request import PerfectWorldApi

_API = PerfectWorldApi()

_REMIND_FILE = get_res_path(["CS2UID"]) / "reminders.json"
_TZ_CN = timezone(timedelta(hours=8))

_JOB_PREFIX = "cs_remind_"


def _reminders_path() -> Path:
    p = _REMIND_FILE.resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _load() -> list[dict[str, Any]]:
    p = _reminders_path()
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save(reminders: list[dict[str, Any]]) -> None:
    p = _reminders_path()
    p.write_text(
        json.dumps(reminders, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _job_id(match_id: int, user_id: str) -> str:
    return f"{_JOB_PREFIX}{match_id}_{user_id}"


async def add_reminder(
    match_id: int,
    user_id: str,
    bot_id: str,
    team1: str,
    team2: str,
    match_time: int,
) -> str:
    """添加比赛开始提醒 (match_time 为毫秒时间戳)。"""
    notify_dt = datetime.fromtimestamp(
        match_time / 1000, tz=_TZ_CN
    ) - timedelta(minutes=10)

    if notify_dt <= datetime.now(_TZ_CN):
        return "比赛已开始或即将开始，无法设置提醒"

    reminders = _load()
    jid = _job_id(match_id, user_id)
    for r in reminders:
        if r["match_id"] == match_id and r["user_id"] == user_id:
            return "已设置过该比赛的提醒"

    entry = {
        "match_id": match_id,
        "user_id": user_id,
        "bot_id": bot_id,
        "team1": team1,
        "team2": team2,
        "match_time": match_time,
    }
    reminders.append(entry)
    _save(reminders)

    scheduler.add_job(
        func=_send_reminder,
        trigger="date",
        run_date=notify_dt,
        id=jid,
        name=f"比赛{match_id}提醒-{user_id}",
        replace_existing=True,
        args=[match_id, user_id, bot_id, team1, team2],
    )

    match_dt = datetime.fromtimestamp(match_time / 1000, tz=_TZ_CN)
    logger.info(f"[CS2][提醒] 已添加提醒: {team1} vs {team2} ({user_id})")
    return f"已设置提醒，将在 {match_dt.strftime('%m-%d %H:%M')} 比赛开始前10分钟通知您"


async def remove_reminder(match_id: int, user_id: str) -> str:
    """取消比赛开始提醒。"""
    reminders = _load()
    before = len(reminders)
    reminders = [
        r
        for r in reminders
        if not (r["match_id"] == match_id and r["user_id"] == user_id)
    ]
    if len(reminders) == before:
        return "未找到该比赛的提醒"
    _save(reminders)

    with contextlib.suppress(Exception):
        scheduler.remove_job(_job_id(match_id, user_id))
    return "已取消该比赛的提醒"


async def _send_reminder(
    match_id: int,
    user_id: str,
    bot_id: str,
    team1: str,
    team2: str,
) -> None:
    """APScheduler job 回调：发送比赛即将开始通知。"""
    try:
        bot = gss.active_bot.get(bot_id)
        if bot is None:
            logger.warning(f"[CS2][提醒] bot {bot_id} 不可用，跳过推送")
            return

        msg = f"⏰ 比赛即将开始！\n{team1} vs {team2}\n比赛ID: {match_id}"
        await bot.target_send(msg, "direct", user_id, bot_id, "")
        logger.info(
            f"[CS2][提醒] 已推送比赛开始提醒: {team1} vs {team2} -> {user_id}"
        )
    except Exception as e:
        logger.error(f"[CS2][提醒] 推送失败: {e}")
    finally:
        reminders = _load()
        reminders = [
            r
            for r in reminders
            if not (r["match_id"] == match_id and r["user_id"] == user_id)
        ]
        _save(reminders)


def reschedule_pending() -> None:
    """在插件加载时重新注册所有未触发的提醒。"""
    now = datetime.now(_TZ_CN)
    reminders = _load()
    valid = []
    for r in reminders:
        notify_dt = datetime.fromtimestamp(
            r["match_time"] / 1000, tz=_TZ_CN
        ) - timedelta(minutes=10)
        if notify_dt <= now:
            continue
        valid.append(r)
        jid = _job_id(r["match_id"], r["user_id"])
        scheduler.add_job(
            func=_send_reminder,
            trigger="date",
            run_date=notify_dt,
            id=jid,
            name=f"比赛{r['match_id']}提醒-{r['user_id']}",
            replace_existing=True,
            args=[
                r["match_id"],
                r["user_id"],
                r["bot_id"],
                r["team1"],
                r["team2"],
            ],
        )
    if valid:
        logger.info(f"[CS2][提醒] 已重新注册 {len(valid)} 个待推送的比赛提醒")
    _save(valid)


reschedule_pending()
