import json
import random

import requests

from settings import USER_TOKEN_STRING
from user import User


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
