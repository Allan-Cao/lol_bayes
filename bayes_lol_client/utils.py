from requests.exceptions import (
    JSONDecodeError,
    ConnectionError,
    ConnectTimeout,
    Timeout,
    ReadTimeout,
    HTTPError,
)
import requests
from requests import Response
from bayes_lol_client.sleep import Sleeper
from bayes_lol_client import BayesAPIClient
from typing import Union
from datetime import datetime
import pytz


def download_game_asset(
    api: BayesAPIClient, asset_url: str, sleeper: Sleeper = None
) -> Response:
    if not sleeper:
        sleeper = api.sleepers.make()
    try:
        response = requests.get(asset_url)
        response.raise_for_status()
    except (
        JSONDecodeError,
        ConnectionError,
        ConnectTimeout,
        Timeout,
        ReadTimeout,
        HTTPError,
    ) as e:
        sleeper.sleep(exception=e)
        return download_game_asset(api=api, asset_url=asset_url, sleeper=sleeper)
    return response


def get_list(
    api: BayesAPIClient, params: dict, service: str, limit: int, key: str
) -> list:
    ret = []
    while True:
        if limit and limit <= len(ret):
            break
        response = api.do_api_call("GET", service, params)
        ret.extend(response[key])
        if limit and response["count"] <= limit:
            break
        if len(ret) == response["count"]:
            break
        params["page"] += 1
    return ret[:limit]


def join_if_needed(_list):
    if not isinstance(_list, list):
        return _list
    return ",".join(_list)


def process_datetime(date: Union[datetime, int, float, None]) -> Union[str, None]:
    if date is None:
        return date
    if isinstance(date, (int, float)):
        date = datetime.fromtimestamp(date, tz=pytz.UTC)
    if not date.tzinfo:
        date = date.replace(tzinfo=pytz.UTC)
    date = date.isoformat()
    return date
