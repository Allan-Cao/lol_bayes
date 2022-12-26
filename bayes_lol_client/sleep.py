import time
from typing import NoReturn


# Adapted from https://github.com/mwclient/mwclient/blob/master/mwclient/sleep.py
class Sleeper(object):
    def __init__(self, max_retries: int, retry_interval: int):
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.retries = 0

    def sleep(self, exception: Exception, sleep_time: int = None) -> NoReturn:
        self.retries += 1

        if self.retries > self.max_retries:
            raise exception

        if sleep_time is None:
            sleep_time = self.retry_interval

        if sleep_time == 0:
            sleep_time = 1

        time.sleep(sleep_time)


class Sleepers(object):
    def __init__(self, max_retries: int, retry_interval: int):
        self.max_retries = max_retries
        self.retry_interval = retry_interval

    def make(self) -> Sleeper:
        return Sleeper(max_retries=self.max_retries, retry_interval=self.retry_interval)
