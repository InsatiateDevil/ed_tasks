def search(array: list, value: int) -> bool:
    """Функция принимает на вход отсортированный массив и искомое значение
    и возвращает True в случае нахождения искомого значения в массиве
    и False в противном случае."""
    start = 0
    end = len(array) - 1
    if not (value < array[start] or value > array[end]):
        while start <= end:
            middle = (start + end) // 2
            if array[middle] == value:
                return True
            elif array[middle] > value:
                end = middle - 1
            elif array[middle] < value:
                start = middle + 1
    return False


if __name__ == "__main__":
    array_for_search = [1, 2, 3, 45, 356, 569, 600, 705, 923]

    print(search(array_for_search, 600))

# ToDo - Вопрос по заданию
# Почему в задании указан тип id для number?
