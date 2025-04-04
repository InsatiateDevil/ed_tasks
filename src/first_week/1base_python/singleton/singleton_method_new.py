class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class SomeClass(Singleton):
    pass


if __name__ == "__main__":
    s1 = SomeClass()
    s2 = SomeClass()

    if id(s1) == id(s2):
        print("Паттерн работает корректно.")
    else:
        print("Паттерн не отрабатывает должным образом.")
