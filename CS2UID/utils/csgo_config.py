# 先导入基础配置模型
from typing import Dict

# 设定一个配置文件（json）保存文件路径
from gsuid_core.data_store import get_res_path
from gsuid_core.utils.plugins_config.models import GSC

# 然后添加到GsCore网页控制台中
from gsuid_core.utils.plugins_config.gs_config import StringConfig

# 建立自己插件的CONFIG_DEFAULT
# 名字无所谓, 类型一定是Dict[str, GSC]，以下为示例，可以添加无数个配置
CONIFG_DEFAULT: Dict[str, GSC] = {}

CONFIG_PATH = get_res_path('CS2UID') / 'config.json'

# 分别传入 配置总名称（不要和其他插件重复），配置路径，以及配置模型
majs_config = StringConfig('CS2UID', CONFIG_PATH, CONIFG_DEFAULT)
