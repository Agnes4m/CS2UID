import json
import re
from datetime import datetime, timedelta, timezone
from typing import cast

from gsuid_core.bot import Bot
from gsuid_core.data_store import get_res_path
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from gsuid_core.utils.database.api import get_uid

from ..utils.api.models import UserMatchRequest
from ..utils.cache import load_json_cached
from ..utils.csgo_api import pf_api
from ..utils.database.models import CS2Bind
from ..utils.error_reply import UID_HINT, get_error, try_send
from ..utils.platform import resolve_uid_and_platform
from ..utils.remind import add_reminder, remove_reminder
from .csgo_5e import get_csgo_5einfo_img
from .csgo_event import (
    get_csgo_event_img,
    get_csgo_eventlist_img,
    get_csgo_match_analysis_img,
)
from .csgo_goods import get_csgo_goods_img
from .csgo_info import get_csgo_info_img
from .csgo_match import get_csgo_match_img
from .csgo_matchdetail import get_csgo_match_detail_img
from .csgo_search import get_search_players, get_search_players5e
from .csgohome_info import get_csgohome_info_img

csgo_user_info = SV("CS2用户信息查询")


@csgo_user_info.on_command(("查询"), block=True)
async def send_csgo_info_msg(bot: Bot, ev: Event):
    logger.info(ev)
    uid, platform, s = await resolve_uid_and_platform(
        bot,
        ev,
        ev.user_id,
        ev.text.strip(),
    )

    if uid is None or platform is None:
        return await try_send(bot, UID_HINT)

    logger.info(f"[CS2]当前平台是：{platform}")

    if platform == "gf":
        await try_send(bot, await get_csgohome_info_img(uid))
    elif platform == "pf":
        await try_send(bot, await get_csgo_info_img(uid, s))
    else:
        logger.info(f"[CS2][5E]正在查询uid: {uid}")
        await try_send(bot, await get_csgo_5einfo_img(uid, s))


@csgo_user_info.on_command(("库存", "仓库", "饰品"), block=True)
async def send_csgo_goods_msg(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev, CS2Bind)
    if uid is None:
        return await try_send(bot, UID_HINT)

    await try_send(bot, await get_csgo_goods_img(uid))


@csgo_user_info.on_command(("好友码"), block=True)
async def send_csgo_friend_msg(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev, CS2Bind)
    if uid is None:
        return await try_send(bot, UID_HINT)

    await try_send(bot, await get_csgohome_info_img(uid, True))


@csgo_user_info.on_command(("对局记录", "对局信息", "对局查询"), block=True)
async def send_csgo_match_msg(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev, CS2Bind)
    if uid is None:
        return await try_send(bot, UID_HINT)
    tag = 1 if "官匹" in ev.text else 3
    type_i = determine_match_type(ev.text)

    resp = await bot.receive_resp(
        await get_csgo_match_img(ev.user_id, uid, tag, type_i)
    )
    if resp is None:
        return

    index = resp.text
    if not index.isdigit():
        return

    detail_path = get_res_path("CS2UID") / "match" / ev.user_id / "match.json"
    cached = load_json_cached(
        detail_path, platform="pf", uid=ev.user_id, method="match_list"
    )
    if cached is None:
        return await try_send(
            bot, "没有对局缓存，请使用指令 cs对局记录 生成数据"
        )
    match_detail = cast(UserMatchRequest, cached)

    try:
        match_list = match_detail["data"]["matchList"]
        if match_list is None or len(match_list) < int(index):
            return await try_send(bot, "比赛记录不完整或不存在。")

        match_id = match_list[int(index) - 1]["matchId"]
        match_detail_out = await get_csgo_match_detail_img(match_id)
        await try_send(bot, match_detail_out)
    except (KeyError, IndexError) as e:
        logger.error(f"无法获取比赛 ID: {e}")
        await try_send(bot, "获取比赛详情时出错。")


def determine_match_type(text: str) -> int:
    from ..utils.csgo_config import get_match_types

    match_types = get_match_types()
    matched_key = next((key for key in match_types if key in text), None)
    return match_types.get(matched_key, -1) if matched_key is not None else -1


@csgo_user_info.on_command(("对局详情"), block=True)
async def send_csgo_match_detail_msg(bot: Bot, ev: Event):
    index = ev.text
    if not index.isdigit() or not index:
        resp = await bot.receive_resp("请输入对局序号查询详情")
        if resp is None or not resp.text.isdigit():
            await try_send(bot, "序号错误")
            return
        index = resp.text
    idx = int(index) - 1
    detail_path = get_res_path("CS2UID") / "match" / ev.user_id / "match.json"
    cached = load_json_cached(
        detail_path, platform="pf", uid=ev.user_id, method="match_list"
    )
    if cached is None:
        return await try_send(
            bot, "没有对局缓存，请使用指令 cs对局记录 生成数据"
        )
    match_detail = cast(UserMatchRequest, cached)

    match_list = match_detail["data"]["matchList"]
    if match_list is None or idx >= len(match_list):
        return await try_send(bot, "比赛记录不完整或不存在。")

    match_id = match_list[idx]["matchId"]
    match_detail_out = await get_csgo_match_detail_img(match_id)
    await try_send(bot, match_detail_out)


@csgo_user_info.on_command(("搜索"), block=True)
async def send_csgo_search(bot: Bot, ev: Event):
    name = ev.text.strip()

    if "5e" in name.lower():
        name = name.replace("5e", "").strip()
        logger.info(f"[cs][5e] 正在搜索 {name}")
        response = await get_search_players5e(name)
    else:
        logger.info(f"[cs][完美] 正在搜索 {name}")
        response = await get_search_players(name)

    await try_send(bot, response)


tz_cn = timezone(timedelta(hours=8))
sv_event_match = SV("CS2赛事")

_DAY_KEYS = {
    "今天": 0,
    "今日": 0,
    "昨天": -1,
    "昨日": -1,
    "前天": -2,
    "前日": -2,
    "明天": 1,
    "明日": 1,
    "后天": 2,
    "后日": 2,
}
_RE_DATE = re.compile(r"(\d{1,2})[月/-](\d{1,2})(?:日)?$")

_TEAM_ALIAS_PATH = get_res_path("CS2UID") / "team_alias.json"

_DEFAULT_TEAM_ALIAS: dict[str, list[str]] = {
    "faze": ["飞猪", "银河战舰"],
    "falcons": ["猎鹰"],
    "spirit": ["绿龙", "雪碧"],
    "vitality": ["小蜜蜂"],
    "g2": ["法国队"],
    "mouz": ["老鼠", "mousesports"],
    "furia": ["黑豹", "狂怒"],
    "navi": ["天生赢家", "natus vincere"],
    "astralis": ["a队", "丹麦王朝"],
    "liquid": ["液体"],
    "cloud9": ["c9", "云九"],
    "heroic": ["英勇"],
    "ence": ["冰刀"],
    "mibr": ["巴西队"],
    "tyloo": ["天禄"],
    "the mongolz": ["蒙古队"],
    "lynn vision": ["天马", "马总"],
    "3dmax": ["三维"],
    "imperial": ["帝国"],
    "pain": ["痛苦"],
    "big": ["big俱乐部"],
    "9z": ["9z队"],
    "sinners": ["罪人"],
    "b8": ["b8队"],
    "nemesis": ["复仇"],
    "alliance": [" Alliance"],
    "monte": ["蒙特"],
    "sinisters": ["邪恶"],
}


def _load_team_aliases() -> dict[str, list[str]]:
    if not _TEAM_ALIAS_PATH.exists():
        _TEAM_ALIAS_PATH.write_text(
            json.dumps(_DEFAULT_TEAM_ALIAS, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return dict(_DEFAULT_TEAM_ALIAS)
    try:
        data = json.loads(_TEAM_ALIAS_PATH.read_text(encoding="utf-8"))
        return {k: [str(i) for i in v] for k, v in data.items()}
    except (json.JSONDecodeError, KeyError, TypeError):
        return dict(_DEFAULT_TEAM_ALIAS)


_TEAM_ALIAS = _load_team_aliases()


def _match_team(query: str, team_name: str) -> bool:
    q = query.lower().strip()
    tn = team_name.lower().strip()
    if q in tn:
        return True
    for eng_name, cn_list in _TEAM_ALIAS.items():
        if (
            tn in eng_name or eng_name in tn or q in eng_name or eng_name in q
        ) and (
            any(q in cn.lower() for cn in cn_list)
            or any(cn.lower() in q for cn in cn_list)
        ):
            return True
    return False


def _clean_text(text: str) -> str:
    text = re.sub(r"@\S+\s*", "", text)
    return text.strip()


@sv_event_match.on_command(("赛程",), block=True)
async def send_event_schedule_msg(bot: Bot, ev: Event):
    text = _clean_text(ev.text)
    if text.isdigit():
        match_id = int(text)
        detail = await pf_api.get_event_match_detail(match_id)
        if isinstance(detail, int):
            return await try_send(bot, get_error(detail))
        analysis = await pf_api.get_player_analysis(match_id)
        if isinstance(analysis, int):
            return await try_send(bot, get_error(analysis))
        share = await pf_api.get_match_share(match_id)
        if isinstance(share, int):
            share = None
        img = await get_csgo_match_analysis_img(detail, analysis, share)
        return await try_send(bot, img)

    team_part = text
    date_str = None
    for key, offset in _DAY_KEYS.items():
        if key in text:
            team_part = text.replace(key, "").strip()
            dt = datetime.now(tz_cn) + timedelta(days=offset)
            date_str = dt.strftime("%Y-%m-%d 00:00:00")
            break
    if date_str is None:
        m = _RE_DATE.search(text)
        if m:
            month, day = int(m.group(1)), int(m.group(2))
            year = datetime.now(tz_cn).year
            try:
                dt = datetime(year, month, day, tzinfo=tz_cn)
                team_part = _RE_DATE.sub("", text).strip()
                date_str = dt.strftime("%Y-%m-%d 00:00:00")
            except ValueError:
                pass

    if date_str and not team_part:
        resp = await pf_api.get_event_match_list(date_str)
        if isinstance(resp, int):
            return await try_send(bot, get_error(resp))
        dto_list = (
            resp.get("result", {}).get("matchResponse", {}).get("dtoList", [])
        )
        if not dto_list:
            return await try_send(bot, f"{date_str[:10]} 暂无赛事对局")
        img = await get_csgo_event_img(dto_list, date_str[:10])
        return await try_send(bot, img)

    team_lower = team_part.lower()
    now = datetime.now(tz_cn)
    day_list: list[str] = []
    if date_str:
        day_list.append(date_str)
    else:
        for i in range(5):
            day_list.append(
                (now - timedelta(days=i)).strftime("%Y-%m-%d 00:00:00")
            )

    all_matches = []
    seen_ids = set()
    for day in day_list:
        resp = await pf_api.get_event_match_list(day)
        if isinstance(resp, int):
            continue
        dto_list = (
            resp.get("result", {}).get("matchResponse", {}).get("dtoList", [])
        )
        for m in dto_list:
            mid = m.get("matchId")
            if mid in seen_ids:
                continue
            t1 = (m.get("team1DTO") or {}).get("name", "")
            t2 = (m.get("team2DTO") or {}).get("name", "")
            if _match_team(team_lower, t1) or _match_team(team_lower, t2):
                seen_ids.add(mid)
                all_matches.append(m)

    if not all_matches:
        return await try_send(bot, f"未找到 {team_part} 的相关比赛")

    date_display = (
        date_str[:10]
        if date_str
        else f"{day_list[-1][5:10]} ~ {day_list[0][5:10]}"
    )
    img = await get_csgo_event_img(
        all_matches,
        date_display,
        title=f"CS2 {team_part} 比赛 ({'近5日' if not date_str else date_str[:10]})",
    )
    await try_send(bot, img)


sv_match_remind = SV("CS2比赛提醒")


@sv_match_remind.on_command(("订阅赛程",), block=True)
async def subscribe_match(bot: Bot, ev: Event):
    text = _clean_text(ev.text)
    if not text.isdigit():
        return await try_send(bot, "请提供比赛ID，如：cs订阅赛程 12345")
    match_id = int(text)
    resp = await pf_api.get_event_match_detail(match_id)
    if isinstance(resp, int):
        return await try_send(bot, f"未找到比赛 {match_id}")
    match_data: dict = resp.get("result", {}).get("match", {})
    if not match_data.get("startTime"):
        return await try_send(bot, "该比赛无开始时间，无法设置提醒")
    t1 = (match_data.get("team1DTO") or {}).get("name", "?")
    t2 = (match_data.get("team2DTO") or {}).get("name", "?")
    start_time = match_data["startTime"]
    now_ms = int(datetime.now(tz_cn).timestamp() * 1000)
    if match_data.get("status") == 3 or start_time < now_ms:
        return await try_send(bot, f"{t1} vs {t2} 比赛已结束或已开始")
    msg = await add_reminder(
        match_id, ev.user_id, ev.bot_id, t1, t2, start_time
    )
    await try_send(bot, msg)


@sv_match_remind.on_command(("取消订阅赛程",), block=True)
async def unsubscribe_match(bot: Bot, ev: Event):
    text = _clean_text(ev.text)
    if not text.isdigit():
        return await try_send(bot, "请提供比赛ID，如：cs取消订阅赛程 12345")
    msg = await remove_reminder(int(text), ev.user_id)
    await try_send(bot, msg)


sv_event_calendar = SV("CS2赛事日历")


_S_LEVELS = frozenset({"Major", "T1"})

_EVENT_SUB_KEYS: dict[str, int] = {
    "major": 4,
    "s": 99,
    "s级": 99,
    "热门": 5,
    "hot": 5,
    "blast": 1,
    "esl": 2,
    "iem": 3,
    "pgl": 6,
    "pwe": 7,
    "sl": 8,
    "fissure": 9,
    "其他": 10,
    "全部": 0,
}


@sv_event_calendar.on_command(("赛事", "比赛"), block=True)
async def send_event_calendar_msg(bot: Bot, ev: Event):
    from ..utils.csgo_config import majs_config

    text = _clean_text(ev.text)
    text_lower = text.lower()

    if text_lower in _EVENT_SUB_KEYS or not text:
        sub_type = _EVENT_SUB_KEYS.get(text_lower, 5)
        label = text if text else "热门"
        page_size = int(majs_config.get_config("EventPageSize").data)
        resp = await pf_api.get_event_list(
            event_sub_type=0 if sub_type == 99 else sub_type,
            page_size=50 if sub_type == 99 else page_size,
        )
        if isinstance(resp, int):
            return await try_send(bot, get_error(resp))
        dto_list = (
            resp.get("result", {}).get("eventResponse", {}).get("dtoList", [])
        )
        if sub_type == 99:
            dto_list = [
                evt for evt in dto_list if evt.get("level") in _S_LEVELS
            ]
            label = "S级"
        if not dto_list:
            return await try_send(bot, f"暂无{label}赛事")
        img = await get_csgo_eventlist_img(dto_list, label)
        return await try_send(bot, img)

    now = datetime.now(tz_cn)
    all_matches = []
    seen_ids = set()
    for i in range(5):
        day = (now - timedelta(days=i)).strftime("%Y-%m-%d 00:00:00")
        resp = await pf_api.get_event_match_list(day)
        if isinstance(resp, int):
            continue
        dto_list = (
            resp.get("result", {}).get("matchResponse", {}).get("dtoList", [])
        )
        for m in dto_list:
            mid = m.get("matchId")
            if mid in seen_ids:
                continue
            t1 = (m.get("team1DTO") or {}).get("name", "").lower()
            t2 = (m.get("team2DTO") or {}).get("name", "").lower()
            if text_lower in t1 or text_lower in t2:
                seen_ids.add(mid)
                all_matches.append(m)

    if not all_matches:
        return await try_send(bot, f"近期未找到 {text} 的比赛")

    day_range = f"{(now - timedelta(days=4)).strftime('%m-%d')} ~ {now.strftime('%m-%d')}"
    img = await get_csgo_event_img(
        all_matches, day_range, title=f"CS2 {text} 比赛 (近5日)"
    )
    await try_send(bot, img)
