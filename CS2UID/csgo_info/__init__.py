from typing import cast

from gsuid_core.bot import Bot
from gsuid_core.data_store import get_res_path
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from gsuid_core.utils.database.api import get_uid

from ..utils.api.models import UserMatchRequest
from ..utils.cache import load_json_cached
from ..utils.database.models import CS2Bind
from ..utils.error_reply import UID_HINT, try_send
from ..utils.platform import resolve_uid_and_platform
from .csgo_5e import get_csgo_5einfo_img
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

    # 获取比赛信息
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

    # 获取比赛 ID
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
    """根据输入文本确定比赛类型,默认 -1 (全部)。"""
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
