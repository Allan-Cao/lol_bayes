import requests
import json
from datetime import datetime, timedelta
import os


class NotFoundError(Exception):
    pass


class BayesApiWrapper(object):
    config_path = os.path.join(os.path.expanduser('~'), '.config', 'bayesapiwrapper')
    tokens_file = os.path.join(config_path, "tokens.json")
    credentials_file = os.path.join(config_path, "credentials.json")

    def __init__(self):
        self.tokens = None
        self.credentials = None

    def load_credentials(self):
        with open(file=self.credentials_file, mode="r+", encoding="utf8") as f:
            self.credentials = json.load(f)

    def load_tokens(self):
        if not os.path.exists(self.config_path):
            os.makedirs(self.config_path)
            with open(file=self.tokens_file, mode="w+", encoding="utf8") as f:
                json.dump({}, f, ensure_ascii=False)
            email = input("Bayes email: ")
            password = input("Bayes password: ")
            with open(file=self.credentials_file, mode="w+", encoding="utf8") as f:
                json.dump({"username": email, "password": password}, f, ensure_ascii=False)
        with open(file=self.tokens_file, mode="r+", encoding="utf8") as f:
            self.tokens = json.load(f)

    def save_tokens(self):
        with open(file=self.tokens_file, mode="w+", encoding="utf8") as f:
            json.dump(self.tokens, f, ensure_ascii=False)

    def get_game(self, game_rpgid):
        self.ensure_login()
        data_url = self.do_api_call("GET", f"api/v1/games/{game_rpgid}/download?type=GAMH_SUMMARY")["url"]
        timeline_url = self.do_api_call("GET", f"api/v1/games/{game_rpgid}/download?type=GAMH_DETAILS")["url"]
        data = requests.get(data_url).json()
        timeline = requests.get(timeline_url).json()
        return data, timeline

    def should_refresh(self):
        expires = datetime.fromtimestamp(self.tokens["expires"])
        if expires - datetime.now() <= timedelta(minutes=5):
            return True
        return False

    def ensure_login(self):
        self.load_tokens()
        if "accessToken" not in self.tokens:
            self.do_login()
        if self.should_refresh():
            data = self.do_api_call("POST", "login/refresh_token", {"refreshToken": self.tokens["refreshToken"]})
            self.tokens = {"accessToken": data["accessToken"], "refreshToken": data["refreshToken"],
                           "expires": datetime.now().timestamp() + data["expiresIn"]}
            self.save_tokens()

    def do_login(self):
        self.load_credentials()
        data = self.do_api_call("POST", "login", {"username": self.credentials["username"],
                                                  "password": self.credentials["password"]})
        print(data)
        self.tokens = {"accessToken": data["accessToken"], "refreshToken": data["refreshToken"],
                       "expires": datetime.now().timestamp() + data["expiresIn"]}
        self.save_tokens()

    def get_headers(self):
        if not self.tokens.get("accessToken"):
            raise Exception("accessToken can't be found.")
        return {"Authorization": f"Bearer {self.tokens['accessToken']}"}

    def do_api_call(self, method, service, data=None):
        endpoint = "https://emh-api.bayesesports.com/"

        if method == "GET":
            response = requests.get(endpoint + service, headers=self.get_headers(), params=data)
        elif method == "POST":
            response = requests.post(endpoint + service, json=data)
        else:
            raise ValueError("HTTP Method must be GET or POST.")
        if response.status_code == 429:
            raise Exception("Bayes Ratelimit! Please try again later")
        elif response.status_code == 404:
            raise NotFoundError()
        return response.json()


if __name__ == "__main__":
    print(BayesApiWrapper().get_game("ESPORTSTMNT06_2570477"))
