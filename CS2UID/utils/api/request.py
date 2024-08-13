import json as js
import random
from copy import deepcopy
from typing import Any, Dict, List, Literal, Optional, Union, cast

# from gsuid_core.logger import logger
from httpx import AsyncClient

from ..database.models import CS2User
from .api import (
    CsgoFall,
    MatchDetailAPI,
    MatchTitelAPI,
    UserDetailAPI,
    UserHomeApi,
    UserHomematchApi,
    UserInfoAPI,
    UserSearchApi,
    UserSeasonScoreAPI,
    UserSteamPreview,
)
from .models import (
    MatchDetail,
    MatchTitel,
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


class PerfectWorldApi:
    ssl_verify = False
    _HEADER: Dict[str, str] = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36'
        '(KHTML, like Gecko) perfectworldarena/1.0.24060811   '
        'Chrome/80.0.3987.163'
        'Electron/8.5.5'
        'Safari/537.36',
        'Content-Type': 'application/json;charset=UTF-8'
    }

    async def get_token(self) -> Optional[List[str]]:
        user_list = await CS2User.get_all_user()
        if user_list:
            user: CS2User = random.choice(user_list)
            if user.uid is None:
                raise Exception('No valid uid')
            token = await CS2User.get_user_cookie_by_uid(user.uid)
            if token is None:
                raise Exception('No valid cookie')
            return [user.uid, token]

    async def _pf_request(
        self,
        url: str,
        method: Literal['GET', 'POST'] = 'GET',
        header: Dict[str, str] = _HEADER,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        pwasteamid: Optional[str] = None,
        need_tk: bool = True,
    ) -> Union[Dict, int]:
        header = deepcopy(self._HEADER)

        if pwasteamid:
            header['pwasteamid'] = pwasteamid

        if json:
            method = 'POST'
        async with AsyncClient(verify=self.ssl_verify) as client:
            resp = await client.request(
                method,
                url=url,
                headers=header,
                params=params,
                json=json,
                data=data,
                timeout=300,
            )
            try:
                raw_data = await resp.json()
            except:  # noqa: E722
                _raw_data = resp.text
                try:
                    raw_data = js.loads(_raw_data)
                except:  # noqa: E722
                    raw_data = {
                        'result': {'error_code': -999, 'data': _raw_data}
                    }
            try:
                if not raw_data['result']:
                    return raw_data
            except Exception:
                return raw_data
            if (
                'result' in raw_data
                and 'error_code' in raw_data['result']
                and raw_data['code'] != 0
            ):
                return raw_data['result']['error_code']
            return raw_data

    async def get_season_scoce(self, uid: str):
        uid_token = await self.get_token()

        if uid_token is None:
            return -1
        token = uid_token[-1]
        params = {'uid': uid, 'access_token': token}
        data = await self._pf_request(
            UserSeasonScoreAPI,
            params=params,
            pwasteamid=uid,
        )
        if isinstance(data, int):
            return data
        return cast(UserSeasonScore, data)

    async def get_userinfo(self, uid: str):
        uid_token = await self.get_token()
        if uid_token is None:
            return -1
        token = uid_token[-1]
        if token is None:
            return -1
        header = self._HEADER
        header['pwasteamid'] = uid
        header['Accept'] = 'application/json, text/plain, */*'
        data = await self._pf_request(
            UserInfoAPI,
            header=header,
            method='POST',
            data={
                'with_green_info': 1,
                'with_perfect_power': 1,
                'with_roles': 1,
                'with_ladder_info': '1',
                'access_token': token,
                'lang': 'zh',
            },
        )
        if isinstance(data, int):
            return data
        return cast(UserInfo, data)

    async def get_userdetail(self, uid: str, season: str = ""):
        uid_token = await self.get_token()
        if uid_token is None:
            return -1
        if season:
            season = "S" + season
            print("赛季", season)
        header = self._HEADER
        header['appversion'] = '3.3.7.154'
        header["User-Agent"] = "okhttp/4.11.0"
        data = await self._pf_request(
            UserDetailAPI,
            header=header,
            method='POST',
            json={
                'toSteamId': uid,
                'csgoSeasonId': season,
                'mySteamId': uid_token[0],
                'accessToken': uid_token[-1],
            },
        )
        if isinstance(data, int):
            return data
        return cast(UserDetailRequest, data)

    async def get_steamgoods(self, uid: str):
        uid_token = await self.get_token()
        if uid_token is None:
            return -1

        header = self._HEADER
        header['appversion'] = '3.3.7.154'
        header["User-Agent"] = "okhttp/4.11.0"
        header['token'] = uid_token[-1]
        data = await self._pf_request(
            UserSteamPreview,
            header=header,
            params={'steamId': uid, 'previewSize': 20},
        )
        if isinstance(data, int):
            return data
        return cast(SteamGetRequest, data)

    async def get_csgohomematch(self, uid: str, search_number: int = 11):
        """国服对战信息"""
        uid_token = await self.get_token()
        if uid_token is None:
            return -1

        header = self._HEADER
        header['appversion'] = '3.3.7.154'
        header["User-Agent"] = "okhttp/4.11.0"
        header['token'] = uid_token[-1]
        data = await self._pf_request(
            UserHomematchApi,
            header=header,
            method='POST',
            json={
                'toSteamId': uid,
                'dataSource': 0,
                'mySteamId': uid_token[0],
                'pageSize': search_number,
            },
        )
        if isinstance(data, int):
            return data
        return cast(UserHomeRequest, data)

    async def get_csgopfmatch(self, uid: str, csgoSeasonId: int, type: int):
        """完美对战信息"""
        uid_token = await self.get_token()
        if uid_token is None:
            return -1

        header = self._HEADER
        header['appversion'] = '3.3.7.154'
        header["User-Agent"] = "okhttp/4.11.0"
        header['token'] = uid_token[-1]
        data = await self._pf_request(
            UserHomematchApi,
            header=header,
            method='POST',
            json={
                'toSteamId': uid,
                'mySteamId': uid_token[0],
                'csgoSeasonId': 'recent',
                'pvpType': type,
                # -1全部, 41pro, 12/0天梯, 20巅峰赛, 27周末联赛, 14自定义
                'page': 1,
                'pageSize': 50,
                'dataSource': csgoSeasonId,
                # 1是官匹，3是完美
            },
        )
        if isinstance(data, int):
            return data
        return cast(UserMatchRequest, data)

    async def get_csgohomedetail(self, uid: str, search_number: int = 11):
        """国服个人信息"""
        uid_token = await self.get_token()
        if uid_token is None:
            return -1

        header = self._HEADER
        header['appversion'] = '3.3.7.154'
        header["User-Agent"] = "okhttp/4.11.0"
        header['token'] = uid_token[-1]
        data = await self._pf_request(
            UserHomeApi,
            header=header,
            method='POST',
            json={
                'toSteamId': uid,
                'mySteamId': uid_token[0],
                'accessToken': uid_token[-1],
            },
        )
        if isinstance(data, int):
            return data
        return cast(UserHomedetailRequest, data)

    async def get_fall(self, uid: str):
        """获取掉落箱子信息"""
        uid_token = await self.get_token()
        if uid_token is None:
            return -1

        header = self._HEADER
        header['appversion'] = '3.3.7.154'
        header["User-Agent"] = "okhttp/4.11.0"
        header['token'] = uid_token[-1]
        data = await self._pf_request(
            CsgoFall,
            header=header,
            params={'steamId': uid, 'token': uid_token[-1]},
        )
        if isinstance(data, int):
            return data
        return cast(UserFallRequest, data)

    async def search_player(self, keyword: str):
        """搜索玩家信息"""
        uid_token = await self.get_token()
        if uid_token is None:
            return -1

        header = self._HEADER
        header['appversion'] = '3.3.7.154'
        header["User-Agent"] = "okhttp/4.11.0"
        header['token'] = uid_token[-1]
        data = await self._pf_request(
            UserSearchApi,
            header=header,
            method='POST',
            json={
                'keyword': keyword,
                'page': 1,
            },
        )
        if isinstance(data, int):
            return data
        return cast(UserSearchRequest, data)

    async def get_match_mvp(self, matchid: str):
        """搜索对局MVP信息"""
        uid_token = await self.get_token()
        if uid_token is None:
            return -1

        header = self._HEADER
        header['appversion'] = '3.3.7.154'
        header['accesstoken'] = uid_token[-1]
        data = await self._pf_request(
            MatchTitelAPI,
            header=header,
            params={'matchId': matchid},
        )
        if isinstance(data, int):
            return data
        elif data['statusCode'] != 0 :
            return data['data']
        return cast(MatchTitel, data['data'])

    async def get_match_detail(self, matchid: str):
        """搜索对局详情信息"""
        uid_token = await self.get_token()
        if uid_token is None:
            return -1

        header = self._HEADER
        header['appversion'] = '3.3.7.154'
        header['accesstoken'] = uid_token[-1]
        data = await self._pf_request(
            MatchDetailAPI,
            header=header,
            json={
                'matchId': f"PVP@{matchid}",
                "platform": "admin",
                "dataSource": 3,
                },
        )
        if isinstance(data, int):
            return data
        elif data['statusCode'] != 0 :
            return data['data']
        return cast(MatchDetail, data['data'])
