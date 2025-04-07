import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

import aiofiles
import aiohttp


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
    async with aiohttp.ClientSession() as session:
        while True:
            url = await url_queue.get()
            if url is None:
                await result_queue.put(None)
                break
            result = await fetch_url(session, url)
            await result_queue.put(result)
            url_queue.task_done()


async def encode_worker(result_queue, write_queue):
    while True:
        url_content = await result_queue.get()
        if url_content is None:
            await write_queue.put(None)
            result_queue.task_done()
            break
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(
            ThreadPoolExecutor(), json.loads, url_content[1]
        )
        await write_queue.put((url_content[0], data))
        result_queue.task_done()


async def write_worker(write_queue, output_file):
    while True:
        write_data = await write_queue.get()
        if write_data is None:
            write_queue.task_done()
            break
        write_data = {write_data[0]: write_data[1]}
        async with aiofiles.open(output_file, "a") as file:
            await file.write(f"{write_data}\n")


async def main(input_file="urls.txt", output_file="results.json"):
    worker_num = 5
    url_queue = asyncio.Queue(maxsize=worker_num)
    result_queue = asyncio.Queue(maxsize=worker_num)
    write_queue = asyncio.Queue(maxsize=worker_num)
    fetch_workers = [
        asyncio.create_task(
            fetch_url_worker(url_queue=url_queue, result_queue=result_queue)
        )
        for _ in range(worker_num)
    ]
    encode_workers = [
        asyncio.create_task(
            encode_worker(result_queue=result_queue, write_queue=write_queue)
        )
        for _ in range(worker_num)
    ]
    write_workers = [
        asyncio.create_task(
            write_worker(write_queue=write_queue, output_file=output_file)
        )
        for _ in range(worker_num)
    ]

    async with aiofiles.open(input_file, "r") as file:
        while True:
            url = await file.readline()
            if not url:
                break
            await url_queue.put(url.strip())

    for _ in range(5):
        await url_queue.put(None)

    await asyncio.gather(*fetch_workers, *encode_workers, *write_workers)
    print("Все процессы завершены, файл сохранен.")


if __name__ == "__main__":
    asyncio.run(main())
