import datetime
from pathlib import Path
from typing import Dict, Union

from PIL import Image
from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.utils import download_pic_to_image
from gsuid_core.utils.image.image_tools import draw_pic_with_ring

from ..utils.csgo_api import pf_api
from ..utils.error_reply import not_msg, get_error
from ..utils.api.models import SteamGet, TagDecoration
from .utils import paste_img, assign_rank, resize_image_to_percentage

TEXTURE = Path(__file__).parent / "texture2d"
FONT_PATH = Path(__file__).parent / "font/萝莉体 第二版.ttf"


async def get_csgo_goods_img(uid: str, count: int) -> Union[str, bytes]:
    detail = await pf_api.get_steamgoods(uid, count)
    # print(detail)

    if isinstance(detail, int):
        return get_error(detail)

    return await draw_csgo_goods_img(detail['result'])


async def draw_csgo_goods_img(detail: SteamGet) -> bytes | str:
    if not detail:
        return "token已过期"
    if not detail["previewItem"]:
        return "你的库存空空如也"
    totalCount = detail["totalCount"]
    totalPrice = detail["totalPrice"]

    # 背景图
    img = Image.open(TEXTURE / "bg" / "3.jpg")

    await paste_img(img, "steam库存信息", 40, (100, 100))
    await paste_img(img, f"总物品数量：{totalCount}", 40, (100, 150))
    await paste_img(img, f"总物品价值：{totalPrice/100}馒头", 40, (100, 200))
    
    for index, one_get in enumerate(detail["previewItem"], start=0):
        site_x = 100
        site_y = 400
        
        row = index // 3  # 当前行数  
        col = index % 3   # 当前列数  
        
        s = index
        
        site_x += 240 * col
        site_y += 180 * row
            
        good = await download_pic_to_image(one_get['picUrl'])
        good_img = await resize_image_to_percentage(good, 12)
        good_img.resize((30, 30))
        # weap_out = await draw_pic_with_ring(weap_out, 5)
        img.paste(good_img, (site_x, site_y), good_img)
        name_out = one_get["name"].split("|")
        
        if len(name_out) == 1:
            await paste_img(img, name_out[0], 20, (site_x + 70, site_y))
        else:

            await paste_img(img, name_out[0].replace("（StatTrak™）",""), 20, (site_x + 70, site_y))
            await paste_img(img, name_out[-1], 20, (site_x, site_y+60))
        
        tag = one_get["decorationTags"]
        tag_data: Dict[str, str]= {}
        for one in tag:
            if one["category"] == "Type":
                """装备，音乐盒，微型冲锋枪"""
                tag_data["类型"] = one["name"]
            if one["category"] == "Quality":
                tag_data["类别"] = one["name"]
            if one["category"] == "Rarity":
                tag_data["品质"] = one["name"]
            if tag_data["类型"] != "音乐盒":
                if one["category"] == "Weapon":
                    tag_data["武器"] = one["name"]
                if one["category"] == "ItemSet":
                    tag_data["收藏品"] = one["name"]
                if one["category"] == "Exterior":
                    tag_data["外观"] = one["name"]
                    
            if tag_data["类型"] in ["音乐盒", "收藏品", "武器箱", "涂鸦"]:
                tag_data["武器"] = ""
                tag_data["收藏品"] = ""
                tag_data["外观"] = ""
                
        if tag_data["类型"] == ["音乐盒", "收藏品", "武器箱", "涂鸦"]:
            await paste_img(
                img, f"{tag_data['类别']}", 20, (site_x + 70, site_y + 30)
            )      
        else:
            await paste_img(
                img, f"{tag_data['类别']}", 20, (site_x + 70, site_y +30)
   
            )
            await paste_img(
                img, f"{tag_data['外观']}", 20, (site_x + 100, site_y +60)
   
            )
            # await paste_img(
            #     img, tag_data["类型"], 20, (site_x+50, site_y)
            # ) 
                        
        await paste_img(
            img, f"cn价格: {one_get['suggestPrice']/100}馒头", 20, (site_x, site_y + 90)
        )
        if one_get['steamPrice'] == 0:
            await paste_img(
                img, "b-steam比例: 无", 20, (site_x, site_y + 120)
            )
        else:
            await paste_img(
                img, 
                f"steam比例: {(one_get['suggestPrice']/one_get['steamPrice']*100):.2f}%", 
                20, 
                (site_x, site_y + 120)
            )
        # await paste_img(
        #     img, f"{tag_data['收藏品']} . {tag_data['类别']}", 20, (site_x, site_y + 120)
        # )            
        if index % 10 == 0:
            logger.info(f"已读取{index}件物品")
    logger.info(f"{totalCount}件物品已读取完毕，准备输出")
    return await convert_img(img)