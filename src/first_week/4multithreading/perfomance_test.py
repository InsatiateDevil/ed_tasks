import csv
import random
import sys
import time
import json
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

sys.setrecursionlimit(10**6)


# Создание массива чисел для теста
def generate_data(n):
    list_of_numbers = []
    for _ in range(n):
        list_of_numbers.append(random.randint(1, 1000))
    return list_of_numbers


# Высоконагруженная функция
def factorial(number):
    if number == 0 or number == 1:
        return 1
    else:
        return number * factorial(number - 1)


# Различные варианты параллельного выполнения


# Вариант A: Использование пула потоков с concurrent.futures
def process_with_threads(data):
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(factorial, data))
    return results


# Вариант Б: Использование multiprocessing.Pool с пулом процессов, равным количеству CPU.
def process_with_pool(data):
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.map(factorial, data)
    return results


# Вариант В: Использование multiprocessing.Process и очередей
def worker(input_queue, output_queue):
    while True:
        number = input_queue.get()
        if number is None:
            break
        output_queue.put(factorial(number))


def process_with_processes(data):
    input_queue = multiprocessing.Queue()
    output_queue = multiprocessing.Queue()
    processes = []

    # Создание процессов
    for _ in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=worker, args=(input_queue, output_queue))
        p.start()
        processes.append(p)

    # Отправка данных в очередь
    for number in data:
        input_queue.put(number)

    # Завершение процессов
    for _ in processes:
        input_queue.put(None)

    results = [output_queue.get() for _ in data]

    # Ожидание завершения всех процессов
    for p in processes:
        p.join()

    return results


# Сравнение производительности
def compare_performance(data):
    results = {}

    # Однопоточный вариант
    start = time.time()
    single_thread_result = [factorial(num) for num in data]
    results["Single Thread"] = time.time() - start

    # Вариант А c использованием пула потоков с concurrent.futures
    start = time.time()
    thread_result = process_with_threads(data)
    results["Thread Pool"] = time.time() - start

    # Вариант Б с использованием multiprocessing.Pool с доступным количеством процессоров
    start = time.time()
    pool_result = process_with_pool(data)
    results["Process Pool"] = time.time() - start

    # Вариант В с использованием связки процессов и очередей
    start = time.time()
    process_result = process_with_processes(data)
    results["Separate Processes"] = time.time() - start

    return results


# Сохранение результатов в json и csv форматах
def save_results(results, filename):
    with open(filename, "w") as f:
        json.dump(results, f)


def save_results_csv(results, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Variant", "Time"])
        for variant, time in results.items():
            writer.writerow([variant, time])


if __name__ == "__main__":
    n = 1000000  # Количество генерируемых чисел для теста
    data = generate_data(n)

    # Сравнение производительности
    performance_results = compare_performance(data)

    print("Время выполнения разных вариантов обработки CPU-bound задачи, секундах:")
    for variant, time in performance_results.items():
        print(f"{variant}: {time:.3f} seconds")

    save_results(performance_results, "performance_results.json")
    save_results_csv(performance_results, "performance_results.csv")
