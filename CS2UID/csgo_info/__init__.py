from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.utils.database.api import get_uid

from .csgo_info import get_csgo_info_img
from .csgo_goods import get_csgo_goods_img
from .csgo_match import get_csgo_match_img
from ..utils.database.models import CS2Bind
from .csgo_search import get_search_players
from .csgohome_info import get_csgohome_info_img
from ..utils.error_reply import UID_HINT, try_send

csgo_user_info = SV('CS2用户信息查询')


@csgo_user_info.on_command(('查询'), block=True)
async def send_csgo_info_msg(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev, CS2Bind)
    if uid is None:
        return await try_send(bot, UID_HINT)
    s = ""
    if 'S' or 's' in ev.text:
        after_s = ev.text.lower().split("s")[-1]
        if (
            after_s.isdigit()
            or after_s.startswith(('+', '-'))
            and after_s[1:].isdigit()
        ):
            s = after_s
        else:
            i = 0
            while i < len(after_s) and after_s[i].isdigit():
                i += 1
            s = after_s[:i] if i > 0 else ""
    if '官匹' in ev.text:
        await try_send(bot, await get_csgohome_info_img(uid))
    else:
        await try_send(bot, await get_csgo_info_img(uid, s))


@csgo_user_info.on_command(('库存', '仓库', '饰品'), block=True)
async def send_csgo_goods_msg(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev, CS2Bind)
    if uid is None:
        return await try_send(bot, UID_HINT)

    await try_send(bot, await get_csgo_goods_img(uid))


@csgo_user_info.on_command(('好友码'), block=True)
async def send_csgo_friend_msg(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev, CS2Bind)
    if uid is None:
        return await try_send(bot, UID_HINT)

    await try_send(bot, await get_csgohome_info_img(uid, True))


@csgo_user_info.on_command(('对局记录', '对局信息', '对局查询'), block=True)
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

    await try_send(bot, await get_csgo_match_img(uid, tag, type_i))


@csgo_user_info.on_command(('搜索'), block=True)
async def send_csgo_search(bot: Bot, ev: Event):
    name = ev.text.strip()
    await try_send(bot, await get_search_players(name))
