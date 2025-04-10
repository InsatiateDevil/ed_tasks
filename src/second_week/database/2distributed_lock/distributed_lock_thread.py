import time
import datetime
import unittest
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Callable

import redis


def timeout_handler(signum, frame):
    raise TimeoutError("Время выполнения превышено")


class RedisLock:
    def __init__(self, lock_key, timeout):
        self.r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        self.lock_key = lock_key
        self.timeout = timeout

    def set_lock(self):
        if self.r.set(self.lock_key, "locked", ex=self.timeout, nx=True):
            return True
        else:
            return False

    def release_lock(self):
        if self.r.get(self.lock_key) == "locked":
            self.r.delete(self.lock_key)
            return True
        else:
            return False


def single(func: Callable = None, max_processing_time: datetime.timedelta = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            lock = RedisLock(func.__name__, int(max_processing_time.total_seconds()))
            if not lock.set_lock():
                raise RuntimeError("Функция уже выполняется")

            try:
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(func, *args, **kwargs)
                    result = future.result(
                        timeout=int(max_processing_time.total_seconds())
                    )
                return result
            finally:
                lock.release_lock()

        return wrapper

    return decorator


@single(max_processing_time=datetime.timedelta(seconds=2))
def process_transaction():
    time.sleep(2.1)


class TestMyDecorator(unittest.TestCase):
    @single(max_processing_time=datetime.timedelta(seconds=2))
    def raise_runtime_error(self):
        time.sleep(2)

    @single(max_processing_time=datetime.timedelta(seconds=2))
    def raise_timeout_error(self):
        time.sleep(2.1)

    def test_raise_runtime_error(self):
        with ThreadPoolExecutor(max_workers=3) as executor:
            future = {executor.submit(self.raise_runtime_error) for _ in range(3)}

            for future in as_completed(future):
                try:
                    result = future.result()
                except RuntimeError as e:
                    self.assertIsInstance(e, RuntimeError)

    def test_raise_timeout_error(self):
        with self.assertRaises(TimeoutError) as e:
            self.raise_timeout_error()


if __name__ == "__main__":
    unittest.main()

    # start_time = time.time()
    # try:
    #     process_transaction()
    # except RuntimeError as e:
    #     print("RuntimeError был возбужден")
    # except TimeoutError as e:
    #     print("TimeoutError был возбужден")
    # finally:
    #     finish_time = time.time()
    #     result_time = finish_time - start_time
    #     print(result_time)
