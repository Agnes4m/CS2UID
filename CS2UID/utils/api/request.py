
import json as js
from copy import deepcopy
from typing import Any, Dict, Literal, Optional, Union
from httpx import AsyncClient
from gsuid_core.logger import logger

from ..database.models import CS2User
from .api import UserInfoAPI, DailyStatsAPI, UserSeasonScoreAPI


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
    async def _pf_request(
        self,
        url: str,
        method: Literal['GET', 'POST'] = 'GET',
        header: Dict[str, str] = _HEADER,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,  # noqa: F811
        pwasteamid: Optional[str] = None,
        need_ck: bool = True,
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
                and raw_data['result']['error_code'] != 0
            ):
                return raw_data['result']['error_code']
            return raw_data