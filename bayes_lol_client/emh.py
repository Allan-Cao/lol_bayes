from bayes_lol_client import BayesAPIClient
from bayes_lol_client.errors import NotFoundError
from typing import Optional, Union
import pytz
import backoff
from requests.exceptions import (
    JSONDecodeError,
    ConnectionError,
    ConnectTimeout,
    Timeout,
    ReadTimeout,
)
import requests
from datetime import datetime


class BayesEMH(object):
    endpoint = "https://lolesports-api.bayesesports.com/"

    def __init__(self, username=None, password=None):
        self.api = BayesAPIClient(endpoint=self.endpoint, username=username, password=password)

    def get_game_summary(self, platform_game_id):
        return self.get_asset(platform_game_id, "GAMH_SUMMARY").json()

    def get_game_details(self, platform_game_id):
        return self.get_asset(platform_game_id, "GAMH_DETAILS").json()

    def get_game_replay(self, platform_game_id):
        return self.get_asset(platform_game_id, "ROFL_REPLAY").content

    @staticmethod
    @backoff.on_exception(
        backoff.expo,
        (
            JSONDecodeError,
            ConnectionError,
            ConnectTimeout,
            Timeout,
            ReadTimeout,
        ),
        max_time=60,
    )
    def download_game_asset(asset_url):
        return requests.get(asset_url)

    def get_asset(self, platform_game_id, asset_name):
        asset_url = self.api.do_api_call(
            f"GET", f"emh/v1/games/{platform_game_id}/download", data={"type": asset_name}
        )["url"]
        return self.download_game_asset(asset_url)

    def get_game_data(self, platform_game_id):
        summary = self.get_game_summary(platform_game_id)
        details = self.get_game_details(platform_game_id)
        return summary, details

    @staticmethod
    def _process_datetime(date):
        if not date:
            return date
        if isinstance(date, (int, float)):
            date = datetime.fromtimestamp(date, tz=pytz.UTC)
        if isinstance(date, datetime):
            if not date.tzinfo:
                date = date.replace(tzinfo=pytz.UTC)
            date = date.isoformat()
        return date

    def get_tags_list(self):
        return self.api.do_api_call("GET", "emh/v1/tags")

    def get_games_info(self, platform_game_ids: Union[str, list]):
        if isinstance(platform_game_ids, str):
            platform_game_ids = platform_game_ids.split(",")
        ret = {}
        for platform_game_id in platform_game_ids:
            try:
                resp = self.get_game_info(platform_game_id)
                ret[resp["platformGameId"]] = {"success": True, "payload": resp}
            except NotFoundError:
                ret[platform_game_id] = {"success": False}
        return ret

    def get_game_info(self, platform_game_id: str):
        return self.api.do_api_call("GET", f"emh/v1/games/{platform_game_id}")

    def get_game_list(
        self,
        *,
        tags: Optional[Union[str, list]] = None,
        from_timestamp: Optional[Union[datetime, int, float]] = None,
        to_timestamp: Optional[Union[datetime, int, float]] = None,
        page: Optional[int] = None,
        size: Optional[int] = None,
        team1: Optional[str] = None,
        team2: Optional[str] = None,
    ):
        if type(tags) == list:
            tags = ",".join(tags)
        from_timestamp, to_timestamp = self._process_datetime(
            from_timestamp
        ), self._process_datetime(to_timestamp)
        params = {
            "from": from_timestamp,
            "to": to_timestamp,
            "tags": tags,
            "page": page,
            "size": size,
            "team1": team1,
            "team2": team2,
        }
        return self.api.do_api_call("GET", "emh/v1/games", params)
