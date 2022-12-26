from bayes_lol_client import BayesAPIClient
from bayes_lol_client import utils
from bayes_lol_client.errors import NotFoundError
from typing import Optional, Union, List
from requests import Response
from datetime import datetime


class BayesEMH(object):
    """
    This class makes requests to the /emh/v1 endpoint in the Bayes API.
    Useful to get summary/details/replay files for professional games
    """
    endpoint = "https://lolesports-api.bayesesports.com/emh/v1/"
    DEFAULT_MAX_PAGE_SIZE = 500

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        wait_on_ratelimit: Optional[bool] = True,
        retry_interval: Optional[int] = 2,
        max_retries: Optional[int] = 5,
    ):
        self.api = BayesAPIClient(
            endpoint=self.endpoint,
            username=username,
            password=password,
            wait_on_ratelimit=wait_on_ratelimit,
            retry_interval=retry_interval,
            max_retries=max_retries,
        )

    def get_game_summary(self, platform_game_id: str) -> dict:
        """
        Returns the game summary as a json file

        :param platform_game_id: A Riot esports game ID
        :return: The game summary as a json file
        """
        return self.get_asset(platform_game_id, "GAMH_SUMMARY").json()

    def get_game_details(self, platform_game_id: str) -> dict:
        """
        Returns the game details (timeline) as a json file

        :param platform_game_id: A Riot esports game ID
        :return: The game details as a json file
        """
        return self.get_asset(platform_game_id, "GAMH_DETAILS").json()

    def get_game_replay(self, platform_game_id: str) -> bytes:
        """
        Returns a replay file as bytes which can later be saved locally

        :param platform_game_id: A Riot esports game ID
        :return: Replay file as bytes
        """
        return self.get_asset(platform_game_id, "ROFL_REPLAY").content

    def get_asset(self, platform_game_id: str, asset_name: str) -> Response:
        """
        Gets a generic asset for a game by its name (SUMMARY, DETAILS, or REPLAY)

        :param platform_game_id: A Riot esports game ID
        :param asset_name: The name of the asset to return (GAMH_SUMMARY, GAMH_DETAILS, ROFL_REPLAY)
        :return: An asset for a specific game
        """
        asset_url = self.api.do_api_call(
            "GET",
            f"games/{platform_game_id}/download",
            data={"type": asset_name},
        )["url"]
        return utils.download_game_asset(self.api, asset_url)

    def get_game_data(self, platform_game_id: str) -> tuple:
        """
        Returns both the game summary and details as a tuple

        :param platform_game_id: A Riot esports game ID
        :return: Game summary and details as a tuple
        """
        summary = self.get_game_summary(platform_game_id)
        details = self.get_game_details(platform_game_id)
        return summary, details

    def get_tags_list(self) -> List[str]:
        """
        Gets all the available game tags in EMH

        :return: A list of game tags
        """
        return self.api.do_api_call("GET", "tags")

    def get_games_info(self, platform_game_ids: Union[str, list]) -> dict:
        """
        Gets basic metadata for a list of games

        :param platform_game_ids: Riot esports game IDs as a list or a comma-separated string
        :return: A dict containing each platform game ID as a key
        """
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

    def get_game_info(self, platform_game_id: str) -> dict:
        """
        Gets basic metadata for a specific game

        :param platform_game_id: A riot esports game ID
        :return: Metadata for a game as a dict
        """
        return self.api.do_api_call("GET", f"games/{platform_game_id}")

    def get_games_list(
        self,
        *,
        tags: Optional[Union[str, List[str]]] = None,
        from_timestamp: Optional[Union[datetime, int, float]] = None,
        to_timestamp: Optional[Union[datetime, int, float]] = None,
        limit: Optional[int] = None,
        team1: Optional[str] = None,
        team2: Optional[str] = None,
        max_page_size: Optional[int] = None,
    ) -> list:
        """
        Gets a list of games which can be filtered using the different function arguments
        If no limit is specified, the function will make multiple requests and return every matched game

        :param tags: Only return games containing these tags, as a comma-separated string, or a list
        :param from_timestamp: Only return games after this moment, can be a unix epoch timestamp as int or float, or a datetime object
        :param to_timestamp: Only return games before this moment, can be a unix epoch timestamp as int or float, or a datetime object
        :param limit: Maximum number of games to return
        :param team1: Only return games where this team played, this should be the team tricode
        :param team2: Only return games where this team and team1 played, this should be the team tricode
        :param max_page_size: Maximum size for each request, this is only useful for tweaking performance
        :return: A dict of games with the ID as a key and metadata for each one
        """
        if max_page_size is None:
            if limit is not None and self.DEFAULT_MAX_PAGE_SIZE >= limit:
                max_page_size = limit
            else:
                max_page_size = self.DEFAULT_MAX_PAGE_SIZE
        params = {
            "from": utils.process_datetime(from_timestamp),
            "to": utils.process_datetime(to_timestamp),
            "tags": utils.join_if_needed(tags),
            "page": 0,
            "size": max_page_size,
            "team1": team1,
            "team2": team2,
        }
        return utils.get_list(self.api, params, "games", limit, "games")
