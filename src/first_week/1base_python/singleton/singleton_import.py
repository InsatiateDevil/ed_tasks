from singleton_for_import import example


if __name__ == "__main__":
    s1 = example
    s2 = example

    if id(s1) == id(s2):
        print("Паттерн работает корректно.")
    else:
        print("Паттерн не отрабатывает должным образом.")
