from parsers.BaseParser import BaseParser
from bs4 import BeautifulSoup
from models.item import Item
from utils.helpers import clean_text, normalize_url


class HtmlParser(BaseParser):  # FIX: đổi tên từ `Parser` -> `HtmlParser` cho khớp Engine.py và mindmap
    def __init__(self, config):
        super().__init__(config)

    def extract_links(self, html_content, base_url=None):
        soup = BeautifulSoup(html_content or "", "html.parser")
        links = []
        seen = set()
        for anchor in soup.find_all("a", href=True):
            href = str(anchor["href"]).strip()
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue
            try:
                normalized = normalize_url(href, base_url)
            except ValueError:
                continue
            if normalized not in seen:
                seen.add(normalized)
                links.append(normalized)
        return links

    def parse(self, data, base_url=None):
        """base_url nên là URL của chính trang vừa fetch (task.url), không phải config.

        FIX cũ: code trước check `isinstance(self.config, dict)` để quyết định có gọi
        `.get("url")` không -> nhưng self.config thường là object `Setting`, không phải
        dict, nên luôn rơi vào None. Giờ nhận base_url trực tiếp làm tham số, rõ ràng hơn.
        """
        if isinstance(data, bytes):
            data = data.decode("utf-8", errors="replace")
        if not isinstance(data, str):
            raise TypeError("HTML data must be text or bytes")

        soup = BeautifulSoup(data, "html.parser")
        for element in soup(["script", "style", "noscript", "template"]):
            element.decompose()

        title = clean_text(soup.title.get_text(" ", strip=True)) if soup.title else ""
        return Item({
            "title": title,
            "content": clean_text(soup.get_text(" ", strip=True)),
            "links": self.extract_links(data, base_url),
        })
