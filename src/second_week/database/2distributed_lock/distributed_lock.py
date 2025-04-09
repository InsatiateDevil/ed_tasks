import signal
import threading
import time
import datetime
from typing import Callable

import redis


def timeout_handler(signum, frame):
    raise TimeoutError("Время выполнения превышено")


class RedisLock:
    def __init__(self, lock_key, timeout):
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.lock_key = lock_key
        self.timeout = timeout

    def set_lock(self):
        if self.r.set(self.lock_key, 'locked', ex=self.timeout, nx=True):
            return True
        else:
            return False

    def release_lock(self):
        if self.r.get(self.lock_key) == 'locked':
            self.r.delete(self.lock_key)
            return True
        else:
            return False


def single(func: Callable=None, max_processing_time: datetime.timedelta=None):

    def decorator(func):

        def wrapper(*args, **kwargs):
            lock = RedisLock(func.__name__, int(max_processing_time.total_seconds()))
            if not lock.set_lock():
                raise RuntimeError("Функция уже выполняется")

            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(max_processing_time.total_seconds()))

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                signal.alarm(0)
                lock.release_lock()

        return wrapper

    return decorator


@single(max_processing_time=datetime.timedelta(minutes=2))
def process_transaction():
    time.sleep(2)


if __name__ == '__main__':
    start_time = time.time()
    try:
        process_transaction()
    except RuntimeError as e:
        print("RuntimeError был возбужден")
    finally:
        finish_time = time.time()
        result_time = finish_time - start_time
        print(result_time)
