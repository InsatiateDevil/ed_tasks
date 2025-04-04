import asyncio
import json
import aiohttp

urls = [
    "https://example.com",
    "https://httpbin.org/status/404",
    "https://nonexistent.url",
    "https://httpbin.org/status/200",
    "https://example5.com",
    "https://example4.com",
    "https://example3.com",
    "https://example2.com",
    "https://example1.com",
    "https://example0.com",
]


async def fetch_urls(urls: list[str], file_path: str):
    semaphore = asyncio.Semaphore(5)
    results_dict = {}

    for url in urls:
        async with aiohttp.ClientSession() as session:
            try:
                async with semaphore:
                    async with session.get(url, timeout=5) as response:
                        results_dict[url] = response.status
            except Exception as e:
                results_dict[url] = e.__class__.__name__

    with open(file_path, "w") as f:
        json.dump(results_dict, f, indent=4)


if __name__ == "__main__":
    asyncio.run(fetch_urls(urls, "./results.json"))
