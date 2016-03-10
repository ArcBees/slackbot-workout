#!/usr/bin/env python3

import random
import time
from datetime import datetime, timedelta

import requests
import locale

from callout import CallOut
from datetimerangecollection import DateTimeRangeCollection
from exercisecollection import ExerciseCollection
from settings import Settings
from user import UserCollection


class Bot:
    def __init__(self):
        self.settings = Settings()
        self.users = UserCollection(self.settings)
        self.exercises = ExerciseCollection(self.settings)
        self.date_time_ranges = DateTimeRangeCollection(self.settings)

    def run(self):
        self.call_out_if_in_range()

        while True:
            self.wait()
            self.reload()
            self.call_out()

    def reload(self):
        self.settings.reload()
        self.users.reload()

    def wait(self):
        wait_seconds = int(self.date_time_ranges.draw_seconds())
        today = datetime.today()
        next_draw = today + timedelta(seconds=wait_seconds)

        locale.setlocale(locale.LC_ALL, 'fr_CA.utf8')

        message = "LA PROCHAINE LOTERIE EST"
        if next_draw.day != today.day:
            message += " LE " + next_draw.strftime("%A, %b %d")
        message += " À " + next_draw.strftime("%H:%M")

        print(message)
        if not self.settings.is_debug:
            requests.post(self.settings.post_url, data=message)
            time.sleep(wait_seconds)
        else:
            time.sleep(5)

    def call_out_if_in_range(self):
        today = datetime.today()
        start, stop = self.date_time_ranges.next_range_today()

        if start <= today <= stop:
            self.call_out()

    def call_out(self):
        exercise = self.exercises.draw()
        reps = random.randrange(exercise["minReps"], exercise["maxReps"] + 1)
        # TODO: Don't convert to handle here; but need a special "ChannelUser"
        if random.random() < self.settings.group_callout_chance:
            winner_handles = ["@channel"]
        else:
            winner_handles = [user.handle for user in self.users.draw()]

        CallOut(self.settings, exercise, reps, winner_handles).publish()
