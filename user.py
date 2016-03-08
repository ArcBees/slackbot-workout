import json
import random

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


class UserCollection:
    def __init__(self, settings):
        self.settings = settings
        self.users = []
        self.reload()

    def reload(self):
        params = {"token": USER_TOKEN_STRING, "channel": self.settings.channel_id}
        response = requests.get("https://slack.com/api/channels.info", params=params)
        user_ids = json.loads(response.text, encoding='utf-8')["channel"]["members"]

        self.users = []

        for user_id in user_ids:
            self.users.append(User(user_id))

    def draw(self):
        draw_size = min(len(self.users), self.settings.callout_size)

        return random.sample(self.users, draw_size)
