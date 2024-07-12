from typing import Union

from gsuid_core.bot import Bot
from gsuid_core.logger import logger

UID_HINT = '[csgo] 你还没有绑定UID，请先使用[csgo绑定]命令进行绑定'
CK_HINT = '[csgo] 你还没有添加可用TOKEN，请先使用[csgo添加tk]命令进行绑定'

error_dict = {
    -51: UID_HINT,
    -511: CK_HINT,
    8000102: '8000102 - auth check failed!\n该tk失效或不正确, 请检查错误tk!',
}


def get_error(retcode: Union[int, str]) -> str:
    return error_dict.get(
        int(retcode),
        f'未知错误, 错误码为{retcode}, 可能由于完美平台隐私设置不允许搜索!',
    )


not_msg = "本赛季完美平台未有匹配记录"
not_player = "查无此人"


async def try_send(bot: Bot, msg: Union[str, bytes]):
    try:
        await bot.send(msg)
    except Exception as E:
        logger.error(E)
        no_inter = "网络开小差了呢，图片没发出来，请重发指令试试"
        await bot.send(no_inter)
