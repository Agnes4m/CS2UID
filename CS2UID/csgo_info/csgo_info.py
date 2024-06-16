import datetime
from pathlib import Path
from typing import Union

from PIL import Image, ImageDraw
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.utils import download_pic_to_image
from gsuid_core.utils.fonts.fonts import core_font as csgo_font
from gsuid_core.utils.image.image_tools import draw_pic_with_ring

from ..utils.csgo_api import pf_api
from ..utils.error_reply import get_error
from ..utils.api.models import UserDetailData

TEXTURE = Path(__file__).parent / "texture2d"


async def get_csgo_info_img(uid: str) -> Union[str, bytes]:
    # season_scoce = await pf_api.get_season_scoce(uid)
    # user_info = await pf_api.get_userinfo(uid)
    detail = await pf_api.get_userdetail(uid)
    # logger.info(season_scoce)
    # logger.info(user_info)
    if isinstance(detail, int):
        return get_error(detail)

    return await draw_csgo_info_img(detail['data'])


async def paste_img(img: Image.Image, msg, size, site):
    """贴文字"""
    draw = ImageDraw.Draw(img)
    draw.text(xy=site, text=msg, font=csgo_font(size))


async def assign_rank(rank_score: int) -> str:
    if rank_score < 1000:
        return 'D'
    elif 1000 <= rank_score < 1200:
        return 'D+'
    elif 1200 <= rank_score < 1400:
        return 'C'
    elif 1400 <= rank_score < 1600:
        return 'C+'
    elif 1600 <= rank_score < 1800:
        return 'B'
    elif 1800 <= rank_score < 2000:
        return 'B+'
    elif 2000 <= rank_score < 2200:
        return 'A'
    elif 2200 <= rank_score < 2400:
        return 'A+'
    elif rank_score > 2400:
        return 'S'
    else:
        return 'D'


async def resize_image_to_percentage(img: Image.Image, percentage: float):
    """图片缩放"""
    width, height = img.size
    new_width = int(width * percentage / 100)
    new_height = int(height * percentage / 100)
    out_img = img.resize((new_width, new_height))
    return out_img


async def draw_csgo_info_img(detail: UserDetailData) -> bytes:
    name = detail["name"]
    uid = detail["steamId"]
    uid = uid[:4] + "********" + uid[12:]
    avatar = detail["avatar"]

    img = Image.open(TEXTURE / 'bg.jpg')
    head = await download_pic_to_image(avatar)
    round_head = await draw_pic_with_ring(head, 200)

    img.paste(round_head, (350, 100), round_head)

    firsr_msg = f"{name}  .    UID: {uid}"
    await paste_img(img, firsr_msg, 30, (100, 350))

    rank_scoce = detail["pvpScore"]
    rank = await assign_rank(rank_scoce)
    await paste_img(
        img,
        f"天梯段位:{rank}  天梯段位分:{rank_scoce}  星数:{detail['stars']}",
        30,
        (100, 400),
    )

    await paste_img(img, f"赛季：{detail['seasonId']}", 20, (100, 450))
    await paste_img(img, f"场次：{detail['cnt']}", 20, (100, 480))
    await paste_img(img, f"胜率：{detail['winRate']}", 20, (100, 510))
    await paste_img(img, f"完美RT：{detail['pwRating']}", 20, (100, 540))
    await paste_img(img, f"RWS：{detail['rws']}", 20, (100, 570))
    await paste_img(img, f"ADR：{detail['adr']}", 20, (100, 600))
    await paste_img(img, f"WE评价：{detail['avgWe']}", 20, (100, 630))

    await paste_img(img, f"K/D：{detail['kd']}", 20, (300, 450))
    await paste_img(img, f"击杀数：{detail['kills']}", 20, (300, 480))
    await paste_img(img, f"死亡数：{detail['deaths']}", 20, (300, 510))
    await paste_img(img, f"助攻数：{detail['assists']}", 20, (300, 540))
    await paste_img(img, f"MVP数：{detail['mvpCount']}", 20, (300, 570))
    await paste_img(img, f"爆头率：{detail['headShotRatio']}", 20, (300, 600))
    await paste_img(img, f"首杀率：{detail['entryKillRatio']}", 20, (300, 630))

    await paste_img(img, f"连杀：{detail['multiKill']}", 20, (500, 450))
    await paste_img(img, f"2k：{detail['k2']}", 20, (500, 480))
    await paste_img(img, f"3k：{detail['k3']}", 20, (500, 510))
    await paste_img(img, f"4k：{detail['k4']}", 20, (500, 540))
    await paste_img(img, f"5k：{detail['k5']}", 20, (500, 570))
    await paste_img(img, f"残局：{detail['endingWin']}", 20, (700, 450))
    await paste_img(img, f"vs1：{detail['vs1']}", 20, (700, 474))
    await paste_img(img, f"vs2：{detail['vs2']}", 20, (700, 498))
    await paste_img(img, f"vs3：{detail['vs3']}", 20, (700, 522))
    await paste_img(img, f"vs4：{detail['vs4']}", 20, (700, 546))
    await paste_img(img, f"vs5：{detail['vs5']}", 20, (700, 570))

    """武器"""
    for i in range(4):
        site_x = 100
        site_y = 750
        s = i
        if s == 1:
            site_x += 200
        elif s == 2:
            site_y += 100
        elif s == 3:
            site_x += 200
            site_y += 100

        usr_weapon = detail['hotWeapons'][i]
        weap = await download_pic_to_image(usr_weapon['weaponImage'])
        weap_out = await resize_image_to_percentage(weap, 8)
        # weap_out = await draw_pic_with_ring(weap_out, 5)
        img.paste(weap_out, (site_x, site_y), weap_out)
        await paste_img(
            img, f"{usr_weapon['weaponName']}", 20, (site_x + 80, site_y)
        )
        await paste_img(
            img,
            f"武器击杀：{usr_weapon['weaponKill']}",
            20,
            (site_x, site_y + 30),
        )
        await paste_img(
            img,
            f"武器爆头：{usr_weapon['weaponHeadShot']}",
            20,
            (site_x, site_y + 60),
        )

    """地图战绩"""
    for i in range(2):
        site_x = 500
        site_y = 630
        if i == 1:
            site_y += 350

        usr_map = detail['hotMaps'][i]

        map = await download_pic_to_image(usr_map['mapLogo'])
        # map_out = await resize_image_to_percentage(map, 30)
        map_out = await draw_pic_with_ring(map, 10)
        img.paste(map_out, (site_x + 200, site_y), map_out)

        await paste_img(img, "地图战绩", 20, (site_x, site_y))
        await paste_img(
            img, f"地图：{usr_map['mapName']}", 20, (site_x, site_y + 30)
        )
        await paste_img(
            img, f"场次：{usr_map['totalMatch']}", 20, (site_x, site_y + 60)
        )
        await paste_img(
            img, f"胜场：{usr_map['winCount']}", 20, (site_x, site_y + 90)
        )
        await paste_img(
            img, f"击杀：{usr_map['totalKill']}", 20, (site_x, site_y + 120)
        )
        await paste_img(
            img, f"死亡：{usr_map['deathNum']}", 20, (site_x, site_y + 150)
        )
        await paste_img(
            img, f"首杀：{usr_map['firstKillNum']}", 20, (site_x, site_y + 180)
        )
        await paste_img(
            img,
            f"首死：{usr_map['firstDeathNum']}",
            20,
            (site_x, site_y + 210),
        )
        await paste_img(
            img,
            f"爆头：{usr_map['headshotKillNum']}",
            20,
            (site_x, site_y + 240),
        )
        await paste_img(
            img, f"MVP：{usr_map['matchMvpNum']}", 20, (site_x, site_y + 270)
        )
        await paste_img(
            img, f"RWS：{usr_map['rwsSum']}", 20, (site_x + 200, site_y + 30)
        )
        await paste_img(
            img,
            f"TARD：{usr_map['totalAdr']}",
            20,
            (site_x + 200, site_y + 60),
        )
        await paste_img(
            img,
            f"3K：{usr_map['threeKillNum']}",
            20,
            (site_x + 200, site_y + 90),
        )
        await paste_img(
            img,
            f"4K：{usr_map['fourKillNum']}",
            20,
            (site_x + 200, site_y + 120),
        )
        await paste_img(
            img,
            f"5K：{usr_map['fiveKillNum']}",
            20,
            (site_x + 200, site_y + 150),
        )
        await paste_img(
            img, f"1v3：{usr_map['v3Num']}", 20, (site_x + 200, site_y + 180)
        )
        await paste_img(
            img, f"1v4：{usr_map['v4Num']}", 20, (site_x + 200, site_y + 210)
        )
        await paste_img(
            img, f"1v5：{usr_map['v5Num']}", 20, (site_x + 200, site_y + 240)
        )

    """最近战绩"""
    await paste_img(img, "最近战绩", 20, (60, 1350))
    for i in range(20):
        s = i
        site_x = 60
        site_y = 1400
        if s >= 10:
            site_x += 400
            s -= 10
        while s > 0:
            s -= 1
            site_y += 30

        match = detail['scoreList'][i]
        real_time = datetime.datetime.fromtimestamp(match['time'])
        msg = f"{i+1}. 得分{match['score']} . 时间{real_time}"
        await paste_img(img, msg, 20, (site_x, site_y))

    Create = 'Create by GsCore'
    Power = 'Power by CS2UID'
    Design = 'Design by Agnes Digital'
    Data = 'Data by Perfect World'
    await paste_img(
        img,
        f"{Create} & {Power} & {Design} & {Data}",
        20,
        (20, 1900),
    )
    return await convert_img(img)
