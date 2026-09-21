import asyncio
from dataclasses import replace
from urllib.parse import urlparse

from config.setting import Setting
from core.Scheduler import Scheduler          # FIX: trước là `from Scheduler import scheduler` (sai path)
from core.Pipeline import Pipeline            # FIX: trước là `from Pipeline import pipeline` (sai path)
from models.task import Task                  # MỚI: thay cho `task = {URL, depth}` (set sai kiểu)
from parsers.NormalWeb import HtmlParser      # FIX: khớp tên class thật sự trong NormalWeb.py
from fetchers.StaticFetcher import HttpFetcher
from fetchers.DynamicFetcher import DynamicFetcher
from middlewares.proxy import ProxyMiddleware
from middlewares.retry import RetryMiddleware
from middlewares.rate_limiter import RateLimiter
from storage.json_storage import JsonStorage
from storage.db_storage import DBStorage
from utils.logger import get_logger

logger = get_logger(__name__)


class ScraperEngine:
    def __init__(self, config=None, *, allowed_domains=None, max_depth=3):
        self.setting = Setting(config)

        fetcher_type = self.setting.get("fetcher_type", "http")
        if fetcher_type in ("selenium", "playwright"):
            self.fetcher = DynamicFetcher(self.setting)
        else:
            self.fetcher = HttpFetcher(self.setting)

        self.parser = HtmlParser(self.setting)
        self.scheduler = Scheduler()
        self.pipeline = Pipeline()

        self.rate_limiter = RateLimiter(
            self.setting.get("RATE_LIMIT", 1),
            self.setting.get("RATE_WINDOW", 1.0),
        )
        self.retry_middleware = RetryMiddleware(self.setting.get("MAX_RETRIES", 3))
        self.proxy_middleware = ProxyMiddleware(self.setting.get("PROXIES", []))

        storage_backend = self.setting.get("storage_backend", "json")
        self.storage = DBStorage(self.setting.config) if storage_backend == "db" else JsonStorage(self.setting.config)

        self.allowed_domains = {d.lower() for d in allowed_domains} if allowed_domains else None
        self.max_depth = max_depth
        self.visited = set()
        # Nếu dùng DB và muốn resume crawl từ lần trước, nạp sẵn url đã có vào visited:
        if hasattr(self.storage, "all_urls"):
            self.visited |= self.storage.all_urls()

        self._running = False

    def _in_scope(self, url):
        if self.allowed_domains is None:
            return True
        return urlparse(url).netloc.lower() in self.allowed_domains

    def add_task(self, url, depth=0, priority=0, parent_url=None):
        # FIX: trước là `task = {URL, depth}` (set, sai kiểu) và không hề gọi Schedule.add_task()
        if url in self.visited or not self._in_scope(url):
            return
        self.visited.add(url)
        task = Task(url=url, depth=depth, priority=priority, parent_url=parent_url)
        self.scheduler.add_task(task, priority=priority)

    async def _fetch(self, url):
        fetch = self.fetcher.fetch
        if asyncio.iscoroutinefunction(fetch):
            return await fetch(url)
        return await asyncio.to_thread(fetch, url)

    async def _process_task(self, task):
        await self.rate_limiter.wait()
        html = await self._fetch(task.url)
        item = self.parser.parse(html, base_url=task.url)
        item["url"] = task.url
        item["depth"] = task.depth
        return item

    async def run(self):
        self._running = True
        while self._running and not self.scheduler.is_empty():
            task = self.scheduler.get_next()
            try:
                item = await self._process_task(task)
            except Exception as exc:
                logger.warning("Fetch thất bại cho %s: %s", task.url, exc)
                if task.retries < self.retry_middleware.max_retries:
                    retry_task = replace(task, retries=task.retries + 1)
                    self.visited.discard(task.url)
                    self.scheduler.add_task(retry_task, priority=retry_task.priority)
                else:
                    logger.error("Bỏ cuộc với %s sau %s lần thử", task.url, task.retries)
                continue

            processed = self.pipeline.process_item(item)
            if processed is not None:
                self.storage.save(processed)

            # FIX: trước đây link tìm được không bao giờ được đưa lại vào Scheduler
            if task.depth < self.max_depth:
                for link in item.get("links", []):
                    self.add_task(link, depth=task.depth + 1, parent_url=task.url)

    async def stop(self):  # đổi từ sync `def stop` -> async `def stop`
        self._running = False
        close = getattr(self.fetcher, "close", None)
        if close is None:
            return
        if asyncio.iscoroutinefunction(close):
            await close()
        else:
            close()


ScaperEngine = ScraperEngine  # giữ alias phòng khi nơi khác lỡ import theo tên cũ (có lỗi chính tả)
