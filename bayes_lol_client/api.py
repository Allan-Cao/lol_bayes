import requests
from requests.exceptions import (
    JSONDecodeError,
    ConnectionError,
    ConnectTimeout,
    Timeout,
    ReadTimeout,
    HTTPError,
)
import json
from datetime import datetime, timedelta
import os
from bayes_lol_client.sleep import Sleepers, Sleeper
from typing import NoReturn, Any
from bayes_lol_client.errors import (
    ClientError,
    ServerError,
    NotFoundError,
    TooManyRequests,
    UnauthorizedError,
)


class BayesAPIClient(object):
    config_path = os.path.join(os.path.expanduser("~"), ".config", "bayes_lol_client")
    credentials_file = os.path.join(config_path, "credentials.json")
    auth_endpoint = "https://lolesports-api.bayesesports.com/auth/"

    def __init__(
        self,
        endpoint,
        max_retries: int,
        retry_interval: int,
        username: str = None,
        password: str = None,
        wait_on_ratelimit: bool = True,
    ):
        self.user_tokens = None
        self.credentials = {"username": username, "password": password}
        self.endpoint = endpoint
        self.wait_on_ratelimit = wait_on_ratelimit
        self.sleepers = Sleepers(max_retries=max_retries, retry_interval=retry_interval)
        self._ensure_config_directory_exists()
        self.load_all()

    def _ensure_config_directory_exists(self) -> NoReturn:
        if not os.path.exists(self.config_path):
            os.makedirs(self.config_path)

    @staticmethod
    def _create_config_file(file: str, content=None) -> NoReturn:
        with open(file=file, mode="w+", encoding="utf8") as f:
            json.dump(content or {}, f, ensure_ascii=False)

    def load_all(self) -> NoReturn:
        self.load_credentials()
        self.load_user_tokens()

    @staticmethod
    def _prompt_credentials() -> dict:
        print("You haven't set your credentials for Bayes yet, we will create them now")
        username = input("Bayes username: ")
        password = input("Bayes password: ")
        return {"username": username, "password": password}

    def load_credentials(self) -> NoReturn:
        if self.credentials["username"] and self.credentials["password"]:
            return
        if not os.path.isfile(self.credentials_file):
            self._create_config_file(self.credentials_file, self._prompt_credentials())
        with open(file=self.credentials_file, mode="r+", encoding="utf8") as f:
            self.credentials = json.load(f)

    def get_user_tokens_file(self) -> str:
        username = self.credentials["username"]
        return os.path.join(self.config_path, f"{username}_tokens.json")

    def load_user_tokens(self) -> NoReturn:
        user_tokens_file = self.get_user_tokens_file()
        if not os.path.isfile(user_tokens_file):
            self._create_config_file(user_tokens_file)
        with open(file=user_tokens_file, mode="r+", encoding="utf8") as f:
            self.user_tokens = json.load(f)

    def store_tokens(self, data: dict) -> NoReturn:
        user_tokens_file = self.get_user_tokens_file()
        if not os.path.isfile(user_tokens_file):
            self._create_config_file(user_tokens_file)
        self.user_tokens = {
            "access_token": data["accessToken"],
            "refresh_token": data["refreshToken"],
            "expires": datetime.now().timestamp() + data["expiresIn"],
        }
        with open(file=user_tokens_file, mode="w+", encoding="utf8") as f:
            json.dump(self.user_tokens, f, ensure_ascii=False)

    def should_refresh(self) -> bool:
        expires = datetime.fromtimestamp(self.user_tokens["expires"])
        return expires - datetime.now() <= timedelta(minutes=5)

    def ensure_login(self) -> NoReturn:
        if "access_token" not in self.user_tokens:
            self.do_login()
        if self.should_refresh():
            self.refresh_token()

    def refresh_token(self) -> NoReturn:
        try:
            data = self.do_api_call(
                "POST",
                "refresh",
                {"refreshToken": self.user_tokens["refresh_token"]},
                ensure_login=False,
                allow_retry=False,
                endpoint=self.auth_endpoint,
            )
            self.store_tokens(data)
        except UnauthorizedError:
            self.do_login()

    def do_login(self) -> NoReturn:
        data = self.do_api_call(
            "POST",
            "login",
            {
                "username": self.credentials["username"],
                "password": self.credentials["password"],
            },
            ensure_login=False,
            endpoint=self.auth_endpoint,
        )
        self.store_tokens(data)

    def _get_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.user_tokens['access_token']}"}

    @staticmethod
    def make_http_exception_from_status_code(response: requests.Response):
        return HTTPError(
            f"{response.status_code} for url {response.url}", response=response
        )

    def sleep_and_retry(
        self,
        sleeper: Sleeper,
        method: str,
        service: str,
        endpoint: str,
        data: dict = None,
        exception: Exception = None,
        sleep_time: int = None,
    ):
        sleeper.sleep(exception, sleep_time)
        return self.do_api_call(
            method,
            service,
            data,
            ensure_login=False,
            sleeper=sleeper,
            endpoint=endpoint,
        )

    # TODO: I think this should be in utils so we can use it when downloading game assets as well
    def handle_response(
        self,
        sleeper: Sleeper,
        response: requests.Response,
        method: str,
        service: str,
        allow_retry: bool,
        endpoint: str,
        data: dict = None,
    ):
        if response.status_code == 401:
            raise UnauthorizedError(response.status_code)
        elif response.status_code == 429:
            if not allow_retry or not self.wait_on_ratelimit:
                raise TooManyRequests(response.status_code)
            if "x-rate-limit-retry-after-seconds" in response.headers:
                sleep_time = int(response.headers["x-rate-limit-retry-after-seconds"])
            else:
                sleep_time = None
            return self.sleep_and_retry(
                method=method,
                sleeper=sleeper,
                service=service,
                data=data,
                exception=self.make_http_exception_from_status_code(response),
                sleep_time=sleep_time,
                endpoint=endpoint,
            )
        elif response.status_code == 404:
            raise NotFoundError(response.status_code)
        elif response.status_code >= 500:
            if not allow_retry:
                raise ServerError(response.status_code)
            return self.sleep_and_retry(
                method=method,
                sleeper=sleeper,
                service=service,
                data=data,
                exception=self.make_http_exception_from_status_code(response),
                endpoint=endpoint,
            )
        elif 499 >= response.status_code >= 400:
            raise ClientError(response.status_code)
        response.raise_for_status()
        return response.json()

    def do_api_call(
        self,
        method: str,
        service: str,
        data: dict = None,
        *,
        allow_retry: bool = True,
        ensure_login: bool = True,
        sleeper: Sleeper = None,
        endpoint: str = None,
    ) -> Any:
        if not sleeper:
            sleeper = self.sleepers.make()
        if ensure_login:
            self.ensure_login()
        endpoint = endpoint or self.endpoint
        url = endpoint + service
        try:
            if method == "GET":
                response = requests.get(url, headers=self._get_headers(), params=data)
            elif method == "POST":
                response = requests.post(url, json=data)
            else:
                raise ValueError("HTTP Method must be GET or POST.")
        except (
            JSONDecodeError,
            ConnectionError,
            ConnectTimeout,
            Timeout,
            ReadTimeout,
        ) as e:
            if not allow_retry:
                raise e
            return self.sleep_and_retry(
                method=method,
                sleeper=sleeper,
                service=service,
                data=data,
                exception=e,
                endpoint=endpoint,
            )

        return self.handle_response(
            method=method,
            service=service,
            data=data,
            sleeper=sleeper,
            response=response,
            allow_retry=allow_retry,
            endpoint=endpoint,
        )
