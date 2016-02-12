import random
import time
import requests
import json
import csv
import os
import pickle
import os.path
import datetime

from User import User

# Environment variables must be set with your tokens
USER_TOKEN_STRING = os.environ['SLACK_USER_TOKEN_STRING']
URL_TOKEN_STRING = os.environ['SLACK_URL_TOKEN_STRING']

HASH = "%23"


# Configuration values to be set in setConfiguration
class Bot:
    def __init__(self):
        self.load_configuration()

        self.csv_filename = "log" + time.strftime("%Y%m%d-%H%M") + ".csv"

        # local cache of usernames
        # maps userIds to usernames
        self.user_cache = self.load_user_cache()

    def load_user_cache(self):
        if os.path.isfile('user_cache.save'):
            with open('user_cache.save', 'rb') as f:
                self.user_cache = pickle.load(f)
                print("Loading " + str(len(self.user_cache)) + " users from cache.")
                return self.user_cache

        return {}

    '''
    Sets the configuration file.

    Runs after every callout so that settings can be changed realtime
    '''

    def load_configuration(self):
        # Read variables fromt the configuration file
        with open('config.json') as f:
            settings = json.load(f)

            self.team_domain = settings["teamDomain"]
            self.channel_name = settings["channelName"]
            self.min_countdown = settings["callouts"]["timeBetween"]["minTime"]
            self.max_countdown = settings["callouts"]["timeBetween"]["maxTime"]
            self.num_people_per_callout = settings["callouts"]["numPeople"]
            self.group_callout_chance = settings["callouts"]["groupCalloutChance"]
            self.channel_id = settings["channelId"]
            self.exercises = settings["exercises"]
            self.hours = settings["hours"]
            self.days = settings["days"]

            self.debug = settings["debug"]

        self.post_URL = "https://" + self.team_domain + ".slack.com/services/hooks/slackbot?token=" + URL_TOKEN_STRING + "&channel=" + HASH + self.channel_name


################################################################################


'''
Selects an exercise and start time, and sleeps until the time
period has past.
'''


def prepare_next_exercise(bot):
    next_time_interval = draw_next_time_interval(bot)
    minute_interval = next_time_interval / 60
    exercise = draw_exercise(bot)

    # Announcement String of next lottery time
    lottery_announcement = "NEXT LOTTERY FOR " + exercise["name"].upper() + " IS IN " + str(int(minute_interval)) \
                           + (" MINUTES" if minute_interval != 1 else " MINUTE")

    # Announce the exercise to the thread
    if not bot.debug:
        requests.post(bot.post_URL, data=lottery_announcement)
    print(lottery_announcement)

    # Sleep the script until time is up
    if not bot.debug:
        time.sleep(next_time_interval)
    else:
        # If debugging, once every 5 seconds
        time.sleep(5)

    return exercise


'''
Selects the next exercise
'''


def draw_exercise(bot):
    idx = random.randrange(0, len(bot.exercises))
    return bot.exercises[idx]


'''
Selects the next time interval
'''


def draw_next_time_interval(bot):
    return random.randrange(bot.min_countdown * 60, bot.max_countdown * 60)


'''
Selects a person to do the already-selected exercise
'''


def assign_exercise(bot, exercise):
    # Select number of reps
    exercise_reps = random.randrange(exercise["minReps"], exercise["maxReps"] + 1)

    winner_announcement = str(exercise_reps) + " " + str(exercise["units"]) + " " + exercise["name"] + " RIGHT NOW "

    # EVERYBODY
    if random.random() < bot.group_callout_chance:
        winner_announcement += "@channel!"

        for user_id in bot.user_cache:
            user = bot.user_cache[user_id]
            user.add_exercise(exercise, exercise_reps)

        log_exercise(bot, "@channel", exercise["name"], exercise_reps, exercise["units"])

    else:
        winners = draw_users(bot)

        for i in range(bot.num_people_per_callout):
            winner_announcement += str(winners[i].get_user_handle())
            if i == bot.num_people_per_callout - 2:
                winner_announcement += ", and "
            elif i == bot.num_people_per_callout - 1:
                winner_announcement += "!"
            else:
                winner_announcement += ", "

            winners[i].add_exercise(exercise, exercise_reps)
            log_exercise(bot, winners[i].get_user_handle(), exercise["name"], exercise_reps, exercise["units"])

    # Announce the user
    if not bot.debug:
        requests.post(bot.post_URL, data=winner_announcement)
    print(winner_announcement)


'''
Selects an active user from a list of users
'''


def draw_users(bot):
    users = fetch_users(bot)
    draw_size = min(len(users), bot.num_people_per_callout)

    return random.sample(users, draw_size)


'''
Fetches a list of all users in the channel
'''


def fetch_users(bot):
    # Check for new members
    params = {"token": USER_TOKEN_STRING, "channel": bot.channel_id}
    response = requests.get("https://slack.com/api/channels.info", params=params)
    user_ids = json.loads(response.text, encoding='utf-8')["channel"]["members"]

    users = []

    for user_id in user_ids:
        # Add user to the cache if not already
        if user_id not in bot.user_cache:
            bot.user_cache[user_id] = User(user_id)

        users.append(bot.user_cache[user_id])

    return users


def log_exercise(bot, username, exercise, reps, units):
    filename = bot.csv_filename + "_DEBUG" if bot.debug else bot.csv_filename
    with open(filename, 'a') as f:
        writer = csv.writer(f)
        writer.writerow([str(datetime.datetime.now()), username, exercise, reps, units, bot.debug])


def save_users(bot):
    # Write to the command console today's breakdown
    s = "```\n"
    # s += "Username\tAssigned\tComplete\tPercent
    s += "Username".ljust(15)
    for exercise in bot.exercises:
        s += exercise["name"] + "  "
    s += "\n---------------------------------------------------------------\n"

    for user_id in bot.user_cache:
        user = bot.user_cache[user_id]
        s += user.username.ljust(15)
        for exercise in bot.exercises:
            if exercise["id"] in user.exercises:
                s += str(user.exercises[exercise["id"]]).ljust(len(exercise["name"]) + 2)
            else:
                s += str(0).ljust(len(exercise["name"]) + 2)
        s += "\n"

        user.store_session(str(datetime.datetime.now()))

    s += "```"

    if not bot.debug:
        requests.post(bot.post_URL, data=s)
    print(s)

    # write to file
    with open('user_cache.save', 'wb') as f:
        pickle.dump(bot.user_cache, f)


def is_valid_datetime(bot):
    now = datetime.datetime.now()

    if not now.weekday() in bot.days:
        return False

    for start, stop in bot.hours:
        if start <= now.hour < stop:
            return True

    return False


def main():
    bot = Bot()

    try:
        bot.load_configuration()
        exercise = draw_exercise(bot)
        assign_exercise(bot, exercise)

        while True:
            if is_valid_datetime(bot):
                bot.load_configuration()
                exercise = prepare_next_exercise(bot)
                assign_exercise(bot, exercise)
            else:
                if not bot.debug:
                    time.sleep(5 * 60)
                else:
                    time.sleep(5)

    except KeyboardInterrupt:
        save_users(bot)


main()
