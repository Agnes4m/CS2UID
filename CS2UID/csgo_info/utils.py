from pathlib import Path
from typing import Tuple, Union, Optional

from gsuid_core.logger import logger
from PIL import Image, ImageDraw, ImageFont
from gsuid_core.data_store import get_res_path
from gsuid_core.utils.image.utils import download_pic_to_image
from gsuid_core.utils.image.image_tools import (
    draw_text_by_line,
    draw_pic_with_ring,
)

from .csgo_path import TEXTURE
from ..utils.api.models import UserhomeWeapon, UserDetailhotWeapons2
from ..utils.csgo_font import FONT_MAIN_PATH, FONT_TIELE_PATH, csgo_font_30

ICON_PATH = Path(__file__).parent / 'texture2d/icon'
font_head = ImageFont.truetype(str(FONT_TIELE_PATH), 20)
font_main = ImageFont.truetype(str(FONT_MAIN_PATH), 20)


async def save_img(
    img_url: str, img_type: str, size: Optional[Tuple[int, int]] = None
):
    """下载图片并缓存以读取"""
    map_img = Image.new("RGBA", (200, 600), (0, 0, 0, 255))
    img_path = get_res_path("CS2UID") / img_type / img_url.split("/")[-1]
    img_path.parent.mkdir(parents=True, exist_ok=True)
    if not img_path.is_file():
        for i in range(3):
            try:
                map_img = await download_pic_to_image(img_url)
                if map_img.mode != 'RGBA':
                    map_img = map_img.convert('RGBA')
                if map_img:
                    map_img.save(img_path)
                    break
                logger.warning(f"图片下载错误，正在尝试第{i+2}次")
                if i == 2:
                    raise Exception("图片下载失败！")
            except Exception:
                continue

    else:

        map_img = Image.open(img_path)
        if map_img.mode != 'RGBA':
            map_img = map_img.convert('RGBA')
    if size:
        map_img.resize(size)
    return map_img


async def paste_img(
    img: Image.Image,
    msg: str,
    size: int,
    site: Tuple[int, int] = (0, 0),
    is_mid: bool = False,
    fonts: Optional[str] = None,
    long: Tuple[int, int] = (0, 900),
    color: Union[Tuple[int, int, int, int], str] = (0, 0, 0, 255),
    is_white: bool = True,
):
    """贴文字"""
    # draw = ImageDraw.Draw(img)

    # 字体
    if fonts == "head":
        font = ImageFont.truetype(str(FONT_TIELE_PATH), size)
    else:
        font = ImageFont.truetype(str(FONT_MAIN_PATH), size)

    # 行数
    aa, ab, ba, bb = font.getbbox(msg)
    if is_mid:
        site_x = round((long[1] - long[0] - ba + aa) / 2)
    else:
        site_x = site[0]

    if is_white:
        s = 160
    else:
        s = 0
    # 绘制白色矩形遮罩
    rect_color = (255, 255, 255, 128)
    site_white = (
        site_x + aa - 5,
        site[1] + ab,
        site_x + ba + 5,
        site[1] + bb + 7,
    )
    mask = Image.new(
        'RGBA', (int(ba - aa + 5), int(bb - ab + 5)), (255, 255, 255, s)
    )
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rectangle(site_white, fill=rect_color)

    draw_mask.text(xy=(0, 0), text=msg, font=font, fill=color)
    img.paste(mask, site, mask)


async def simple_paste_img(
    img: Image.Image,
    msg: str,
    site: Tuple[int, int],
    size: int = 20,
    fonts: Optional[str] = None,
    color: Union[Tuple[int, int, int, int], str] = (0, 0, 0, 255),
    max_length: int = 1000,
    center: bool = False,
    line_space: Optional[float] = None,
):
    """无白框贴文字"""
    if size == 20:
        if fonts == "head":
            font = font_head
        else:
            font = font_main
    else:
        if fonts == "head":
            font = ImageFont.truetype(str(FONT_TIELE_PATH), size)
        else:
            font = ImageFont.truetype(str(FONT_MAIN_PATH), size)
    draw = ImageDraw.Draw(img)
    draw.text(site, msg, fill=color, font=font)
    # 以后替换
    draw_text_by_line(
        img=img,
        pos=site,
        text=msg,
        font=font,
        fill=color,
        max_length=max_length,
        center=center,
        line_space=line_space,
    )


async def assign_rank(rank_score: int, is_rank: bool = True):
    if not is_rank:
        return "未定级", 0
    if rank_score < 1000:
        return 'D', rank_score / 1000
    elif 1000 <= rank_score < 1200:
        return 'D+', (rank_score - 1000) / 200
    elif 1200 <= rank_score < 1400:
        return 'C', (rank_score - 1200) / 200
    elif 1400 <= rank_score < 1600:
        return 'C+', (rank_score - 1400) / 200
    elif 1600 <= rank_score < 1800:
        return 'B', (rank_score - 1600) / 200
    elif 1800 <= rank_score < 2000:
        return 'B+', (rank_score - 1800) / 200
    elif 2000 <= rank_score < 2200:
        return 'A', (rank_score - 2000) / 200
    elif 2200 <= rank_score < 2400:
        return 'A+', (rank_score - 2200) / 200
    elif rank_score > 2400:
        return 'S', (rank_score - 2400) / 200
    else:
        return "未定级", 0


async def resize_image_to_percentage(img: Image.Image, percentage: float):
    """图片缩放"""
    width, height = img.size
    new_width = int(width * percentage / 100)
    new_height = int(height * percentage / 100)
    out_img = Image.new(
        'RGBA', (new_width, new_height), color=(255, 255, 255, 255)
    )
    pic_new = img.resize((new_width, new_height))
    out_img.paste(pic_new)
    return out_img


async def add_detail(img: Image.Image):
    Create = 'Create by GsCore'
    Power = 'Power by CS2UID'
    Design = 'Design by Agnes Digital'
    Data = 'Data by Perfect World'
    await paste_img(
        img,
        f"{Create} & {Power} & {Design} & {Data}",
        20,
        (0, 1970),
    )
    return img


async def load_groudback(
    bg_img_path: Path | Image.Image, alpha_percent: float = 0.5
):
    """加载背景图
    透明一半"""
    if isinstance(bg_img_path, Path):
        first_img = Image.open(bg_img_path)
        if first_img.mode != 'RGBA':
            first_img = first_img.convert('RGBA')
    else:
        first_img = bg_img_path
    transparent_img = Image.new(
        'RGBA', first_img.size, (255, 255, 255, int(255 * alpha_percent))
    )
    first_img.paste(transparent_img, None, transparent_img)

    return first_img


async def new_para_img(map_url: str, logo_url: str):
    """生成地图四边形图片
    大小200*600"""
    map_path = get_res_path("CS2UID") / "map"
    map_path.mkdir(parents=True, exist_ok=True)

    # 地图像素为750*480，做渐变遮罩
    map_img = await save_img(map_url, "map")
    if map_img.mode != 'RGBA':
        map_img = map_img.convert('RGBA')

    if map_img.mode != 'RGBA':
        map_img = map_img.convert('RGBA')

    result_img = Image.new('RGBA', map_img.size, (0, 0, 0, 0))
    pixels = result_img.load()

    gradient_length = 100
    start_y = 380
    gradient_scale = 255 / gradient_length

    # 绘制渐变
    for y in range(start_y, start_y + gradient_length):
        alpha = int((y - start_y) * gradient_scale)
        for x in range(map_img.size[0]):
            pixels[x, y] = (0, 0, 0, alpha)

    map_img.paste(result_img, None, result_img)

    logo_img = await save_img(logo_url, "map")

    img = Image.new("RGBA", (200, 600), (0, 0, 0, 255))

    img.paste(map_img.resize((300, 192)))

    # 改成四边形形状
    mask = Image.new('L', img.size, 255)
    draw = ImageDraw.Draw(mask)

    draw.polygon([(0, 0), (200, 0), (0, 80)], fill=0)
    draw.polygon([(0, 600), (200, 520), (200, 600)], fill=0)

    img_data = img.load()
    mask_data = mask.load()
    if img_data and mask_data:
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                if mask_data[x, y] == 0:
                    img_data[x, y] = img_data[x, y][:3] + (0,)

    bg = Image.open(ICON_PATH / "main2.png")
    img.paste(bg, (0, 0), bg)
    img.paste(logo_img.resize((60, 60)), (70, 35), logo_img.resize((60, 60)))

    return img


async def make_head_img(uid: str, name: str, avatar: str):
    """制作图片标题部分
    大小像素900*500
    """
    head_bg = Image.open(ICON_PATH / "header.png")
    if head_bg.mode == 'RGB':
        head_bg = head_bg.convert('RGBA')
    head_img = Image.new("RGBA", head_bg.size, (0, 0, 0, 0))
    head_img.paste(head_bg, (0, 100))

    # 写字
    await simple_paste_img(head_img, name, (35, 130), size=40, fonts="head")
    await simple_paste_img(head_img, uid, (20, 205), size=35, fonts="head")

    head = await save_img(avatar, "map")
    round_head = await draw_pic_with_ring(head, 200)
    head_img.paste(round_head, (620, 70), round_head)

    return head_img


async def make_weapen_img(usr_weapon: UserDetailhotWeapons2):
    """武器图片制作"""
    out_img = Image.open(ICON_PATH / "main1.png").resize((200, 300))
    weap = await save_img(usr_weapon['image'], "weapen")
    weap_out = await resize_image_to_percentage(weap, 14)
    # weap_out = await draw_pic_with_ring(weap_out, 5)
    out_img.paste(weap_out, (40, 25), weap_out)

    await simple_paste_img(
        out_img,
        f"{usr_weapon['nameZh']}",
        (10, 70),
        size=30,
    )
    sa = usr_weapon['sprayAccuracy']
    sa_out = f"{(sa*100):.2f}%" if sa else sa
    hs = usr_weapon['headshotRate']
    hs_out = f"{(hs*100):.2f}%" if hs else hs
    fs = usr_weapon['firstShotAccuracy']
    fs_out = f"{(fs*100):.2f}%" if fs else fs
    print_msg = [
        f"击杀数：{usr_weapon['killNum']}",
        f"首发命中率：{fs_out}",
        f"击杀时间：{usr_weapon['avgTimeToKill']}ms",
        f"扫射精准率：{sa_out}",
        f"爆头率：{hs_out}",
    ]
    color_msg = [
        usr_weapon['levelAvgKillNum'],
        usr_weapon['levelAccuracy'],
        usr_weapon['levelAvgTimeToKill'],
        usr_weapon['levelAvgDamage'],
        usr_weapon['levelHeadshotRate'],
    ]

    index = 0
    for i, one_msg in enumerate(print_msg):
        try:
            await simple_paste_img(
                out_img,
                one_msg,
                (10, 120 + index * 30),
                color=await rank_to_color(color_msg[i]),
            )
            index += 1
        except Exception as E:
            logger.warning(E)

    return out_img


async def make_homeweapen_img(usr_weapon: UserhomeWeapon):
    out_img = Image.open(ICON_PATH / "main1.png").resize((200, 300))
    weap = await save_img(usr_weapon['weaponImage'], "weapen")
    weap_out = await resize_image_to_percentage(weap, 14)
    # weap_out = await draw_pic_with_ring(weap_out, 5)
    out_img.paste(weap_out, (40, 25), weap_out)

    await simple_paste_img(
        out_img, usr_weapon['weaponName'], (10, 70), size=30
    )

    avkill = usr_weapon['weaponKill'] / usr_weapon['totalMatch']
    hs = (
        usr_weapon['weaponHeadShot'] / usr_weapon['weaponKill']
        if usr_weapon['weaponKill']
        else 0
    )
    hs_out = f"{(hs*100):.2f}%" if hs else "0%"

    print_msg = [
        f"使用场次：{usr_weapon['totalMatch']}次",
        f"击杀数：{usr_weapon['weaponKill']}",
        f"场均击杀：{avkill:.2f}",
        f"爆头率：{hs_out}",
    ]

    for index, one_msg in enumerate(print_msg):
        try:
            await simple_paste_img(out_img, one_msg, (10, 120 + index * 30))
        except Exception as E:
            logger.warning(f"Error pasting text to image: {E}")

    return out_img


async def rank_to_color(
    rank: str, green: str = "A", blue: str = "B", red: str = "C"
):
    if rank.upper() == green:
        return "green"
    if rank.upper() == blue:
        return "blue"
    if rank.upper() == red:
        return "red"
    return "black"


async def scoce_to_color(
    rank: float, green: float, blue: float, red: float = 0
):
    switch = {green: "green", blue: "blue", red: "red"}
    return switch.get(rank, "black")


async def percent_to_img(percent: float, size: tuple = (211, 46)):
    """由半分比转化为图"""
    # 31*46
    img_none = Image.open(ICON_PATH / "none.png")
    img_yellow = Image.open(ICON_PATH / "yellow.png")
    img_out = Image.new("RGBA", (211, 46), (0, 0, 0, 0))
    for i in range(10):
        if percent > 0:
            img_out.paste(img_yellow, (i * 20, 0), img_yellow)
        else:
            img_out.paste(img_none, (i * 20, 0), img_none)
        percent -= 0.1
    return img_out.resize(size)


async def draw_card(
    img: Image.Image,
    txt: str,
    site: Tuple[int, int],
    color: str = "blue",
    font=csgo_font_30,
):
    """画卡片"""
    pj_img = Image.open(TEXTURE / "base" / "color" / f"{color}.png")
    pj_text = txt
    pj_draw = ImageDraw.Draw(pj_img)
    pj_draw.text(
        (118, 24), f"评价：{pj_text}", (255, 255, 255, 255), font, "mm"
    )
    img.paste(pj_img, site, pj_img)

def parse_s_value(text: str) -> str:
    """解析 s 值，从文本中提取数字部分"""
    after_s = text.lower().split("s")[-1]
    if after_s.isdigit() or (after_s.startswith(("+", "-")) and after_s[1:].isdigit()):
        return after_s
    
    # 提取连续数字
    i = 0
    while i < len(after_s) and after_s[i].isdigit():
        i += 1
    
    return after_s[:i] if i > 0 else ""