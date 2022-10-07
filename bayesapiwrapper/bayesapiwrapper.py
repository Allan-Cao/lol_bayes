import requests
import json
from datetime import datetime, timedelta
import os
from typing import Optional, Union
import pytz


class BayesApiWrapper(object):
    config_path = os.path.join(os.path.expanduser('~'), '.config', 'bayesapiwrapper')
    tokens_file = os.path.join(config_path, "tokens.json")
    credentials_file = os.path.join(config_path, "credentials.json")
    endpoint = "https://lolesports-api.bayesesports.com/"

    def __init__(self):
        self.tokens = None
        self.credentials = None

    def _load_credentials(self):
        if not os.path.isfile(self.credentials_file):
            print("The credentials file does not exist yet, let's create it")
            email = input("Bayes username: ")
            password = input("Bayes password: ")
            with open(file=self.credentials_file, mode="w+", encoding="utf8") as f:
                json.dump({"username": email, "password": password}, f, ensure_ascii=False)
        with open(file=self.credentials_file, mode="r+", encoding="utf8") as f:
            self.credentials = json.load(f)

    def _load_tokens(self):
        if not os.path.exists(self.config_path):
            os.makedirs(self.config_path)
        if not os.path.isfile(self.tokens_file):
            with open(file=self.tokens_file, mode="w+", encoding="utf8") as f:
                json.dump({}, f, ensure_ascii=False)
        with open(file=self.tokens_file, mode="r+", encoding="utf8") as f:
            self.tokens = json.load(f)

    def _store_tokens(self, data):
        self.tokens = {"accessToken": data["accessToken"],
                       "refreshToken": data["refreshToken"],
                       "expires": datetime.now().timestamp() + data["expiresIn"]}
        with open(file=self.tokens_file, mode="w+", encoding="utf8") as f:
            json.dump(self.tokens, f, ensure_ascii=False)

    def _should_refresh(self):
        expires = datetime.fromtimestamp(self.tokens["expires"])
        if expires - datetime.now() <= timedelta(minutes=5):
            return True
        return False

    def _ensure_login(self):
        if self.tokens is None:
            self._load_tokens()
        if "accessToken" not in self.tokens:
            self._do_login()
        if self._should_refresh():
            data = self._do_api_call("POST", "auth/refresh", {"refreshToken": self.tokens["refreshToken"]},
                                     ensure_login=False)
            self._store_tokens(data)

    def _do_login(self):
        self._load_credentials()
        data = self._do_api_call("POST", "auth/login", {"username": self.credentials["username"],
                                                        "password": self.credentials["password"]},
                                 ensure_login=False)
        self._store_tokens(data)

    def get_game_summary(self, game_rpgid):
        summary = self.get_game_asset(game_rpgid, "GAMH_SUMMARY")
        return summary.json()

    def get_game_details(self, game_rpgid):
        details = self.get_game_asset(game_rpgid, "GAMH_DETAILS")
        return details.json()

    def get_game_asset(self, game_rpgid, asset_name):
        asset_url = self._do_api_call(f"GET", f"emh/v1/games/{game_rpgid}/download", data={"type": asset_name})["url"]
        return requests.get(asset_url)

    def get_game(self, game_rpgid):
        summary = self.get_game_summary(game_rpgid)
        details = self.get_game_details(game_rpgid)
        return summary, details

    @staticmethod
    def _process_datetime(date):
        if not date:
            return date
        if isinstance(date, int or float):
            date = datetime.fromtimestamp(date, tz=pytz.UTC)
        if isinstance(date, datetime):
            if not date.tzinfo:
                date = date.replace(tzinfo=pytz.UTC)
            date = date.isoformat()
        return date

    def get_game_list(self, *, tags: Optional[Union[str, list]] = None,
                      from_timestamp: Optional[Union[datetime, str, int, float]] = None,
                      to_timestamp: Optional[Union[datetime, str, int, float]] = None, page: Optional[int] = None,
                      size: Optional[int] = None, team1: Optional[str] = None, team2: Optional[str] = None):
        if type(tags) == list:
            tags = ",".join(tags)
        from_timestamp, to_timestamp = self._process_datetime(from_timestamp), self._process_datetime(to_timestamp)
        params = {"from": from_timestamp, "to": to_timestamp, "tags": tags, "page": page,
                  "size": size, "team1": team1, "team2": team2}
        game_list = self._do_api_call("GET", "emh/v1/games", params)
        return game_list

    def _get_headers(self):
        return {"Authorization": f"Bearer {self.tokens['accessToken']}"}

    def _do_api_call(self, method, service, data=None, *, allow_retry: bool = True, ensure_login: bool = True):
        if ensure_login:
            self._ensure_login()
        if method == "GET":
            response = requests.get(self.endpoint + service, headers=self._get_headers(), params=data)
        elif method == "POST":
            response = requests.post(self.endpoint + service, json=data)
        else:
            raise ValueError("HTTP Method must be GET or POST.")
        if response.status_code == 401 and allow_retry:
            return self._do_api_call(method, service, data, allow_retry=False)
        if response.status_code != 200:
            response.raise_for_status()
        return response.json()
