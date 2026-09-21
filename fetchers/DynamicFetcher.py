from fetchers.BaseFetchers import BaseFetcher
import os
import json
from pathlib import Path
import playwright_stealth
class DynamicFetcher(BaseFetcher):

    def __init__(self, config=None):
        super().__init__(config or {})
        self._playwright = None
        self._browser = None
        self._page = None

    def _ensure_driver(self):
        if self._page is not None:
            return
        from playwright.sync_api import sync_playwright
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=True)
        self.context = self._browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        if self.config.get("COOKIES_PATH") and os.path.exists(os.path.join(Path(__file__).parent, self.config["COOKIES_PATH"])):
            with open(os.path.join(Path(__file__).parent, self.config["COOKIES_PATH"]), "r") as f:
                cookies = json.load(f)
                self.context.add_cookies(cookies)

        self._page = self.context.new_page()
        playwright_stealth.Stealth.apply_stealth_async(self._page)

    def fetch(self, url, wait_until="networkidle"):
        self._ensure_driver()
        self._page.goto(url, wait_until=wait_until)
        return self._page.content()

    def close(self):
        if self._browser is not None:
            self._browser.close()
        if self._playwright is not None:
            self._playwright.stop()
