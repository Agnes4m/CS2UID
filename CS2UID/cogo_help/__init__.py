from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

from .get_help import get_csgo_core_help

sv_csgo_help = SV('csgo帮助')


@sv_csgo_help.on_fullmatch(('帮助'))
async def send_help_img(bot: Bot, ev: Event):
    logger.info('开始执行[csgo帮助]')
    im = await get_csgo_core_help()
    await bot.send(im)
