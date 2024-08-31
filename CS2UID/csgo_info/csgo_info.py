from pathlib import Path
from typing import Union

from PIL import Image, ImageDraw
from gsuid_core.core import main
from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import easy_paste, draw_pic_with_ring

from ..utils.csgo_api import pf_api
from .csgo_path import TEXTURE, ICON_PATH
from ..utils.api.models import UserDetailData
from ..utils.error_reply import not_msg, get_error
from ..utils.csgo_font import csgo_font_20, csgo_font_30, csgo_font_42
from .utils import (
    save_img,
    add_detail,
    assign_rank,
    make_head_img,
    load_groudback,
    percent_to_img,
    scoce_to_color,
    make_weapen_img,
    simple_paste_img,
)


async def get_csgo_info_img(uid: str, season: str = "") -> Union[str, bytes]:
    detail = await pf_api.get_userdetail(uid, season)

    logger.debug(detail)
    if isinstance(detail, int):
        return get_error(detail)

    try:
        if detail['statusCode'] != 0:
            return f"数据过期，错误代码为{detail['statusCode']}"
    except Exception:
        logger.warning("获取用户详情失败！")

    if len(detail['data']['scoreList']) == 0:
        return not_msg
    return await draw_csgo_info_img(detail['data'])


async def draw_csgo_info_img(detail: UserDetailData) -> bytes | str:
    if not detail:
        return "token已过期"
    name = detail["name"]
    uid = detail["steamId"]
    uid = uid[:4] + "********" + uid[12:]
    avatar = detail["avatar"]

    # 背景图
    img = Image.open(TEXTURE / "base" / "bg.jpg")
    img_bg = Image.open(Path(TEXTURE / "bg" / "1.jpg")).resize((1000, 2400))
    new_alpha = Image.new('L', img_bg.size, 128)
    img_bg_out = Image.merge('RGBA', (img_bg.split()[:3] + (new_alpha,)))
    img.paste(img_bg_out, (0, 0), img_bg_out)

    # 头像

    # head_img = await make_head_img(f"uid：  {uid}", f"昵称：  {name}", avatar)
    # img.paste(head_img, (0, 0), head_img)
    titel_img = Image.open(TEXTURE / "base" / "title_bg.png")
    head = await save_img(avatar, "avatar")
    round_head = await draw_pic_with_ring(head, 100)

    easy_paste(titel_img, round_head, (112, 108), "cc")
    head_draw = ImageDraw.Draw(titel_img)
    head_draw.text((250, 50), name, (255, 255, 255, 255), csgo_font_42)
    head_draw.text((250, 100), uid, (255, 255, 255, 255), csgo_font_30)

    rank_scoce = detail["pvpScore"]
    rank = await assign_rank(rank_scoce)

    img.paste(titel_img, (0, 55), titel_img)

    # 基础信息表
    main1_img = Image.open(TEXTURE / "base" / "banner.png")
    main1_draw = ImageDraw.Draw(main1_img)
    main1_draw.text((50, 10), "基础", (255, 255, 255, 255), csgo_font_42)

    img.paste(main1_img, (0, 350), main1_img)

    # 主信息
    main2_img = Image.open(TEXTURE / "base" / "base_bg.png")

    rank_img = (
        Image.open(TEXTURE / "base" / "rank_logo.png")
        .convert("RGBA")
        .resize((100, 120))
    )
    rank_draw = ImageDraw.Draw(rank_img)
    rank_draw.text((40, 50), rank[0], (255, 255, 255, 255), csgo_font_30, "mm")
    main2_img.paste(rank_img, (50, 50), rank_img)

    main2_draw = ImageDraw.Draw(main2_img)

    main2_draw.text(
        (260, 80),
        f"{detail['avgWe']:.1f}",
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )
    main2_draw.text(
        (415, 80),
        f"{detail['rating']:.2f}",
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )
    main2_draw.text(
        (570, 80),
        f"{detail['rws']:.2f}",
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )
    main2_draw.text(
        (725, 80),
        f"{detail['adr']:.2f}",
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )
    main2_draw.text(
        (880, 80),
        f"{detail['entryKillRatio']* 100 :.2f}%",
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )
    main2_draw.text(
        (105, 230), str(rank_scoce), (255, 255, 255, 255), csgo_font_42, "mm"
    )
    main2_draw.text(
        (260, 230),
        str(detail['cnt']),
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )
    main2_draw.text(
        (415, 230),
        f"{detail['winRate']* 100 :.1f}%",
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )
    main2_draw.text(
        (570, 230),
        f"{detail['kd']:.2f}",
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )
    main2_draw.text(
        (725, 230),
        f"{detail['headShotRatio']* 100 :.1f}%",
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )
    main2_draw.text(
        (880, 230),
        f"{detail['mvpCount']}",
        (255, 255, 255, 255),
        csgo_font_42,
        "mm",
    )

    img.paste(main2_img, (0, 410), main2_img)

    # 地图信息表
    main1_img = Image.open(TEXTURE / "base" / "banner.png")
    main1_draw = ImageDraw.Draw(main1_img)
    main1_draw.text((50, 10), "地图", (255, 255, 255, 255), csgo_font_42)

    img.paste(main1_img, (0, 780), main1_img)

    # 地图
    for i in range(min(4, len(detail['hotMaps']))):

        usr_map = detail['hotMaps'][i]
        # map_layer = Image.new("RGBA", (480, 180), (0, 0, 0, 0))
        # 750*480

        map_img = (await save_img(usr_map['mapImage'], "map")).resize(
            (470, 180)
        )
        new_alpha = Image.new('L', map_img.size, 128)
        map_img = Image.merge('RGBA', (map_img.split()[:3] + (new_alpha,)))

        map_logo = (await save_img(usr_map['mapLogo'], "map")).resize((50, 50))
        easy_paste(map_img, map_logo, (40, 100), "cc")
        map_draw = ImageDraw.Draw(map_img)
        map_draw.text(
            (110, 100),
            usr_map['mapName'],
            (255, 255, 255, 255),
            csgo_font_20,
            "mm",
        )
        map_draw.text(
            (180, 80),
            str(usr_map['totalMatch']),
            (255, 255, 255, 255),
            csgo_font_30,
            "mm",
        )
        map_draw.text(
            (180, 120), "场次", (255, 255, 255, 255), csgo_font_20, "mm"
        )
        map_draw.text(
            (240, 80),
            f"{usr_map['winCount'] / usr_map['totalMatch']*100 :.1f}%",
            (255, 255, 255, 255),
            csgo_font_30,
            "mm",
        )
        map_draw.text(
            (240, 120), "胜率", (255, 255, 255, 255), csgo_font_20, "mm"
        )
        map_draw.text(
            (350, 80),
            f"{usr_map['ratingSum']/ usr_map['totalMatch']:.2f} / {usr_map['totalAdr']/ usr_map['totalMatch']:.0f}",
            (255, 255, 255, 255),
            csgo_font_30,
            "mm",
        )
        map_draw.text(
            (350, 120), "RT/ADR", (255, 255, 255, 255), csgo_font_20, "mm"
        )
        if i % 2 == 0:
            site_x = 20
        else:
            site_x = 520
        site_y = 1080 + 200 * (i // 2 - 1)
        img.paste(map_img, (site_x, site_y), map_img)

    # 武器信息表
    main3_img = Image.open(TEXTURE / "base" / "banner.png")
    main3_draw = ImageDraw.Draw(main3_img)
    main3_draw.text((50, 10), "武器", (255, 255, 255, 255), csgo_font_42)

    img.paste(main3_img, (0, 1300), main3_img)

    # 武器
    for i in range(min(8, len(detail['hotWeapons2']))):

        usr_weapon = detail['hotWeapons2'][i]

        base_img = Image.open(TEXTURE / "base" / "weapon_bg.png").resize(
            (500, 110)
        )
        weapon_img = await save_img(usr_weapon['image'], "weapon")
        weapon_img = weapon_img.resize(
            (int(weapon_img.size[0] * 0.2), int(weapon_img.size[1] * 0.2))
        )
        easy_paste(base_img, weapon_img, (100, 70), "cc")

        weapon_draw = ImageDraw.Draw(base_img)
        weapon_draw.text(
            (77, 17),
            usr_weapon['nameZh'],
            (255, 255, 255, 255),
            csgo_font_20,
            "mm",
        )
        weapon_draw.text(
            (204, 60),
            str(usr_weapon['killNum']),
            (255, 255, 255, 255),
            csgo_font_20,
            "mm",
        )
        weapon_draw.text(
            (375, 60),
            f"{usr_weapon['avgTimeToKill']}ms",
            (255, 255, 255, 255),
            csgo_font_20,
            "mm",
        )
        if usr_weapon['sprayAccuracy'] is None:
            weapon_draw.text(
                (285, 60),
                f"{usr_weapon['firstShotAccuracy']* 100:.2f}%",
                (255, 255, 255, 255),
                csgo_font_20,
                "mm",
            )
        else:
            weapon_draw.text(
                (285, 60),
                f"{usr_weapon['sprayAccuracy']* 100 :.2f}%",
                (255, 255, 255, 255),
                csgo_font_20,
                "mm",
            )
        hdr = (
            f"{usr_weapon['headshotRate']* 100:.2f}"
            if usr_weapon['headshotRate'] is not None
            else 0
        )
        weapon_draw.text(
            (430, 31), f"{hdr}", (255, 255, 255, 255), csgo_font_20, "mm"
        )

        if i % 2 == 0:
            site_x = 0
        else:
            site_x = 500
        site_y = 1520 + 120 * (i // 2 - 1)
        img.paste(base_img, (site_x, site_y), base_img)

    ## 天梯段位
    main4_img = Image.open(TEXTURE / "base" / "banner.png")
    main4_draw = ImageDraw.Draw(main4_img)
    main4_draw.text((50, 10), "分数曲线", (255, 255, 255, 255), csgo_font_42)
    img.paste(main4_img, (0, 1870), main4_img)

    score_list = detail['historyScores']
    if len(score_list) > 0:
        max_score = max(score_list)
        min_score = min(score_list)
        y_start = (min_score // 10) * 10
        y_end = ((max_score // 10) + 1) * 10
        width = 900
        height = 500
        padding = 100
        img_line = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img_line)
        scale = (height - 2 * padding) / (y_end - y_start)
        draw.line(
            [(padding, height - padding), (width - padding, height - padding)],
            fill='black',
        )
        draw.line(
            [(padding, padding), (padding, height - padding)], fill='black'
        )  # Y轴

        # 标注 XY 轴
        for i in range(y_start, y_end + 1, 10):
            y = height - padding - (i - y_start) * scale
            draw.line([(padding - 5, y), (padding, y)], fill='black')
            draw.text(
                (padding - 50, y - 15), str(i), fill='white', font=csgo_font_20
            )
        for i in range(len(score_list)):
            x = padding + i * (width - 2 * padding) / (len(score_list) - 1)
            draw.line(
                [(x, height - padding), (x, height - padding + 5)],
                fill='black',
            )
            draw.text(
                (x - 10, height - padding + 10),
                str(i),
                fill='white',
                font=csgo_font_20,
            )

        points = []
        for i, score in enumerate(reversed(score_list)):
            x = padding + i * (width - 2 * padding) / (len(score_list) - 1)
            y = height - padding - (score - y_start) * scale
            points.append((x, y))
            draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill='red')
            draw.text(
                (x - 15, y - 30), str(score), fill='white', font=csgo_font_20
            )
        draw.line(points, fill='yellow', width=3)
        img.paste(img_line, (50, 1900), img_line)

    # 底
    img_up = Image.open(TEXTURE / "base" / "footer.png")
    img.paste(img_up, (0, 2330), img_up)

    return await convert_img(img)
