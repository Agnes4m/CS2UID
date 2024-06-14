from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.utils.database.api import get_uid

from ..utils.error_reply import UID_HINT
from .csgo_info import get_csgo_info_img
from ..utils.database.models import CS2Bind

csgo_user_info = SV('CS2用户信息查询')


@csgo_user_info.on_command(('查询'), block=True)
async def send_csgo_info_msg(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev, CS2Bind)
    if uid is None:
        return await bot.send(UID_HINT)
    await bot.send(await get_csgo_info_img(uid))


# @csgo_user_info.on_command(('对局记录', '对战记录'), block=True)
# async def send_csgo_battle_msg(bot: Bot, ev: Event):
#     uid = await get_uid(bot, ev, CS2Bind)
#     if uid is None:
#         return await bot.send(UID_HINT)
#     await bot.send(await draw_csgo_battle_list_img(ev, uid))
