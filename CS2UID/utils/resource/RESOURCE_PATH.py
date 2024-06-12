from gsuid_core.data_store import get_res_path

MAIN_PATH = get_res_path() / 'LOLegendsUID'

CONFIG_PATH = MAIN_PATH / 'config.json'

RESOURCE_PATH = MAIN_PATH / 'resource'
HERO_DATA_PATH = MAIN_PATH / 'hero_data'

HERO_LIST = HERO_DATA_PATH / 'hero_list.json'

CARD_PATH = RESOURCE_PATH / 'card'
ITEMS_PATH = RESOURCE_PATH / 'items'
RUNESPERK_PATH = RESOURCE_PATH / 'runesperk'
SKINS_PATH = RESOURCE_PATH / 'skins'
SKINS_SPLASH_PATH = SKINS_PATH / 'splash'
SKINS_ORIGINAL_PATH = SKINS_PATH / 'original'
SKINS_LOADING_PATH = SKINS_PATH / 'loading'
USERICON_PATH = RESOURCE_PATH / 'usericon'
CHAMPIONS_PATH = RESOURCE_PATH / 'champions'
SUMMONABILITY_PATH = RESOURCE_PATH / 'summonability'
TIER_PATH = RESOURCE_PATH / 'tier'


def init_dir():
    for i in [
        MAIN_PATH,
        RESOURCE_PATH,
        CARD_PATH,
        ITEMS_PATH,
        RUNESPERK_PATH,
        SKINS_PATH,
        SKINS_SPLASH_PATH,
        SKINS_ORIGINAL_PATH,
        USERICON_PATH,
        CHAMPIONS_PATH,
        SUMMONABILITY_PATH,
        SKINS_LOADING_PATH,
        TIER_PATH,
        HERO_DATA_PATH,
    ]:
        i.mkdir(parents=True, exist_ok=True)


init_dir()
