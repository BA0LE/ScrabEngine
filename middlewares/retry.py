class RetryMiddleware:
    RETRYABLE_STATUS_CODES = {408, 425, 429, 500, 502, 503, 504}
    def __init__(self, max_retries=3):
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        self.max_retries = max_retries

    def process_request(self, request, retries=1):
        if retries < 0:
            raise ValueError("retries must be non-negative")
        if isinstance(request, dict):
            request.setdefault("meta", {})["retries"] = retries
        else:
            if not hasattr(request, "meta") or request.meta is None:
                request.meta = {}
            request.meta["retries"] = retries
        return request

    def process_response(self, response, retries=0):
        return self.should_retry(response) and retries < self.max_retries

    def should_retry(self, response):
        if isinstance(response, Exception):
            return True
        status = response.get("status_code") if isinstance(response, dict) else getattr(response, "status_code", None)
        return status in self.RETRYABLE_STATUS_CODES
