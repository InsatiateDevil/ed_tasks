import time


class SingletonMetaclass(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Singleton(metaclass=SingletonMetaclass):
    pass


if __name__ == "__main__":
    s1 = Singleton()
    s2 = Singleton()

    if id(s1) == id(s2):
        print("Паттерн работает корректно.")
    else:
        print("Паттерн не отрабатывает должным образом.")

# ToDo - вопрос по заданию
# Какие можете привести примеры невозможности реализации
# функционала без использования метакласса
