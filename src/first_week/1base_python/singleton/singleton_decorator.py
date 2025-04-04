import time


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class SomeClass:
    pass


if __name__ == "__main__":
    s1 = SomeClass()
    s2 = SomeClass()

    if id(s1) == id(s2):
        print("Паттерн работает корректно.")
    else:
        print("Паттерн не отрабатывает должным образом.")
