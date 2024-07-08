from pathlib import Path

from PIL import Image
from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img

from .config import ICON_PATH
from ..utils.csgo_api import pf_api
from ..utils.error_reply import not_msg, get_error
from ..utils.api.models import UserFall, UserHomedetailData
from .utils import (
    save_img,
    add_detail,
    new_para_img,
    make_head_img,
    load_groudback,
    percent_to_img,
    simple_paste_img,
    make_homeweapen_img,
    resize_image_to_percentage,
)

TEXTURE = Path(__file__).parent / "texture2d"
FONT_PATH = Path(__file__).parent / "font/萝莉体 第二版.ttf"


async def get_csgohome_info_img(uid: str, friend: bool = False):

    detail = await pf_api.get_csgohomedetail(uid)
    fall = await pf_api.get_fall(uid)
    # print(detail)

    if isinstance(detail, int):
        return get_error(detail)
    if isinstance(fall, int):
        return get_error(fall)
    if friend:
        return detail['data']["friendCode"]
    if len(detail['data']['hotMaps']) == 0:
        return not_msg
    # print(fall)
    return await draw_csgohome_info_img(detail['data'], fall["result"])


async def draw_csgohome_info_img(
    detail: UserHomedetailData, fall: UserFall
) -> bytes | str:
    if not detail:
        return "token已过期"
    name = detail["nickName"]
    uid = detail["steamId"]
    uid = uid[:4] + "********" + uid[12:]
    avatar = detail["avatar"]

    # 背景图
    img = await load_groudback(Path(TEXTURE / "bg" / "2.jpg"))

    # 头像
    head_img = await make_head_img(f"uid：  {uid}", f"昵称：  {name}", avatar)

    img.paste(head_img, (0, 0), head_img)

    # 等级箱子
    level_img = Image.open(ICON_PATH / "main1.png").resize((700, 400))

    if fall['levelTitle']:
        logo = await save_img(fall['levelIcon'], "logo")
        logo = await resize_image_to_percentage(logo, 50)
        level_img.paste(logo, (40, 30), logo)

        msg = (
            f"{fall['levelTitle']}-{fall['curLevel']}级  {fall['statusDesc']}"
        )
        await simple_paste_img(level_img, msg, (100, 30), 30)

        await simple_paste_img(
            level_img, f"当前经验值{fall['levelUpProgress']}%", (100, 100), 30
        )
        rank_img = await percent_to_img(fall['levelUpProgress'] / 100)
        level_img.paste(rank_img, (350, 95), rank_img)
    else:
        await simple_paste_img(level_img, fall['statusDesc'], (100, 50), 40)

    await simple_paste_img(
        level_img,
        f"胜场/场次：{detail['historyWinCount']} / {detail['cnt']}",
        (50, 150),
    )
    await simple_paste_img(level_img, f"KD：{detail['kd']:.2f}", (50, 190))
    await simple_paste_img(level_img, f"RWS：{detail['rws']:.2f}", (50, 230))
    await simple_paste_img(level_img, f"ADR：{detail['adr']:.2f}", (50, 270))
    await simple_paste_img(level_img, f"kast：{detail['kast']}", (50, 310))

    await simple_paste_img(
        level_img, f"爆头率：{detail['headShotRatio']*100:.2f}%", (300, 150)
    )
    await simple_paste_img(
        level_img, f"首杀率：{detail['entryKillRatio']*100:.2f}%", (300, 190)
    )
    await simple_paste_img(
        level_img, f"狙首杀：{detail['awpKillRatio']*100:.2f}%", (300, 230)
    )
    await simple_paste_img(
        level_img,
        f"闪白率：{detail['flashSuccessRatio']*100:.2f}%",
        (300, 270),
    )
    await simple_paste_img(
        level_img, f"游戏时间：{detail['hours']} h", (300, 310)
    )
    img.paste(level_img, (100, 300), level_img)

    """武器"""
    for i in range(min(8, len(detail['hotWeapons']))):
        site_x = 20
        site_y = 720
        s = i
        if s >= 4:
            site_y += 310
            s -= 4
        site_x += 220 * s

        usr_weapon = detail['hotWeapons'][i]

        one_weapen_img = await make_homeweapen_img(usr_weapon)
        img.paste(one_weapen_img, (site_x, site_y), one_weapen_img)

    """地图战绩"""
    map_msg_list = detail['hotMaps']
    logger.info(f"地图种数{len(map_msg_list)}")

    if map_msg_list is None:
        pass
    s = min(4, len(map_msg_list))
    for i in range(s):
        site_x = 10 + i * 220
        site_y = 1350
        usr_map = map_msg_list[i]
        map_img = await new_para_img(usr_map['mapImage'], usr_map['mapLogo'])
        img.paste(map_img, (site_x, site_y), map_img)

        Match = usr_map['totalMatch']
        await simple_paste_img(
            img,
            f"场次：{usr_map['totalMatch']}",
            (site_x + 10, site_y + 200),
            color=(255, 255, 255, 255),
        )
        win_percent = usr_map['winCount'] / Match
        await simple_paste_img(
            img,
            f"胜率：{win_percent*100:.2f}%",
            (site_x + 10, site_y + 240),
            color=(255, 255, 255, 255),
        )
        await simple_paste_img(
            img,
            f"K/D：{usr_map['totalKill']} / {usr_map['deathNum']}",
            (site_x + 10, site_y + 280),
            color=(255, 255, 255, 255),
        )
        await simple_paste_img(
            img,
            f"首杀：{usr_map['firstKillNum']}",
            (site_x + 10, site_y + 320),
            color=(255, 255, 255, 255),
        )
        headshotpercent = usr_map['headshotKillNum'] / usr_map['totalKill']
        await simple_paste_img(
            img,
            f"爆头率：{headshotpercent*100:.2f}%",
            (site_x + 10, site_y + 360),
            color=(255, 255, 255, 255),
        )
        await simple_paste_img(
            img,
            f"MVP：{usr_map['matchMvpNum']}",
            (site_x + 10, site_y + 400),
            color=(255, 255, 255, 255),
        )
        rws = usr_map['rwsSum'] / Match
        await simple_paste_img(
            img,
            f"RWS：{rws:.2f}",
            (site_x + 10, site_y + 440),
            color=(255, 255, 255, 255),
        )
        adr = usr_map['totalAdr'] / Match
        await simple_paste_img(
            img,
            f"ARD：{adr:.2f}",
            (site_x + 10, site_y + 480),
            color=(255, 255, 255, 255),
        )
        rt = usr_map['ratingSum'] / Match
        await simple_paste_img(
            img,
            f"RT：{rt:.2f}",
            (site_x + 10, site_y + 520),
            color=(255, 255, 255, 255),
        )

    return await convert_img(await add_detail(img))
