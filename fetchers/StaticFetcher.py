import requests
import os
from fetchers.BaseFetchers import BaseFetcher
import json


class HttpFetcher(BaseFetcher):
    def __init__(self, config):
        super().__init__(config)  # FIX: __init__ cũ nhận `url` vô nghĩa, giờ nhận `config` như BaseFetcher yêu cầu
        self.headers = self._build_headers()

    def fetch(self, url, params=None):
        timeout = self.config.get("TIMEOUT", 10) if hasattr(self.config, "get") else 10
        if self.config.get("COOKIES_PATH") and os.path.exists(self.config["COOKIES_PATH"]):
            self.session = requests.Session()
            with open(self.config["COOKIES_PATH"], "r") as f:
                browser_cookies = json.load(f)
                cookies_dict = {cookie['name']: cookie['value'] for cookie in browser_cookies}
                self.session.cookies.update(cookies_dict)
            response = self.session.get(url, headers=self.headers, params=params, timeout=timeout)

        else:
            response = requests.get(url, headers=self.headers, params=params, timeout=timeout)
            response.raise_for_status()
        return response.text

    def _build_headers(self):
        user_agent = self.config.get("USER_AGENT", "ScrabEngine/1.0") if hasattr(self.config, "get") else "ScrabEngine/1.0"
        return {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
