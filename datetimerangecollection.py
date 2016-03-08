import random
from datetime import datetime, timedelta


class DateTimeRangeCollection:
    def __init__(self, settings):
        self.settings = settings

    def draw_minutes(self):
        today = datetime.today()
        start, stop = self.next_range()
        min_minutes = self.settings.callout_min_time
        max_minutes = self.settings.callout_max_time

        if stop < today + timedelta(minutes=max_minutes):
            max_minutes = (stop - today).total_seconds() / 60

        if today < start:
            return (start - today).total_seconds() / 60
        elif max_minutes <= min_minutes:
            # Let's squeeze an extra exercise before the end of the current range :p
            return max_minutes
        else:
            return random.randrange(min_minutes, max_minutes)

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

                if start <= today < stop:
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
