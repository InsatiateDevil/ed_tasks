import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

import aiofiles
import aiohttp


async def read_worker(file_name, url_queue):
    print("Воркер запущен(чтение)")
    async with aiofiles.open(file_name, "r") as file:
        while True:
            url = await file.readline()
            await url_queue.put(url.strip())
            if url is None:
                for _ in range(5):
                    print("All URLs read.")
                    await url_queue.put(None)
                break
    print("Воркер завершен(чтение)")


async def fetch_url(session, url):
    try:
        print(f"Fetching URL: {url}")
        async with session.get(url, timeout=20) as response:
            if response.status == 200:
                content = await response.read()
                return url, content
            else:
                print(f"Error: Received status code {response.status} for URL: {url}")
    except Exception as e:
        print(f"Exception for URL {url}: {e}")


async def fetch_url_worker(url_queue, result_queue):
    print("Воркер запущен(запрос)")
    async with aiohttp.ClientSession() as session:
        while True:
            url = await url_queue.get()
            if url is None:
                print("All URLs processed.")
                await result_queue.put(None)
                url_queue.task_done()
                break
            result = await fetch_url(session, url)
            await result_queue.put(result)
            url_queue.task_done()
    print("Воркер завершен(запрос)")


async def encode_worker(result_queue, write_queue):
    print("Воркер запущен(декодирование)")
    while True:
        url_content = await result_queue.get()
        if url_content is None:
            print("All results processed.")
            await write_queue.put(None)
            result_queue.task_done()
            break
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(ThreadPoolExecutor(), json.loads, url_content[1])
        await write_queue.put((url_content[0], data))
        result_queue.task_done()
    print("Воркер завершен(декодирование)")


async def write_worker(write_queue, output_file):
    print("Воркер запущен(запись)")
    while True:
        write_data = await write_queue.get()
        if write_data is None:
            print("All data written.")
            write_queue.task_done()
            break
        write_data = {write_data[0]: write_data[1]}
        async with aiofiles.open(output_file, "a") as file:
            await file.write(f"{write_data}\n")
    print("Воркер завершен(запись)")


async def main(input_file="urls.txt", output_file="results.json"):
    worker_num = 5
    url_queue = asyncio.Queue(maxsize=worker_num)
    result_queue = asyncio.Queue(maxsize=worker_num)
    write_queue = asyncio.Queue(maxsize=worker_num)
    read_workers = [asyncio.create_task(read_worker(file_name=input_file, url_queue=url_queue)) for _ in range(1)]
    fetch_workers = [asyncio.create_task(fetch_url_worker(url_queue=url_queue, result_queue=result_queue)) for _ in range(worker_num)]
    encode_workers = [asyncio.create_task(encode_worker(result_queue=result_queue, write_queue=write_queue)) for _ in range(worker_num)]
    write_workers = [asyncio.create_task(write_worker(write_queue=write_queue, output_file=output_file)) for _ in range(worker_num)]

    await asyncio.gather(*read_workers, *fetch_workers, *encode_workers, *write_workers)


if __name__ == "__main__":
    asyncio.run(main())
