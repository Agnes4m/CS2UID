


from pathlib import Path
from typing import List, Union

from PIL import Image, ImageDraw

from gsuid_core.logger import logger
from gsuid_core.utils.fonts.fonts import core_font as csgo_font
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import draw_pic_with_ring
from gsuid_core.utils.image.utils import download_pic_to_image

from ..utils.api.models import SeasonScore, UsrInfo
from ..utils.csgo_api import pf_api
from ..utils.error_reply import get_error

TEXTURE = Path(__file__).parent / "texture2d"

async def get_csgo_info_img(uid: str) -> Union[str, bytes]:
    season_scoce = await pf_api.get_season_scoce(uid)
    user_info = await pf_api.get_userinfo(uid)
    # logger.info(season_scoce) 
    # logger.info(user_info)    
    if isinstance(season_scoce, int):
        return get_error(season_scoce)
    if isinstance(user_info, int):
        return get_error(user_info)

    return await draw_csgo_info_img(
        season_scoce['data'], user_info['data']
    )

async def paste_img(img: Image.Image, msg, size, site):
    """贴文字"""
    draw = ImageDraw.Draw(img) 
    draw.text(xy=site , text=msg, font=csgo_font(size))

async def draw_csgo_info_img(
    season: List[SeasonScore], user: UsrInfo
    ) -> bytes:
    nickname = user['nickname']
    uid = user['uid']
    uid = uid[:4] + "********" + uid[12:]  
    avatar = user['avatar']
    # lastLoginTime = user['lastLoginTime']
    pwLevel = user['pwLevel']
    score = user['score']
    ladderGrade = user['ladderGrade']
    now_s = season[0]['season']
    
    img = Image.open(TEXTURE / 'bg.jpg')
    head = await download_pic_to_image(avatar)
    round_head = await draw_pic_with_ring(head, 200)
    
    img.paste(round_head, (350, 100), round_head)
    
    firsr_msg = f"{nickname}  .  UID: {uid}"
    await paste_img(img, firsr_msg, 40, (100, 400))
    await paste_img(img, "—————————完美对战平台—————————", 40, (0, 500))
    await paste_img(img, f"当前赛季：{now_s}", 40, (100, 600))
    await paste_img(img, f"段位战力：{score}", 40, (100, 700))
    await paste_img(img, f"段位评分：{ladderGrade}", 40, (100, 800))

    await paste_img(img, f"完美等级：{pwLevel}级", 40, (500, 600))

    await paste_img(img, "Create by GsCore & Power by CS2UID & Design by Agnes Digital & Data by Perfect World", 20, (20, 1900))
    return await convert_img(img)
