from bayes_lol_client import BayesAPIClient
from bayes_lol_client import utils
from requests import Response
from typing import Union, List
from datetime import datetime
from bayes_lol_client.errors import NotFoundError


class BayesHistoric(object):
    endpoint = "https://lolesports-api.bayesesports.com/historic/v1/riot-lol/"
    DEFAULT_MAX_PAGE_SIZE = 500

    def __init__(
        self,
        username: str = None,
        password: str = None,
        wait_on_ratelimit: bool = True,
        retry_interval: int = 2,
        max_retries: int = 5,
    ):
        self.api = BayesAPIClient(
            endpoint=self.endpoint,
            username=username,
            password=password,
            wait_on_ratelimit=wait_on_ratelimit,
            retry_interval=retry_interval,
            max_retries=max_retries,
        )

    def get_asset(self, service: str):
        asset_url = self.api.do_api_call(
            "GET",
            service,
        )["url"]
        return utils.download_game_asset(self.api, asset_url)

    def get_game_data(self, game_id: Union[str, int]) -> Response.content:
        return self.get_asset(f"games/{game_id}/download").content

    def get_game_data_dump(self, game_id: Union[str, int]) -> dict:
        return self.get_asset(f"games/{game_id}/downloadDump").json()

    def get_matches_info(self, match_ids: Union[str, List[Union[int, str]]]) -> dict:
        if isinstance(match_ids, str):
            match_ids = match_ids.split(",")
        ret = {}
        for match_id in match_ids:
            try:
                resp = self.get_match_info(match_id)
                ret[match_id] = {"success": True, "payload": resp}
            except NotFoundError:
                ret[match_id] = {"success": False}
        return ret

    def get_match_info(self, match_id: Union[int, str]) -> dict:
        return self.api.do_api_call("GET", f"matches/{match_id}")

    def get_matches_list(
        self,
        *,
        match_or_game_id: Union[str, int] = None,
        team_ids: Union[str, int, List[int]] = None,
        league_ids: Union[str, int, List[int]] = None,
        date_from: Union[datetime, int, float] = None,
        date_to: Union[datetime, int, float] = None,
        limit: int = None,
        max_page_size: int = None,
    ) -> list:
        if max_page_size is None:
            if limit is not None and self.DEFAULT_MAX_PAGE_SIZE >= limit:
                max_page_size = limit
            else:
                max_page_size = self.DEFAULT_MAX_PAGE_SIZE

        params = {
            "matchOrGameId": match_or_game_id and int(match_or_game_id) or None,
            "teamIds": utils.join_if_needed(team_ids),
            "leagueIds": utils.join_if_needed(league_ids),
            "matchDateFrom": utils.process_datetime(date_from),
            "matchDateTo": utils.process_datetime(date_to),
            "page": 0,
            "size": max_page_size,
        }
        return utils.get_list(self.api, params, "matches", limit, "results")

    def get_teams_list(self) -> list:
        return self.api.do_api_call("GET", "teams")

    def get_tournaments_list(self, league_ids: Union[List[int], str, int]) -> list:
        return self.api.do_api_call(
            "GET", "tournaments", data={"leagueIds": utils.join_if_needed(league_ids)}
        )

    def get_tournaments_info(self, tournament_ids: Union[str, List[Union[int, str]]]) -> dict:
        if isinstance(tournament_ids, str):
            tournament_ids = tournament_ids.split(",")
        ret = {}
        for tournament_id in tournament_ids:
            try:
                resp = self.get_match_info(tournament_id)
                ret[tournament_id] = {"success": True, "payload": resp}
            except NotFoundError:
                ret[tournament_id] = {"success": False}
        return ret

    def get_tournament_info(self, tournament_id: Union[str, int]) -> dict:
        return self.api.do_api_call("GET", f"tournaments/{tournament_id}")

    def get_tournament_matches_list(self, tournament_id: Union[str, int]) -> list:
        return self.api.do_api_call("GET", f"tournaments/{tournament_id}/matches")

    def get_user_leagues_list(self) -> list:
        return self.api.do_api_call("GET", f"leagues")

    def get_leagues_info(self, league_ids: Union[str, List[Union[int, str]]]) -> dict:
        if isinstance(league_ids, str):
            league_ids = league_ids.split(",")
        ret = {}
        for league_id in league_ids:
            try:
                resp = self.get_match_info(league_id)
                ret[league_id] = {"success": True, "payload": resp}
            except NotFoundError:
                ret[league_id] = {"success": False}
        return ret

    def get_league_info(self, league_id: Union[str, int]) -> dict:
        return self.api.do_api_call("GET", f"leagues/{league_id}")

    def get_league_tournaments_list(self, league_id: Union[str, int]) -> list:
        return self.api.do_api_call("GET", f"leagues/{league_id}/tournaments")
