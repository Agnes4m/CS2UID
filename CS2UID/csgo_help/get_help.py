from typing import Dict
from pathlib import Path

import aiofiles
from PIL import Image
from msgspec import json as msgjson
from gsuid_core.sv import get_plugin_available_prefix
from gsuid_core.help.model import PluginHelp
from gsuid_core.help.draw_new_plugin_help import get_new_help

from ..version import CS2UID_version

HELP_DATA = Path(__file__).parent / 'help.json'
ICON_PATH = Path(__file__).parent / 'icon_path'
TEXT_PATH = Path(__file__).parent / 'texture2d'
ICON = TEXT_PATH / 'icon.png'

PREFIX = get_plugin_available_prefix('CS2UID')

def get_footer():
    return Image.open(TEXT_PATH / 'footer.png')


async def get_help_data() -> Dict[str, PluginHelp]:
    async with aiofiles.open(HELP_DATA, 'rb') as file:
        return msgjson.decode(await file.read(), type=Dict[str, PluginHelp])


async def get_help():
    return await get_new_help(
        plugin_name='CS2UID',
        plugin_info={f'v{CS2UID_version}': ''},
        plugin_icon=Image.open(ICON),
        plugin_help=await get_help_data(),
        plugin_prefix=PREFIX,
        help_mode='dark',
        banner_bg=Image.open(
            TEXT_PATH / 'banner_bg.jpg',
        ),
        banner_sub_text='所有CS玩家集体向瓦投降!',
        help_bg=Image.open(TEXT_PATH / 'bg.jpg'),
        cag_bg=Image.open(TEXT_PATH / 'cag_bg.png'),
        item_bg=Image.open(TEXT_PATH / 'item.png'),
        icon_path=ICON_PATH,
        footer=get_footer(),
        enable_cache=True,
    )
