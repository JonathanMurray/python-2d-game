from pythongame.core.common import Millis


class AbstractWorldBehavior:
    def control(self, time_passed: Millis):
        pass
