import json

import redis


class RedisQueue:
    """Класс очереди сообщений на основе Redis"""
    # Добавляем справа - берем слева(иначе кладем в конец, берем из начала)

    def __init__(self, queue_name: str):
        self.connection = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.queue_name = queue_name

    def publish(self, msg: dict):
        """Добавляет сообщение в очередь"""
        self.connection.rpush(self.queue_name, json.dumps(msg))

    def consume(self) -> dict | None:
        """Получает сообщение из очереди"""
        msg = self.connection.lpop(self.queue_name)
        if msg:
            return json.loads(msg)
        return None


if __name__ == '__main__':
    q = RedisQueue('queue')
    q.publish({'a': 1})
    q.publish({'b': 2})
    q.publish({'c': 3})

    assert q.consume() == {'a': 1}
    assert q.consume() == {'b': 2}
    assert q.consume() == {'c': 3}
