from pathlib import Path
from typing import List, Union

from PIL import Image
from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.utils import download_pic_to_image
from gsuid_core.utils.image.image_tools import draw_pic_with_ring

from ..utils.csgo_api import pf_api
from ..utils.api.models import Match
from ..utils.error_reply import get_error
from .utils import paste_img, add_detail, load_groudback

TEXTURE = Path(__file__).parent / "texture2d"
FONT_PATH = Path(__file__).parent / "font/萝莉体 第二版.ttf"
green_logo = Image.open(TEXTURE / 'green.png')


async def get_csgo_match_img(
    uid: str, tag: int, _type: int
) -> Union[str, bytes]:
    detail = await pf_api.get_csgopfmatch(uid, tag, _type)
    logger.debug(detail)
    if isinstance(detail, dict) and detail['data'] is None:
        return detail['errorMessage']
    if tag == 1:
        msg = await pf_api.get_csgohomedetail(uid)
        if isinstance(msg, int):
            return get_error(msg)
        name = msg['data']['nickName']
        avatar = msg['data']['avatar']
    else:
        msg = await pf_api.get_userdetail(uid)
        if isinstance(msg, int):
            return get_error(msg)
        name = msg['data']['name']
        avatar = msg['data']['avatar']
    if isinstance(detail, int):
        return get_error(detail)

    # 类型
    if tag == 1:
        match_type = "国服竞技"
    else:
        if tag == -1:
            match_type = "完美平台对战"
        elif tag == 12:
            match_type = "完美普通天梯"
        elif tag == 41:
            match_type = "完美官匹Pro"
        elif tag == 20:
            match_type = "完美巅峰赏金"
        elif tag == 27:
            match_type = "完美周末联赛"
        elif tag == 14:
            match_type = "完美自定义"
        else:
            match_type = "完美平台对战"

    return await draw_csgo_match_img(
        detail['data']['matchList'], name, avatar, uid, match_type
    )


async def create_one_match_img(detail: Match) -> Image.Image:
    if detail['score1'] == detail['score2']:
        color = (128, 128, 128, 128)
    elif detail['team'] == detail['winTeam']:
        color = (0, 255, 0, 128)
    else:
        color = (255, 0, 0, 128)

    img = Image.new("RGBA", (800, 80), color=color)
    logo = await download_pic_to_image(detail['mapLogo'])
    round_logo = await draw_pic_with_ring(logo, 50)
    img.paste(round_logo, (10, 10), round_logo)

    await paste_img(
        img, f"比分 {detail['score1']}:{detail['score2']}", 35, (80, 0)
    )
    await paste_img(img, detail['endTime'], 20, (70, 50))

    await paste_img(img, detail['mapName'], 30, (250, 0))
    await paste_img(img, f"{detail['mode']}", 20, (250, 50))

    await paste_img(img, f"RT: {detail['rating']}", 30, (400, 0))
    await paste_img(
        img,
        f"{detail['kill']}/{detail['death']}/{detail['assist']}",
        20,
        (400, 50),
    )
    await paste_img(img, f"WE: {detail['we']}", 30, (550, 0))

    await paste_img(img, f"分{detail['pvpScore']}", 30, (680, 0))
    if detail['pvpScoreChange']:
        await paste_img(img, f"变化{detail['pvpScoreChange']}", 20, (700, 50))
    else:
        await paste_img(img, "-", 20, (700, 50))

    return img


async def draw_csgo_match_img(
    detail: List[Match], name: str, avatar: str, uid: str, match_type: str
) -> bytes | str:
    if not detail:
        return "token已过期"

    uid = uid[:4] + "********" + uid[12:]

    # 背景图
    img = await load_groudback(Path(TEXTURE / "bg" / "4.jpg"))

    # 头像
    if img.mode == 'RGB':
        img = img.convert('RGBA')
    head = await download_pic_to_image(avatar)
    round_head = await draw_pic_with_ring(head, 200)
    img.paste(round_head, (350, 50), round_head)

    await paste_img(img, f"昵称：  {name}", 40, (300, 300), is_mid=True)
    await paste_img(img, f"uid：  {uid}", 20, (330, 350), is_mid=True)

    await paste_img(img, match_type, 28, (50, 300))

    for i in range(12):
        if i >= len(detail):
            break
        one_img = await create_one_match_img(detail[i])
        img.paste(one_img, (50, 400 + 120 * i), one_img)
        if detail[i]['greenMatch']:

            img.paste(green_logo, (20, 400 + 120 * i), green_logo)

    return await convert_img(await add_detail(img))
    return await convert_img(await add_detail(img))
