# coding:utf-8
import json
from typing import cast

from loguru import logger
from .csgo_5e import get_csgo_5einfo_img
from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.data_store import get_res_path
from gsuid_core.utils.database.api import get_uid

from .csgo_info import get_csgo_info_img
from .csgo_goods import get_csgo_goods_img
from .csgo_match import get_csgo_match_img
from ..utils.database.models import CS2Bind
from .csgo_search import get_search_players, get_search_players5e
from ..utils.api.models import UserMatchRequest
from .csgohome_info import get_csgohome_info_img
from ..utils.error_reply import UID_HINT, try_send
from .csgo_matchdetail import get_csgo_match_detail_img

csgo_user_info = SV("CS2用户信息查询")


@csgo_user_info.on_command(("查询"), block=True)
async def send_csgo_info_msg(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev, CS2Bind)
    logger.info(ev.text)
    arg = ev.text.strip()
    logger.info(arg)
    if uid is None:
        return await try_send(bot, UID_HINT)
    try:
        paltform = await CS2Bind.get_paltform(ev.user_id)
    except Exception as E:
        logger.warning(f"{E}\n获取CS2Bind数据失败，将使用默认值：pf")
        paltform = "pf"
    if paltform is None:
        logger.warning("平台是空，默认使用pf")
        paltform = "pf"
    
    s = ""
    if "S" or "s" in ev.text:
        after_s = ev.text.lower().split("s")[-1]
        if (
            after_s.isdigit()
            or after_s.startswith(("+", "-"))
            and after_s[1:].isdigit()
        ):
            s = after_s
        else:
            i = 0
            while i < len(after_s) and after_s[i].isdigit():
                i += 1
            s = after_s[:i] if i > 0 else ""
    if arg:
        paltform = arg
    logger.info("当前平台是：" + paltform)
    if paltform in ["官匹", "gp", "gf"]:
        await try_send(bot, await get_csgohome_info_img(uid))
    elif paltform in ["pf", "完美"]:
        await try_send(bot, await get_csgo_info_img(uid, s))
    elif paltform in ["5e", "5E"]:
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

    if "官匹" in ev.text:
        tag = 1
    else:
        tag = 3

    if "天梯" in ev.text:
        type_i = 12
    elif "pro" in ev.text:
        type_i = 41
    elif "巅峰" in ev.text:
        type_i = 20
    elif "周末" in ev.text:
        type_i = 27
    elif "自定义" in ev.text:
        type_i = 14
    else:
        type_i = -1
    resp = await bot.receive_resp(
        await get_csgo_match_img(ev.user_id, uid, tag, type_i)
    )
    if resp is not None:
        index = resp.text
        if not index.isdigit():
            return
        detail_path = (
            get_res_path("CS2UID") / "match" / ev.user_id / "match.json"
        )
        if not detail_path.is_file():
            await try_send(bot, "没有对局缓存，请使用指令 cs对局记录 生成数据")
        with detail_path.open("r", encoding="utf-8") as f:
            match_detail = cast(UserMatchRequest, json.load(f))
        match_id = match_detail["data"]["matchList"][int(index) - 1]["matchId"]
        match_detail_out = await get_csgo_match_detail_img(match_id)
        await try_send(bot, match_detail_out)


@csgo_user_info.on_command(("对局详情"), block=True)
async def send_csgo_match_detail_msg(bot: Bot, ev: Event):
    index = ev.text
    if not index.isdigit() or not index:
        resp = await bot.receive_resp("请输入对局序号查询详情")
        if resp is None or not resp.text.isdigit():
            await try_send(bot, "序号错误")
            return
        index = resp.text
    index = cast(int, int(index) - 1)
    detail_path = get_res_path("CS2UID") / "match" / ev.user_id / "match.json"
    print(detail_path)
    if not detail_path.is_file():
        await try_send(bot, "没有对局缓存，请使用指令 cs对局记录 生成数据")
    with detail_path.open("r", encoding="utf-8") as f:
        f.seek(0)
        match_detail = cast(UserMatchRequest, json.load(f))
    print(match_detail["data"]["matchList"])
    print(int(index))
    match_id = match_detail["data"]["matchList"][int(index)]["matchId"]
    print(match_id)
    match_detail_out = await get_csgo_match_detail_img(match_id)
    await try_send(bot, match_detail_out)


@csgo_user_info.on_command(("搜索"), block=True)
async def send_csgo_search(bot: Bot, ev: Event):
    name = ev.text.strip()
    if "5e" in ev.text:
        await try_send(bot, await get_search_players5e(name))
    
    await try_send(bot, await get_search_players(name))