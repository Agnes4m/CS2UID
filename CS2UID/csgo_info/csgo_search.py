from typing import Union

from gsuid_core.logger import logger

from ..utils.csgo_api import pf_api
from ..utils.error_reply import get_error, not_player


async def get_search_players(name: str) -> Union[str, bytes]:
    detail = await pf_api.search_player(name)
    logger.debug(detail)
    if isinstance(detail, int):
        return get_error(detail)

    if len(detail['result']) == 0:
        return not_player

    players_msg = detail['result']
    out_msg = ""
    for one_player in players_msg:
        info_msg = f"玩家:{one_player['pvpNickName'].strip()}"
        info_msg += f"({one_player['appNickName']})\n"
        info_msg += f"【ID:{one_player['steamId']}】\n"
        out_msg += f"{info_msg}"
    out_msg += "请输入【csgo绑定uid xxx】来绑定信息"
    return out_msg
