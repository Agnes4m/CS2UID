from typing import Optional

from sqlmodel import Field
from gsuid_core.utils.database.base_models import Bind, User
from gsuid_core.webconsole.mount_app import PageSchema, GsAdminModel, site


class CS2Bind(Bind, table=True):
    uid: Optional[str] = Field(default=None, title='CS2UID')


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
