

from typing import Union

from gsuid_core.models import Event
from gsuid_core.logger import logger

from ..utils.csgo_api import pf_api
from ..utils.error_reply import get_error


async def draw_csgo_info_img(ev: Event, uid: str) -> Union[str, bytes]:
    season_scoce = await pf_api.get_season_scoce(uid)
    user_info = await pf_api.get_userinfo(uid)
    # logger.info(season_scoce) 
    # logger.info(user_info)    
    s_list = [season_scoce, user_info]
    for i in s_list:
        if isinstance(i,int):
            return get_error(i)
    

    return "输出成功，检查控制台"
