import asyncio
import concurrent
import json
import aiohttp


def read_large_file(file_name):
    with open(file_name, "r") as file:
        for line in file:
            yield line.strip()


def write_to_file(file_path, data):
    lock = asyncio.Lock()
    with lock:
        with open(file_path, "a+") as f:
            f.write(json.dumps(data) + "\n")


async def fetch_urls(path_to_urls: str, file_path: str):
    urls = read_large_file(path_to_urls)

    async def fetch_url(session: aiohttp.ClientSession, url: str,
                        semaphore: asyncio.Semaphore):
        try:
            async with semaphore:
                async with session.get(url, timeout=10) as response:
                    content = await response.text()
                    result_dict = {
                        "url": url,
                        "status": response.status,
                        "content": content,
                    }
        except Exception as e:
            content = None
            result_dict = {
                "url": url,
                "status": e.__class__.__name__,
                "content": content,
            }
        return result_dict

# создание 2 очередей (под чтение из урла и под запись в файл)
# запуск пяти воркеров
# подача урлов в воркеры (aiofiles)
# воркер возвращает text
# memray


if __name__ == "__main__":
    asyncio.run(fetch_urls("urls.txt", "./results.json"))
