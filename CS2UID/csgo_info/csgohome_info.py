import random
import datetime
from pathlib import Path
from typing import Tuple, Union

from PIL import Image, ImageDraw, ImageFont

from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.utils import download_pic_to_image
from gsuid_core.utils.image.image_tools import draw_pic_with_ring

from ..utils.csgo_api import pf_api
from ..utils.error_reply import get_error
from ..utils.api.models import UserHomedetailData
from .utils import paste_img, assign_rank, resize_image_to_percentage

TEXTURE = Path(__file__).parent / "texture2d"
FONT_PATH = Path(__file__).parent / "font/萝莉体 第二版.ttf"


async def get_csgohome_info_img(uid: str) -> Union[str, bytes]:

    detail = await pf_api.get_csgohomedetail(uid)
    print(detail)
    if isinstance(detail, int):
        return get_error(detail)

    return await draw_csgohome_info_img(detail['data'])


async def draw_csgohome_info_img(detail: UserHomedetailData) -> bytes | str:
    if not detail:
        return "token已过期"
    name = detail["nickName"]
    uid = detail["steamId"]
    uid = uid[:4] + "********" + uid[12:]
    avatar = detail["avatar"]

    # 背景图
    img = Image.open(TEXTURE / "bg" / "2.jpg")

    # 头像
    if img.mode == 'RGB':
        img = img.convert('RGBA')
    head = await download_pic_to_image(avatar)
    round_head = await draw_pic_with_ring(head, 200)
    img.paste(round_head, (350, 50), round_head)

    await paste_img(img, f"昵称：  {name}", 40, (300, 300), is_mid=True)
    await paste_img(img, f"uid：  {uid}", 20, (330, 350), is_mid=True)

    await paste_img(img, f"胜场/场次：{detail['historyWinCount']} / {detail['cnt']}", 20, (100, 450))
    await paste_img(img, f"KD：{detail['kd']:.2f}", 20, (100, 480))
    await paste_img(img, f"RWS：{detail['rws']:.2f}", 20, (100, 510))
    await paste_img(img, f"ADR：{detail['adr']:.2f}", 20, (100, 540))
    await paste_img(img, f"kast：{detail['kast']}", 20, (100, 570))

    await paste_img(img, f"爆头率：{detail['headShotRatio']*100:.2f}%", 20, (300, 450))
    await paste_img(img, f"首杀率：{detail['entryKillRatio']*100:.2f}%", 20, (300, 480))
    await paste_img(img, f"狙首杀：{detail['awpKillRatio']*100:.2f}%", 20, (300, 510))
    await paste_img(img, f"闪白率：{detail['flashSuccessRatio']*100:.2f}%", 20, (300, 540))
    await paste_img(img, f"游戏时间：{detail['hours']} h", 20, (300, 570))

    x_values = [10 + i*10 for i in range(20)] 
    y_values = detail["historyRatings"]
    # 设定图像大小和背景颜色  
    image_width = 400  
    image_height = 300  
    background_color = (255, 255, 255, 0)  # 白色背景  

    # 创建一个新的图像和绘图对象 
    image = Image.new('RGBA', (image_width, image_height), background_color)  
    draw = ImageDraw.Draw(image)  
    
    # 设定y轴的最大值和最小值，用于缩放数据到图像上  
    y_max = max(y_values)  
    y_min = min(y_values)  
    y_range = y_max - y_min  
    
    # 绘制x轴和y轴（可选）  
    draw.line([(0, image_height - 10), (image_width - 10, image_height - 10)], fill=(0, 0, 0), width=2)  # x轴  
    draw.line([(10, 0), (10, image_height - 10)], fill=(0, 0, 0), width=2)  # y轴（部分）  
    
    # 绘制数据点并连接它们  
    previous_x = None  
    previous_y = None  
    for x, y in zip(x_values, y_values):  
        # 将y值转换为图像上的像素位置（反转，因为图像的原点在左上角）  
        y_pixel = image_height - int((y - y_min) / y_range * (image_height - 20)) - 10  # 减去10是为了给轴留一些空间  
        x_pixel = x  
        
        # 绘制数据点（可选）  
        draw.point((x_pixel, y_pixel), fill=(0, 0, 255))  # 蓝色数据点  
        
        # 如果不是第一个点，则连接前一个点和当前点  
        if previous_x and previous_y is not None:  
            draw.line([(previous_x, previous_y), (x_pixel, y_pixel)], fill=(0, 0, 255), width=2)  # 蓝色线条  
        
        # 更新前一个点的位置  
        previous_x = x_pixel  
        previous_y = y_pixel  
    await paste_img(img, "rating变化", 40, (0, 0))
    img.paste(image, (100, 600), image)

    return await convert_img(img)
