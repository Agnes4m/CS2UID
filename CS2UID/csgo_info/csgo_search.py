from typing import Union

from gsuid_core.logger import logger

from ..utils.csgo_api import api_5e, pf_api
from ..utils.error_reply import get_error, not_player


async def get_search_players(name: str) -> Union[str, bytes]:
    detail = await pf_api.search_player(name)
    logger.debug(detail)

    if isinstance(detail, int):
        return get_error(detail)

    if not detail['result']:
        return not_player

    players_msg = detail['result']
    out_msg = []

    for one_player in players_msg:
        info_msg = (
            f"玩家: {one_player['pvpNickName'].strip()} "
            f"({one_player['appNickName']})\n"
            f"【ID: {one_player['steamId']}】\n"
        )
        out_msg.append(info_msg)

    out_msg.append("请输入【cs绑定uid xxx】来绑定信息")
    return ''.join(out_msg)


async def get_search_players5e(name: str) -> Union[str, bytes]:
    detail = await api_5e.search_player(name)
    logger.info(detail)

    if isinstance(detail, int):
        return get_error(detail)

    if not detail:
        return not_player

    out_msg = [
        f"{index}. {one_player['username'].strip()}\nuid: {one_player['domain']}\n"
        for index, one_player in enumerate(detail, start=1)
    ]
    out_msg.append("请输入【cs绑定5euid xxx】来绑定信息")
    return ''.join(out_msg)
