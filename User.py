import json

import requests

from settings import USER_TOKEN_STRING


class User:
    def __init__(self, user_id):
        self.id = user_id
        self.username, self.real_name = self.fetch_names()

    def fetch_names(self):
        params = {"token": USER_TOKEN_STRING, "user": self.id}
        response = requests.get("https://slack.com/api/users.info", params=params)
        user = json.loads(response.text, encoding='utf-8')["user"]

        return user["name"], user["profile"]["real_name"]

    @property
    def handle(self):
        return "@" + self.username
