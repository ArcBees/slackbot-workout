import json
import os

USER_TOKEN_STRING = os.environ['SLACK_USER_TOKEN_STRING']
URL_TOKEN_STRING = os.environ['SLACK_URL_TOKEN_STRING']

HASH = "%23"


class Settings:
    def __init__(self):
        self.settings = {}
        self.reload()

    def reload(self):
        with open('config.json') as f:
            self.settings = json.load(f)

    @property
    def post_url(self):
        return "https://" + self.team_domain() + ".slack.com/services/hooks/slackbot?token=" + URL_TOKEN_STRING \
               + "&channel=" + HASH + self.channel_name()

    @property
    def is_debug(self):
        return self.settings["debug"]

    @property
    def team_domain(self):
        return self.settings["teamDomain"]

    @property
    def channel_name(self):
        return self.settings["channelName"]

    @property
    def channel_id(self):
        return self.settings["channelId"]

    @property
    def weekdays(self):
        return sorted(self.settings["days"])

    @property
    def hours(self):
        return sorted(self.settings["hours"], key=lambda hour_range: hour_range[0])

    @property
    def callout_min_time(self):
        return self.settings["callouts"]["timeBetween"]["minTime"]

    @property
    def callout_max_time(self):
        return self.settings["callouts"]["timeBetween"]["maxTime"]

    @property
    def callout_size(self):
        return self.settings["callouts"]["numPeople"]

    @property
    def group_callout_chance(self):
        return self.settings["callouts"]["groupCalloutChance"]

    @property
    def exercises(self):
        return self.settings["exercises"]
