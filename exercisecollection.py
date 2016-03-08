import random


class ExerciseCollection:
    def __init__(self, settings):
        self.settings = settings

    def draw(self):
        exercises = self.get_exercises()
        idx = random.randrange(0, len(exercises))
        return exercises[idx]

    def get_exercises(self):
        return self.settings.exercises
