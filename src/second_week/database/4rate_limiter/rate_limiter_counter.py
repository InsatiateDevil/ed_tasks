import time

import redis


class RateLimitExceed(Exception):
    pass


class RateLimiter:
    # логика такова что мы устанаваливаем время жизни ключа только
    # при его создании, а в последующем увеличиваем сам счетчик,
    # но не затрагиваем его время жизни.

    def __init__(self, limit=5, period=3):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.limit = limit
        self.period = period

    def test(self) -> bool:
        key = "rate_limiter"  # Ключ для хранения счетчика

        # Увеличиваем значение счетчика на 1
        request_count = self.redis.incr(key)

        if request_count == 1:
            # Если это первый запрос, устанавливаем время жизни ключа
            self.redis.expire(key, self.period)

        if request_count <= self.limit:
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
