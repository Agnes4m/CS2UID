"""utils/api/api.py 端点常量单元测试。"""

from CS2UID.utils.api import api


def test_required_endpoints_defined():
    for name in (
        "UserInfoAPI",
        "UserSeasonScoreAPI",
        "UserDetailAPI",
        "UserHomematchApi",
        "UserHomeApi",
        "UserSearchApi",
        "MatchDetailAPI",
        "UserSteamPreview",
        "CsgoFall",
        "MatchTitelAPI",
        "MatchAdvanceAPI",
        "LoginAPI",
        "SearchAPI",
        "HomeDetailAPI",
        "HomePageAPI",
        "HomeSeason",
    ):
        assert hasattr(api, name), f"missing endpoint: {name}"


def test_endpoints_use_https():
    for name in (
        "UserInfoAPI",
        "UserDetailAPI",
        "MatchDetailAPI",
        "LoginAPI",
        "SearchAPI",
        "HomeDetailAPI",
    ):
        url = getattr(api, name)
        assert url.startswith("https://"), f"{name} must be https: {url}"


def test_pf_and_5e_hosts_separated():
    """完美域(wmpvp/pwesports)和 5E 域(5eplay)不能混淆。"""
    pf_endpoints = [api.UserInfoAPI, api.UserDetailAPI, api.LoginAPI]
    for url in pf_endpoints:
        assert "wmpvp" in url or "pwesports" in url, f"PF 端点错了: {url}"

    for url in (api.SearchAPI, api.HomeDetailAPI, api.HomeSeason):
        assert "5eplay" in url, f"5E 端点错了: {url}"
