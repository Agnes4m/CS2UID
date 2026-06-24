from pathlib import Path

from sqlmodel import Field

from gsuid_core.utils.database.base_models import Bind, User, with_session
from gsuid_core.utils.database.startup import exec_list
from gsuid_core.webconsole.mount_app import GsAdminModel, PageSchema, site

# 数据库迁移 SQL 集中管理
# 详见 migrations.sql
_MIGRATIONS_FILE = Path(__file__).parent / "migrations.sql"
if _MIGRATIONS_FILE.is_file():
    for stmt in _MIGRATIONS_FILE.read_text(encoding="utf-8").split(";"):
        cleaned = stmt.strip()
        if not cleaned or cleaned.startswith("--"):
            continue
        if cleaned not in exec_list:
            exec_list.append(cleaned)


class CS2Bind(Bind, table=True):
    uid: str | None = Field(default=None, title="CS2UID")
    platform: str = Field(default="pf", title="平台")
    domain: str = Field(default="", title="5e域名")

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
    async def get_platform(
        cls,
        session,
        user_id: str,
    ):
        """获取paltform的参数值"""
        data = await cls.select_data(user_id)

        return data.platform if data else None

    @classmethod
    @with_session
    async def get_domain(
        cls,
        session,
        user_id: str,
    ):
        """获取domain的参数值"""
        data = await cls.select_data(user_id)

        return data.domain if data else None


class CS2User(User, table=True):
    uid: str | None = Field(default=None, title="CS2UID")


@site.register_admin
class CS2Bindadmin(GsAdminModel):
    pk_name = "id"
    page_schema = PageSchema(
        label="CS2绑定管理",
        icon="fa fa-users",
    )  # type: ignore

    # 配置管理模型
    model = CS2Bind


@site.register_admin
class CS2Useradmin(GsAdminModel):
    pk_name = "id"
    page_schema = PageSchema(
        label="CS2用户管理",
        icon="fa fa-users",
    )  # type: ignore

    # 配置管理模型
    model = CS2User
