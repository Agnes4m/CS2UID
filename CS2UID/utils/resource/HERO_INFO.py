import json
from typing import Dict, Union

import aiofiles

from ..lol_api import wg_api
from .RESOURCE_PATH import HERO_DATA_PATH


async def get_hero_data(hero_id: Union[str, int]) -> Dict:
    path = HERO_DATA_PATH / f"{hero_id}.json"
    if not path.exists():
        await wg_api.get_hero_info(hero_id)

    async with aiofiles.open(path, mode='r', encoding='utf-8') as file:
        data = await file.read()
        return json.loads(data)
