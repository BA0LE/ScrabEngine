import asyncio

from core.Engine import ScraperEngine


async def main():
    engine = ScraperEngine(
        config={
            "fetcher_type": "playwright",       # "http" or "selenium"/"playwright"
            "storage_backend": "json",    #"json" or "db"
            "MAX_RETRIES": 5,
            "TIMEOUT": 10,
            "RATE_LIMIT": 2,              #max s 2 request
            "RATE_WINDOW": 1.0,           #per sec
            "COOKIES_PATH": "Cookies.json"
        },
        allowed_domains=None,  #None to Crawl all domain
        max_depth=2,
    )

    engine.add_task("https://www.facebook.com/", depth=1, priority=0)

    try:
        await engine.run()
    finally:
        engine.stop()


if __name__ == "__main__":
    asyncio.run(main())
