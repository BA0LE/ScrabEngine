
class ProxyMiddleware:
    def __init__(self, proxy_list):
        self.proxy_list = list(proxy_list or [])
        self.current_proxy_index = 0

    def get_next_proxy(self):
        if not self.proxy_list:
            return None
        proxy = self.proxy_list[self.current_proxy_index]
        self.rotate_proxy()
        return proxy

    def process_request(self, request):
        proxy = self.get_next_proxy()
        if proxy:
            if isinstance(request, dict):
                request.setdefault("meta", {})["proxy"] = proxy
            else:
                if not hasattr(request, "meta") or request.meta is None:
                    request.meta = {}
                request.meta["proxy"] = proxy
        return request

    def rotate_proxy(self):
        if self.proxy_list:
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
