import random
import json as js
from copy import deepcopy
from typing import Any, Dict, List, Union, Literal, Optional, cast

from httpx import AsyncClient

from gsuid_core.logger import logger

from ..database.models import CS2User
from .api import UserInfoAPI, UserDetailAPI, UserSeasonScoreAPI
from .models import UserInfo, UserSeasonScore, UserDetailRequest


class PerfectWorldApi:
    ssl_verify = False
    _HEADER: Dict[str, str] = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36'
        '(KHTML, like Gecko) perfectworldarena/1.0.24060811   '
        'Chrome/80.0.3987.163'
        'Electron/8.5.5'
        'Safari/537.36',
        'HOST': 'pwaweblogin.wmpvp.com',
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
            logger.debug(raw_data)
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
        header['Content-Type'] = 'application/x-www-form-urlencoded'
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

    async def get_userdetail(self, uid: str):
        uid_token = await self.get_token()
        if uid_token is None:
            return -1

        header = self._HEADER
        header['appversion'] = '3.3.7.154'
        header["HOST"] = "api.wmpvp.com"
        header["User-Agent"] = "okhttp/4.11.0"
        header['Content-Type'] = 'application/json;charset=UTF-8'
        logger.info(f"header: {header}")
        data = await self._pf_request(
            UserDetailAPI,
            header=header,
            method='POST',
            json={
                'toSteamId': uid,
                'csgoSeasonId': "",
                'mySteamId': uid_token[0],
                'accessToken': uid_token[-1]
            },
        )
        # print(data)
        if isinstance(data, int):
            return data
        return cast(UserDetailRequest, data)
