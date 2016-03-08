import requests


class CallOut:
    def __init__(self, settings, exercise, reps, users):
        self.settings = settings
        self.exercise = exercise
        self.reps = reps
        self.users = users

    def publish(self):
        message = str(self.reps) + " " + self.exercise["units"] + " " + self.exercise["name"] + " RIGHT NOW "
        message += self.format_handles(self.users)

        if not self.settings.is_debug:
            requests.post(self.settings.post_url, data=message)
        print(message)

    def format_handles(self, handles):
        result = ""
        count = len(handles)

        for i in range(count):
            result += handles[i]
            if i == count - 2:
                result += " and "
            elif i == count - 1:
                result += "!"
            else:
                result += ", "
        return result
