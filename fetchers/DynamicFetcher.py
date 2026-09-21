import os
import json
from pathlib import Path
from playwright_stealth import Stealth
from fetchers.BaseFetchers import BaseFetcher

class DynamicFetcher(BaseFetcher):
    def __init__(self, config=None):
        super().__init__(config or {})
        self._playwright = None
        self._browser = None
        self.context = None
        self._page = None
        self._stealth = Stealth()

    async def _ensure_driver(self):
        if self._page is not None:
            return
        
        from playwright.async_api import async_playwright
        
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.config["HEADLESS"])
        self.context = await self._browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        await self._stealth.apply_stealth_async(self.context)

        if self.config.get("COOKIES_PATH") and os.path.exists(
            os.path.join(Path(__file__).parent, self.config["COOKIES_PATH"])
        ):
            with open(os.path.join(Path(__file__).parent, self.config["COOKIES_PATH"]), "r") as f:
                cookies = json.load(f)
                await self.context.add_cookies(cookies)

        self._page = await self.context.new_page()

    async def fetch(self, url, wait_until="networkidle"):
        await self._ensure_driver()
        await self._page.goto(url, wait_until=wait_until)
        return await self._page.content()

    async def close(self):
        if self._browser is not None:
            await self._browser.close()
        if self._playwright is not None:
            await self._playwright.stop()
