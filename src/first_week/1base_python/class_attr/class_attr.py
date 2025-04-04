import datetime


class CreatedAtMixin:
    created_at = datetime.datetime.now()


class SomeClass(CreatedAtMixin):
    pass


if __name__ == "__main__":
    s1 = SomeClass()

    print(s1.created_at)
