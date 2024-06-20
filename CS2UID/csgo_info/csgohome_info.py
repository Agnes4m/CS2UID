from pathlib import Path

from PIL import Image
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.utils import download_pic_to_image
from gsuid_core.utils.image.image_tools import draw_pic_with_ring

from ..utils.csgo_api import pf_api
from ..utils.error_reply import not_msg, get_error
from .utils import paste_img, resize_image_to_percentage
from ..utils.api.models import UserFall, UserHomedetailData

TEXTURE = Path(__file__).parent / "texture2d"
FONT_PATH = Path(__file__).parent / "font/萝莉体 第二版.ttf"


async def get_csgohome_info_img(uid: str, friend: bool = False):

    detail = await pf_api.get_csgohomedetail(uid)
    fall = await pf_api.get_fall(uid)
    # print(detail)
    
    if isinstance(detail, int) :
        return get_error(detail)
    if isinstance(fall, int) :
        return get_error(fall)    
    if friend:
        return detail['data']["friendCode"]
    if len(detail['data']['hotMaps']) == 0:
        return not_msg
    print(fall)
    return await draw_csgohome_info_img(detail['data'], fall["result"])


async def draw_csgohome_info_img(detail: UserHomedetailData, fall: UserFall) -> bytes | str:
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

    # 等级
    if fall['levelTitle']:
        logo = await download_pic_to_image(fall['levelIcon'])
        round_head = await draw_pic_with_ring(head, 3)
        img.paste(logo, (100, 340), logo)
        
        msg = f"{fall['levelTitle']}-{fall['curLevel']}级  {fall['statusDesc']}"
        await paste_img(img, msg, 30, (250, 380))
        
        await paste_img(img, f"当前经验值{fall['levelUpProgress']}%", 30, (600, 380))
    else:
        await paste_img(img, fall['statusDesc'], 30, (330, 380), is_mid=True)
    await paste_img(
        img,
        f"胜场/场次：{detail['historyWinCount']} / {detail['cnt']}",
        20,
        (100, 450),
    )
    await paste_img(img, f"KD：{detail['kd']:.2f}", 20, (100, 480))
    await paste_img(img, f"RWS：{detail['rws']:.2f}", 20, (100, 510))
    await paste_img(img, f"ADR：{detail['adr']:.2f}", 20, (100, 540))
    await paste_img(img, f"kast：{detail['kast']}", 20, (100, 570))

    await paste_img(
        img, f"爆头率：{detail['headShotRatio']*100:.2f}%", 20, (300, 450)
    )
    await paste_img(
        img, f"首杀率：{detail['entryKillRatio']*100:.2f}%", 20, (300, 480)
    )
    await paste_img(
        img, f"狙首杀：{detail['awpKillRatio']*100:.2f}%", 20, (300, 510)
    )
    await paste_img(
        img, f"闪白率：{detail['flashSuccessRatio']*100:.2f}%", 20, (300, 540)
    )
    await paste_img(img, f"游戏时间：{detail['hours']} h", 20, (300, 570))

    """武器"""
    for i in range(8):
        site_x = 100
        site_y = 700
        s = i
        if s % 2 == 0:
            site_y += 60 * s
        else:
            site_x += 200
            site_y += 60 * (s - 1)

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
            f"使用场次：{usr_weapon['totalMatch']}次",
            20,
            (site_x, site_y + 30),
        )
        avkill = usr_weapon['weaponKill'] / usr_weapon['totalMatch']
        await paste_img(
            img,
            f"场均击杀：{avkill:.2f}",
            20,
            (site_x, site_y + 60),
        )
        whs = usr_weapon['weaponHeadShot'] / usr_weapon['weaponKill']
        await paste_img(
            img,
            f"爆头率：{whs*100:.2f}%",
            20,
            (site_x, site_y + 90),
        )
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

    return await convert_img(img)
