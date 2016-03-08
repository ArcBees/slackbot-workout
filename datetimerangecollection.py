import random
from datetime import datetime, timedelta


class DateTimeRangeCollection:
    def __init__(self, settings):
        self.settings = settings

    def draw_seconds(self):
        today = datetime.today()
        start, stop = self.next_range()
        min_seconds = self.settings.callout_min_time * 60
        max_seconds = self.settings.callout_max_time * 60

        if stop < today + timedelta(seconds=max_seconds):
            max_seconds = (stop - today).total_seconds()

        if today < start:
            return (start - today).total_seconds() + 1
        elif max_seconds <= min_seconds:
            # Let's squeeze an extra exercise before the end of the current range :p
            return max_seconds
        else:
            return random.randrange(min_seconds, max_seconds + 1)

    def next_range(self):
        next_range = self.next_range_today()
        if next_range is None:
            next_range = self.next_range_future()
        return next_range

    def next_range_today(self):
        today = datetime.today()

        if not today.weekday() in self.settings.weekdays:
            return

        for hour_start, hour_stop in self.settings.hours:
            if hour_start > hour_stop:
                print("Invalid hour range [", hour_start, "-", hour_stop, "] will be ignored.")
            else:
                start = datetime(today.year, today.month, today.day, hour_start)
                stop = datetime(today.year, today.month, today.day, hour_stop)

                if start <= today < stop or today < start:
                    return start, stop

        return None

    def next_range_future(self):
        next_datetime = datetime.today()
        weekday = next_datetime.weekday()
        allowed_weekdays = self.settings.weekdays

        next_weekday_index = allowed_weekdays.index(weekday)
        next_weekday_index = 0 if next_weekday_index == len(allowed_weekdays) - 1 else next_weekday_index + 1
        next_weekday = allowed_weekdays[next_weekday_index]

        days_to_add = next_weekday - weekday
        if weekday >= next_weekday:
            days_to_add += 7

        next_datetime += timedelta(days=days_to_add)
        next_datetime = next_datetime.replace(minute=0, second=0, microsecond=0)
        return next_datetime.replace(hour=self.settings.hours[0][0]), \
               next_datetime.replace(hour=self.settings.hours[0][1])
