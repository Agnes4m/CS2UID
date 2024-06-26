from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = Path(__file__).parent / "font/萝莉体 第二版.ttf"


async def paste_img(
    img: Image.Image,
    msg: str,
    size: int,
    site: Tuple[int, int],
    is_mid: bool = False,
    long: Tuple[int, int] = (0, 900),
    color: Tuple[int, int, int, int] = (0, 0, 0, 255),
    is_white: bool = True,
):
    """贴文字"""
    # draw = ImageDraw.Draw(img)

    # 行数
    font = ImageFont.truetype(str(FONT_PATH), size)

    aa, ab, ba, bb = font.getbbox(msg)
    if is_mid:
        # print(font.getbbox(msg))
        site_x = round((long[1] - long[0] - ba + aa) / 2)
        # print(f"横坐标{site_x}")
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
    mask = Image.new('RGBA', (ba - aa + 10, bb - ab + 10), (255, 255, 255, s))
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rectangle(site_white, fill=rect_color)

    draw_mask.text(xy=(5, 5), text=msg, font=font, fill=color)
    img.paste(mask, site, mask)


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
