from pathlib import Path
from typing import Dict, Union

import aiofiles
from PIL import Image
from msgspec import json as msgjson
from gsuid_core.help.model import PluginHelp
from gsuid_core.utils.fonts.fonts import core_font
from gsuid_core.help.draw_plugin_help import get_help

from ..version import CS2UID_version

TEXT_PATH = Path(__file__).parent / 'texture2d'
HELP_DATA = Path(__file__).parent / 'Help.json'


async def get_help_data() -> Union[Dict[str, PluginHelp], None]:
    if HELP_DATA.exists():
        async with aiofiles.open(HELP_DATA, 'rb') as file:
            return msgjson.decode(
                await file.read(),
                type=Dict[str, PluginHelp],
            )


async def get_csgo_core_help() -> Union[bytes, str]:
    help_data = await get_help_data()
    if help_data is None:
        return '暂未找到帮助数据...'

    bg_out = Image.open(TEXT_PATH / 'bg.jpg')
    bg_new = Image.new(
        'RGBA', (bg_out.width, bg_out.height), (255, 255, 255, 100)
    )
    bg_out.paste(bg_new, None, bg_new)

    img = await get_help(
        'CS2UID',
        f'版本号:{CS2UID_version}',
        help_data,
        bg_out,
        Image.open(TEXT_PATH / 'icon.png'),
        Image.open(TEXT_PATH / 'badge.png'),
        Image.open(TEXT_PATH / 'banner.png'),
        Image.open(TEXT_PATH / 'button.png'),
        core_font,
        is_dark=False,
        column=4,
        is_gaussian=False,
        text_color=(23, 67, 91),
        sub_c=(49, 110, 144),
    )
    return img
