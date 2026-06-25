import json as js
from copy import deepcopy
from typing import Any, Literal, cast

import httpx

from gsuid_core.logger import logger

from ..cache import cs2_cache
from .api import (
    CsgoFall,
    EventCardDetailAPI,
    EventListAPI,
    EventMatchListAPI,
    EventVrsInvitesAPI,
    HomeDetailAPI,
    HomePageAPI,
    HomeSeason,
    LoginAPI,
    MatchAdvanceAPI,
    MatchDetailAPI,
    MatchTitelAPI,
    SearchAPI,
    UserDetailAPI,
    UserHomeApi,
    UserHomematchApi,
    UserInfoAPI,
    UserSearchApi,
    UserSeasonScoreAPI,
    UserSteamPreview,
)
from .models import (
    AccountInfo,
    EventCardDetailResponse,
    EventListResponse,
    EventMatchListResponse,
    EventVrsInvitesResponse,
    MatchAdvance,
    MatchTitel,
    MatchTotal,
    SteamGetRequest,
    UserDetailRequest,
    UserFallRequest,
    UserHomedetailRequest,
    UserHomeRequest,
    UserInfo,
    UserMatchRequest,
    UserSearchRequest,
    UserSeasonScore,
)
from .models_5e import SearchRequest5, UserHomeDetail5, UserSeason5
from .perf import get_coalescer, get_pool, token_manager
from .safe_log import safe_log_response

# 网络错误码
NETWORK_ERROR = -999
TOKEN_MISSING = -1


def _is_success_response(data: Any) -> bool:
    """仅当响应体表明业务成功时才缓存,避免缓存 4013 等错误响应。"""
    if not isinstance(data, dict):
        return False
    code = data.get("statusCode")
    return code is None or code == 0


def _check_api_error(data: Any) -> int | None:
    """如果响应体中 statusCode != 0,返回 int 错误码;否则返回 None。"""
    if not isinstance(data, dict):
        return None
    code = data.get("statusCode")
    if isinstance(code, int) and code != 0:
        return code
    return None


METHOD = Literal["GET", "POST"]

_PF_HEADER: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36"
        "(KHTML, like Gecko) perfectworldarena/1.0.24060811   "
        "Chrome/80.0.3987.163"
        "Electron/8.5.5"
        "Safari/537.36"
    ),
    "Content-Type": "application/json;charset=UTF-8",
}

_5E_HEADER: dict[str, str] = {
    "User-Agent": "okhttp/3.14.9",
    "version": "6.2.2",
}


def _parse_json(resp: httpx.Response) -> dict[str, Any] | int:
    """解析响应 JSON,失败时返回 NETWORK_ERROR 包装。"""
    text = resp.text
    try:
        return cast(dict[str, Any], resp.json())
    except (ValueError, js.JSONDecodeError):
        try:
            return cast(dict[str, Any], js.loads(text))
        except (ValueError, js.JSONDecodeError):
            logger.warning(f"[CS2] 响应非 JSON: {text[:200]}")
            return {
                "result": {"error_code": NETWORK_ERROR, "data": text},
            }


class PerfectWorldApi:
    """完美世界平台 API 客户端。"""

    ssl_verify = False

    async def get_token(self):
        return await token_manager.get_random_token("pf")

    async def _do_request(
        self,
        method: METHOD,
        url: str,
        header: dict[str, str],
        params: dict[str, Any] | None,
        json: dict[str, Any] | None,
        data: dict[str, Any] | None,
    ) -> dict[str, Any] | int:
        pool = get_pool()
        resp = await pool.request(
            method,
            url=url,
            headers=header,
            params=params,
            json=json,
            data=data,
        )
        logger.debug(
            f"[CS2][PF] {method} {url} -> {resp.status_code} {safe_log_response(resp.text)}"
        )

        raw = _parse_json(resp)
        if isinstance(raw, int):
            return raw

        try:
            if not raw.get("result"):
                return raw
        except AttributeError:
            return raw

        result = raw.get("result", {})
        if "error_code" in result:
            return result["error_code"]
        if raw.get("code") not in (0, 1):
            return raw["code"]
        return raw

    async def _pf_request(
        self,
        url: str,
        method: METHOD = "GET",
        header: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        pwasteamid: str | None = None,
    ) -> dict[str, Any] | int:
        merged_header = (
            deepcopy(header) if header is not None else deepcopy(_PF_HEADER)
        )
        if pwasteamid:
            merged_header["pwasteamid"] = pwasteamid
        if json:
            method = "POST"

        async def _do() -> dict[str, Any] | int:
            return await self._do_request(
                method, url, merged_header, params, json, data
            )

        if method == "GET":
            coalescer = get_coalescer()
            return await coalescer.request(
                _do, method, url, params or {}, merged_header.get("token")
            )
        return await _do()

    async def get_season_scoce(self, uid: str) -> UserSeasonScore | int:
        uid_token = await self.get_token()
        if uid_token is None:
            return TOKEN_MISSING
        data = await self._pf_request(
            UserSeasonScoreAPI,
            params={"uid": uid, "access_token": uid_token[-1]},
            pwasteamid=uid,
        )
        if isinstance(data, int):
            return data
        return cast(UserSeasonScore, data)

    async def get_userinfo(self, uid: str) -> UserInfo | int:
        uid_token = await self.get_token()
        if uid_token is None:
            return TOKEN_MISSING
        token = uid_token[-1]
        if token is None:
            return TOKEN_MISSING
        header = deepcopy(_PF_HEADER)
        header["pwasteamid"] = uid
        header["Accept"] = "application/json, text/plain, */*"
        data = await self._pf_request(
            UserInfoAPI,
            header=header,
            method="POST",
            data={
                "with_green_info": 1,
                "with_perfect_power": 1,
                "with_roles": 1,
                "with_ladder_info": "1",
                "access_token": token,
                "lang": "zh",
            },
        )
        if isinstance(data, int):
            return data
        return cast(UserInfo, data)

    async def get_userdetail(
        self, uid: str, season: str = ""
    ) -> UserDetailRequest | int:
        cached = cs2_cache.get("pf", uid, "get_userdetail", season=season)
        if cached is not None:
            logger.debug(f"[CS2][PF][Cache] get_userdetail 命中 uid={uid}")
            return cached

        uid_token = await self.get_token()
        if uid_token is None:
            return TOKEN_MISSING
        if season:
            season = "S" + season
            logger.info(f"[CS2][PF] 赛季: {season}")
        header = deepcopy(_PF_HEADER)
        header["appversion"] = "3.4.6.164"
        header["User-Agent"] = "okhttp/4.11.0"
        data = await self._pf_request(
            UserDetailAPI,
            header=header,
            method="POST",
            json={
                "toSteamId": uid,
                "csgoSeasonId": season,
                "mySteamId": uid_token[0],
                "accessToken": uid_token[-1],
            },
        )
        if isinstance(data, int):
            return data

        err = _check_api_error(data)
        if err is not None:
            return err

        if _is_success_response(data):
            cs2_cache.set(
                "pf", uid, "get_userdetail", data, ttl=300, season=season
            )
        return cast(UserDetailRequest, data)

    async def get_steamgoods(self, uid: str) -> SteamGetRequest | int:
        cached = cs2_cache.get("pf", uid, "get_steamgoods")
        if cached is not None:
            logger.debug(f"[CS2][PF][Cache] get_steamgoods 命中 uid={uid}")
            return cached

        uid_token = await self.get_token()
        if uid_token is None:
            return TOKEN_MISSING

        header = deepcopy(_PF_HEADER)
        header["appversion"] = "3.4.6.164"
        header["User-Agent"] = "okhttp/4.11.0"
        header["token"] = uid_token[-1]
        data = await self._pf_request(
            UserSteamPreview,
            header=header,
            params={"steamId": uid, "previewSize": 20},
        )
        if isinstance(data, int):
            return data

        err = _check_api_error(data)
        if err is not None:
            return err

        if _is_success_response(data):
            cs2_cache.set("pf", uid, "get_steamgoods", data, ttl=300)
        return cast(SteamGetRequest, data)

    async def get_csgohomematch(
        self, uid: str, search_number: int = 11
    ) -> UserHomeRequest | int:
        """国服对战信息。"""
        uid_token = await self.get_token()
        if uid_token is None:
            return TOKEN_MISSING

        header = deepcopy(_PF_HEADER)
        header["appversion"] = "3.4.6.164"
        header["User-Agent"] = "okhttp/4.11.0"
        header["token"] = uid_token[-1]
        data = await self._pf_request(
            UserHomematchApi,
            header=header,
            method="POST",
            json={
                "toSteamId": uid,
                "dataSource": 0,
                "mySteamId": uid_token[0],
                "pageSize": search_number,
            },
        )
        if isinstance(data, int):
            return data
        return cast(UserHomeRequest, data)

    async def get_csgopfmatch(
        self, uid: str, csgoSeasonId: int, type: int
    ) -> UserMatchRequest | int:
        """完美对战信息。"""
        uid_token = await self.get_token()
        if uid_token is None:
            return TOKEN_MISSING

        header = deepcopy(_PF_HEADER)
        header["appversion"] = "3.4.6.164"
        header["User-Agent"] = "okhttp/4.11.0"
        header["token"] = uid_token[-1]
        data = await self._pf_request(
            UserHomematchApi,
            header=header,
            method="POST",
            json={
                "toSteamId": uid,
                "mySteamId": uid_token[0],
                "csgoSeasonId": "recent",
                "pvpType": type,
                # -1全部, 41pro, 12/0天梯, 20巅峰赛, 27周末联赛, 14自定义
                "page": 1,
                "pageSize": 50,
                "dataSource": csgoSeasonId,
                # 1是官匹，3是完美
            },
        )
        if isinstance(data, int):
            return data
        return cast(UserMatchRequest, data)

    async def get_csgohomedetail(
        self, uid: str, search_number: int = 11
    ) -> UserHomedetailRequest | int:
        """国服个人信息。"""
        cached = cs2_cache.get("pf", uid, "get_csgohomedetail")
        if cached is not None:
            logger.debug(f"[CS2][PF][Cache] get_csgohomedetail 命中 uid={uid}")
            return cached

        uid_token = await self.get_token()
        if uid_token is None:
            return TOKEN_MISSING

        header = deepcopy(_PF_HEADER)
        header["appversion"] = "3.4.6.164"
        header["User-Agent"] = "okhttp/4.11.0"
        header["token"] = uid_token[-1]
        data = await self._pf_request(
            UserHomeApi,
            header=header,
            method="POST",
            json={
                "toSteamId": uid,
                "mySteamId": uid_token[0],
                "accessToken": uid_token[-1],
            },
        )
        if isinstance(data, int):
            return data

        err = _check_api_error(data)
        if err is not None:
            return err

        if _is_success_response(data):
            cs2_cache.set("pf", uid, "get_csgohomedetail", data, ttl=300)
        return cast(UserHomedetailRequest, data)

    async def get_fall(self, uid: str) -> UserFallRequest | int:
        """获取掉落箱子信息。"""
        uid_token = await self.get_token()
        if uid_token is None:
            return TOKEN_MISSING

        header = deepcopy(_PF_HEADER)
        header["appversion"] = "3.4.6.164"
        header["User-Agent"] = "okhttp/4.11.0"
        header["token"] = uid_token[-1]
        data = await self._pf_request(
            CsgoFall,
            header=header,
            params={"steamId": uid, "token": uid_token[-1]},
        )
        if isinstance(data, int):
            return data
        return cast(UserFallRequest, data)

    async def search_player(self, keyword: str) -> UserSearchRequest | int:
        """搜索玩家信息。"""
        uid_token = await self.get_token()
        if uid_token is None:
            return TOKEN_MISSING

        header = deepcopy(_PF_HEADER)
        header["appversion"] = "3.4.6.164"
        header["User-Agent"] = "okhttp/4.11.0"
        header["token"] = uid_token[-1]
        data = await self._pf_request(
            UserSearchApi,
            header=header,
            method="POST",
            json={"keyword": keyword, "page": 1},
        )
        if isinstance(data, int):
            return data
        return cast(UserSearchRequest, data)

    async def get_match_mvp(self, matchid: str) -> MatchTitel | int:
        """搜索对局 MVP 信息。"""
        uid_token = await self.get_token()
        if uid_token is None:
            return TOKEN_MISSING

        header = deepcopy(_PF_HEADER)
        header["appversion"] = "3.4.6.164"
        header["accesstoken"] = uid_token[-1]
        data = await self._pf_request(
            MatchTitelAPI,
            header=header,
            params={"matchId": matchid},
        )
        if isinstance(data, int):
            return data
        if data.get("statusCode") != 0:
            return data.get("data", NETWORK_ERROR)
        return cast(MatchTitel, data["data"])

    async def get_match_detail(self, matchid: str) -> MatchTotal | int:
        """搜索对局详情信息。"""
        uid_token = await self.get_token()
        if uid_token is None:
            return TOKEN_MISSING

        header = deepcopy(_PF_HEADER)
        header["appversion"] = "3.4.6.164"
        header["accesstoken"] = uid_token[-1]
        data = await self._pf_request(
            MatchDetailAPI,
            header=header,
            json={
                "matchId": f"{matchid}",
                "platform": "admin",
                "dataSource": 3,
            },
        )
        if isinstance(data, int):
            return data
        if data.get("statusCode") != 0:
            return cast(str, data.get("data", NETWORK_ERROR))
        return cast(MatchTotal, data["data"])

    async def get_match_advance(self, matchid: str) -> MatchAdvance | int:
        """搜索对局其他数据。"""
        uid_token = await self.get_token()
        if uid_token is None:
            return TOKEN_MISSING

        header = deepcopy(_PF_HEADER)
        header["appversion"] = "3.4.6.164"
        header["accesstoken"] = uid_token[-1]
        data = await self._pf_request(
            MatchAdvanceAPI,
            header=header,
            params={"matchId": matchid.replace("PVP@", "")},
        )
        if isinstance(data, int):
            return data
        if data.get("statusCode") != 0:
            return cast(str, data.get("data", NETWORK_ERROR))
        return cast(MatchAdvance, data["data"])

    async def login_pf(
        self, phone_number: str, code: str
    ) -> AccountInfo | int:
        """手机号和验证码登录。"""
        header = deepcopy(_PF_HEADER)
        header["appversion"] = "3.4.6.164"
        data = await self._pf_request(
            LoginAPI,
            header=header,
            json={
                "appId": 2,
                "mobilePhone": phone_number,
                "securityCode": code,
            },
        )
        if isinstance(data, int):
            return data
        if data.get("statusCode") != 0:
            return cast(str, data.get("data", NETWORK_ERROR))
        return cast(AccountInfo, data["result"]["accountInfo"])

    async def get_event_match_list(
        self, match_time: str = ""
    ) -> EventMatchListResponse | int:
        """获取赛事对局列表。

        Args:
            match_time: 时间范围,格式 ``"2026-06-24 00:00:00"``。
                       默认留空由服务端决定最近时间。
        """
        uid_token = await self.get_token()
        if uid_token is None:
            return TOKEN_MISSING

        header = deepcopy(_PF_HEADER)
        header["appversion"] = "4.0.9.215"
        header["token"] = uid_token[-1]
        header["platform"] = "h5_android"
        header["Referer"] = "https://news.wmpvp.com/"
        header["Origin"] = "https://news.wmpvp.com"
        header["X-Requested-With"] = "XMLHttpRequest"
        header["appTheme"] = "0"
        header["User-Agent"] = (
            "Mozilla/5.0 (Linux; Android 16; V2329A Build/BP2A.250605.031.A3; wv) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
            "Chrome/138.0.7204.179 Mobile Safari/537.36 "
            "EsportsApp Version=4.0.9.215"
        )

        params: dict[str, str] = {}
        if match_time:
            params["matchTime"] = match_time

        data = await self._pf_request(
            EventMatchListAPI,
            header=header,
            params=params,
        )
        if isinstance(data, int):
            return data
        err = _check_api_error(data)
        if err is not None:
            return err
        return cast(EventMatchListResponse, data)

    async def get_event_card_detail(
        self, start_date: str, end_date: str
    ) -> EventCardDetailResponse | int:
        """获取赛事日历(按月分组)。"""
        uid_token = await self.get_token()
        if uid_token is None:
            return TOKEN_MISSING

        header = deepcopy(_PF_HEADER)
        header["appversion"] = "4.0.9.215"
        header["token"] = uid_token[-1]
        header["platform"] = "h5_android"
        header["Referer"] = "https://news.wmpvp.com/"
        header["Origin"] = "https://news.wmpvp.com"
        header["sec-ch-ua-platform"] = "Android"
        header["sec-ch-ua"] = (
            '"Not)A;Brand";v="8", "Chromium";v="138", "Android WebView";v="138"'
        )
        header["sec-ch-ua-mobile"] = "?1"
        header["X-Requested-With"] = "XMLHttpRequest"
        header["User-Agent"] = (
            "Mozilla/5.0 (Linux; Android 16; V2329A Build/BP2A.250605.031.A3; wv) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
            "Chrome/138.0.7204.179 Mobile Safari/537.36 "
            "EsportsApp Version=4.0.9.215"
        )

        data = await self._pf_request(
            EventCardDetailAPI,
            header=header,
            params={"startDate": start_date, "endDate": end_date},
        )
        if isinstance(data, int):
            return data
        err = _check_api_error(data)
        if err is not None:
            return err
        return cast(EventCardDetailResponse, data)

    async def get_vrs_invites(self) -> EventVrsInvitesResponse | int:
        """获取 VRS 邀请赛事列表。"""
        uid_token = await self.get_token()
        if uid_token is None:
            return TOKEN_MISSING

        header = deepcopy(_PF_HEADER)
        header["appversion"] = "4.0.9.215"
        header["token"] = uid_token[-1]
        header["platform"] = "h5_android"
        header["Referer"] = "https://news.wmpvp.com/"
        header["Origin"] = "https://news.wmpvp.com"
        header["sec-ch-ua-platform"] = "Android"
        header["sec-ch-ua"] = (
            '"Not)A;Brand";v="8", "Chromium";v="138", "Android WebView";v="138"'
        )
        header["sec-ch-ua-mobile"] = "?1"
        header["X-Requested-With"] = "XMLHttpRequest"
        header["User-Agent"] = (
            "Mozilla/5.0 (Linux; Android 16; V2329A Build/BP2A.250605.031.A3; wv) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
            "Chrome/138.0.7204.179 Mobile Safari/537.36 "
            "EsportsApp Version=4.0.9.215"
        )

        data = await self._pf_request(
            EventVrsInvitesAPI,
            header=header,
        )
        if isinstance(data, int):
            return data
        err = _check_api_error(data)
        if err is not None:
            return err
        return cast(EventVrsInvitesResponse, data)

    async def get_event_list(
        self,
        event_sub_type: int = 0,
        page_num: int = 1,
        page_size: int = 10,
        event_type: int = 1,
    ) -> EventListResponse | int:
        """获取赛事列表(按子类型筛选)。

        event_type: 1=近期(未开始), 2=往期(已结束)
        eventSubType: 0=全部, 4=Major, 5=热门, 1=Blast系列,
                      2=ESL系列, 3=IEM系列, 6=PGL系列,
                      7=PWE系列, 8=SL系列, 9=FISSURE系列, 10=其他
        """
        uid_token = await self.get_token()
        if uid_token is None:
            return TOKEN_MISSING

        header = deepcopy(_PF_HEADER)
        header["appversion"] = "4.0.9.215"
        header["accessToken"] = uid_token[-1]
        header["platform"] = "h5_android"
        header["Referer"] = "https://news.wmpvp.com/"
        header["Origin"] = "https://news.wmpvp.com"
        header["sec-ch-ua-platform"] = "Android"
        header["sec-ch-ua"] = (
            '"Not)A;Brand";v="8", "Chromium";v="138", "Android WebView";v="138"'
        )
        header["sec-ch-ua-mobile"] = "?1"
        header["X-Requested-With"] = "XMLHttpRequest"
        header["device"] = "rGPSv1782353861kXAkUgT3R0c"
        header["User-Agent"] = (
            "Mozilla/5.0 (Linux; Android 16; V2329A Build/BP2A.250605.031.A3; wv) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
            "Chrome/138.0.7204.179 Mobile Safari/537.36 "
            "EsportsApp Version=4.0.9.215"
        )

        data = await self._pf_request(
            EventListAPI,
            header=header,
            params={
                "pageNum": page_num,
                "pageSize": page_size,
                "type": event_type,
                "eventSubType": event_sub_type,
            },
        )
        if isinstance(data, int):
            return data
        err = _check_api_error(data)
        if err is not None:
            return err
        return cast(EventListResponse, data)


class FiveEApi:
    """5E 平台 API 客户端。"""

    ssl_verify = False

    async def get_stoken(self):
        return await token_manager.get_random_token("5e")

    async def _5e_request(
        self,
        url: str,
        method: METHOD = "GET",
        header: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        pwasteamid: str | None = None,
    ) -> dict[str, Any] | int:
        merged_header = (
            deepcopy(header) if header is not None else deepcopy(_5E_HEADER)
        )
        if pwasteamid:
            merged_header["pwasteamid"] = pwasteamid
        if json:
            method = "POST"

        pool = get_pool()
        resp = await pool.request(
            method,
            url=url,
            headers=merged_header,
            params=params,
            json=json,
            data=data,
        )
        logger.debug(
            f"[CS2][5E] {method} {url} -> {resp.status_code} {safe_log_response(resp.text)}"
        )

        raw = _parse_json(resp)
        if isinstance(raw, int):
            return raw
        if raw.get("success") is not True or raw.get("errcode") != 0:
            return raw.get("errcode", NETWORK_ERROR)
        return raw

    async def search_player(self, keyword: str) -> list[SearchRequest5] | int:
        """搜索玩家信息。"""
        header = deepcopy(_5E_HEADER)
        uid_token = await self.get_stoken()
        if uid_token is None:
            logger.info("[CS2][5E]找不到stoken")
            return 1
        header["token"] = uid_token[1]
        data = await self._5e_request(
            SearchAPI,
            header=header,
            method="GET",
            params={"keywords": keyword, "page": 1},
        )
        if isinstance(data, int):
            return data
        return cast(list[SearchRequest5], data["data"]["list"])

    async def get_user_detail(self, domain: str) -> UserHomeDetail5 | int:
        """获取玩家信息。"""
        cached = cs2_cache.get("5e", domain, "get_user_detail")
        if cached is not None:
            logger.debug(
                f"[CS2][5E][Cache] get_user_detail 命中 domain={domain}"
            )
            return cached

        header = deepcopy(_5E_HEADER)
        data = await self._5e_request(
            f"{HomeDetailAPI}/{domain}",
            header=header,
            method="GET",
        )
        if isinstance(data, int):
            return data

        err = _check_api_error(data)
        if err is not None:
            return err

        if _is_success_response(data):
            cs2_cache.set("5e", domain, "get_user_detail", data, ttl=300)
        return cast(UserHomeDetail5, data["data"])

    async def get_user_homepage(self, domain: str) -> UserDetailRequest | int:
        """获取玩家库存信息。"""
        header = deepcopy(_5E_HEADER)
        uid_token = await self.get_stoken()
        if uid_token is None:
            logger.info("[CS2][5E]找不到stoken")
            return 1
        header["Content-Type"] = "application/x-www-form-urlencoded"
        data = await self._5e_request(
            HomePageAPI,
            header=header,
            method="POST",
            json={"domain": domain},
        )
        if isinstance(data, int):
            return data
        return cast(UserDetailRequest, data["data"])

    async def get_user_homeall(
        self, domain: str, year: str, season: str
    ) -> UserSeason5 | int:
        """获取年度信息。"""
        header = deepcopy(_5E_HEADER)
        data = await self._5e_request(
            f"{HomeSeason}/{domain}",
            header=header,
            method="GET",
            params={"matchType": "9", "year": year, "season": season},
        )
        if isinstance(data, int):
            return data
        return cast(UserSeason5, data["data"])
