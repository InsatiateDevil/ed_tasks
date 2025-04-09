import random
import time

import redis


class RateLimitExceed(Exception):
    pass


class RateLimiter:

    def __init__(self, limit=5, period=3):
        self.redis = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
        self.limit = limit
        self.period = period

    def test(self) -> bool:
        """
        Логика ограничения количества запросов - в бд(редис) помещаем множество
        по ключу key, в которое будем добавлять временные метки совершаемых
        запросов. При добавлении будем чистить устаревшие метки, всё множество
        также будем удалять через встроенный в редис таймер(истечение времени
        хранения ключа).
        """
        current_time = time.time()  # Записываем время для временных меток
        key = "rate_limiter"  # Ключ для хранения множества с временными метками

        # Удаляем устаревшие метки(дословно текущее время минус
        # ограничивающий период это устаревшие метки которые уже не нужны)
        self.redis.zremrangebyscore(key, 0, current_time - self.period)

        # Получаем текущее количество элементов в множестве после очистки
        request_count = self.redis.zcard(key)

        if request_count < self.limit:
            # Добавляем новую временную метку
            self.redis.zadd(key, {current_time: current_time})
            # Обновляем период хранения всего множества
            self.redis.expire(key, self.period)
            return True
        else:
            return False


def make_api_request(rate_limiter: RateLimiter):
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        # какая-то бизнес логика
        pass


if __name__ == '__main__':
    rate_limiter = RateLimiter()

    for _ in range(15):
        time.sleep(0.55)

        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")
