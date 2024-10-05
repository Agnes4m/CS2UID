from typing import Optional

from sqlmodel import Field
from gsuid_core.utils.database.startup import exec_list
from gsuid_core.utils.database.base_models import Bind, User, with_session
from gsuid_core.webconsole.mount_app import PageSchema, GsAdminModel, site

exec_list.extend(
    [
        'ALTER TABLE CS2Bind ADD COLUMN platform TEXT DEFAULT "pf"',
    ]
)


class CS2Bind(Bind, table=True):
    uid: Optional[str] = Field(default=None, title='CS2UID')
    platform: str = Field(default='pf', title='平台')

    @classmethod
    @with_session
    async def switch_paltform(
        cls,
        session,
        user_id: str,
        bot_id,
        platform: str,
    ) -> int:
        """更改paltform的参数值"""

        data = await cls.update_data(user_id, bot_id, platform=platform)
        return data

    @classmethod
    @with_session
    async def get_paltform(
        cls,
        session,
        user_id: str,
    ):
        """获取paltform的参数值"""
        data = await cls.select_data(user_id)

        return data.platform if data else None


class CS2User(User, table=True):
    uid: Optional[str] = Field(default=None, title='CS2UID')


@site.register_admin
class CS2Bindadmin(GsAdminModel):
    pk_name = 'id'
    page_schema = PageSchema(
        label='CS2绑定管理',
        icon='fa fa-users',
    )  # type: ignore

    # 配置管理模型
    model = CS2Bind


@site.register_admin
class CS2Useradmin(GsAdminModel):
    pk_name = 'id'
    page_schema = PageSchema(
        label='CS2用户管理',
        icon='fa fa-users',
    )  # type: ignore

    # 配置管理模型
    model = CS2User
