import requests
from requests.exceptions import (
    JSONDecodeError,
    ConnectionError,
    ConnectTimeout,
    Timeout,
    ReadTimeout,
)
import json
from datetime import datetime, timedelta
import os
import backoff
from bayes_lol_client.errors import (
    ClientError,
    ServerError,
    NotFoundError,
    TooManyRequests,
    UnauthorizedError,
)


class BayesAPIClient(object):
    config_path = os.path.join(os.path.expanduser("~"), ".config", "bayes_lol_client")
    tokens_file = os.path.join(config_path, "tokens.json")
    credentials_file = os.path.join(config_path, "credentials.json")

    def __init__(self, endpoint, username=None, password=None):
        self.tokens = None
        self.credentials = {"username": username, "password": password}
        self.endpoint = endpoint
        self._ensure_config_directory_exists()

    def _ensure_config_directory_exists(self):
        if not os.path.exists(self.config_path):
            os.makedirs(self.config_path)

    @staticmethod
    def _create_config_file(file, content=None):
        with open(file=file, mode="w+", encoding="utf8") as f:
            json.dump(content or {}, f, ensure_ascii=False)

    def load_all(self):
        self.load_credentials()
        self.load_tokens()

    @staticmethod
    def _prompt_credentials():
        print("You haven't set your credentials for Bayes yet, we will create them now")
        username = input("Bayes username: ")
        password = input("Bayes password: ")
        return {"username": username, "password": password}

    def load_credentials(self):
        if self.credentials["username"] and self.credentials["password"]:
            return
        if not os.path.isfile(self.credentials_file):
            self._create_config_file(self.credentials_file, self._prompt_credentials())
        with open(file=self.credentials_file, mode="r+", encoding="utf8") as f:
            self.credentials = json.load(f)

    def load_tokens(self):
        if not os.path.isfile(self.tokens_file):
            self._create_config_file(self.tokens_file)
        with open(file=self.tokens_file, mode="r+", encoding="utf8") as f:
            self.tokens = json.load(f)

    def store_tokens(self, data):
        self.tokens = {
            "access_token": data["accessToken"],
            "refresh_token": data["refreshToken"],
            "expires": datetime.now().timestamp() + data["expiresIn"],
        }
        with open(file=self.tokens_file, mode="w+", encoding="utf8") as f:
            json.dump(self.tokens, f, ensure_ascii=False)

    def should_refresh(self):
        expires = datetime.fromtimestamp(self.tokens["expires"])
        if expires - datetime.now() <= timedelta(minutes=5):
            return True
        return False

    def ensure_login(self):
        if self.tokens is None:
            self.load_tokens()
        if "access_token" not in self.tokens:
            self.do_login()
        if self.should_refresh():
            self.refresh_token()

    def refresh_token(self):
        try:
            if self.tokens is None:
                self.load_tokens()
            data = self.do_api_call(
                "POST",
                "auth/refresh",
                {"refreshToken": self.tokens["refresh_token"]},
                ensure_login=False,
                allow_retry=False,
            )
            self.store_tokens(data)
        except UnauthorizedError:
            self.do_login()

    def do_login(self):
        self.load_credentials()
        data = self.do_api_call(
            "POST",
            "auth/login",
            {
                "username": self.credentials["username"],
                "password": self.credentials["password"],
            },
            ensure_login=False,
            allow_retry=False,
        )
        self.store_tokens(data)

    def _get_headers(self):
        if not self.tokens:
            self.load_tokens()
        return {"Authorization": f"Bearer {self.tokens['access_token']}"}

    @backoff.on_exception(
        backoff.expo,
        (
            JSONDecodeError,
            ConnectionError,
            ConnectTimeout,
            Timeout,
            ReadTimeout,
            TooManyRequests,
        ),
        max_time=60,
    )
    def do_api_call(
        self,
        method,
        service,
        data=None,
        *,
        allow_retry: bool = True,
        ensure_login: bool = True,
    ):
        if ensure_login:
            self.ensure_login()
        if method == "GET":
            response = requests.get(
                self.endpoint + service, headers=self._get_headers(), params=data
            )
        elif method == "POST":
            response = requests.post(self.endpoint + service, json=data)
        else:
            raise ValueError("HTTP Method must be GET or POST.")

        if response.status_code == 401:
            if allow_retry:
                return self.do_api_call(method, service, data, allow_retry=False)
            raise UnauthorizedError(response.status_code)
        elif response.status_code == 429:
            raise TooManyRequests(response.status_code)
        elif response.status_code == 404:
            raise NotFoundError(response.status_code)
        elif response.status_code >= 500:
            if allow_retry:
                return self.do_api_call(method, service, data, allow_retry=False)
            raise ServerError(response.status_code)
        elif 499 >= response.status_code >= 400:
            raise ClientError(response.status_code)
        response.raise_for_status()
        return response.json()
