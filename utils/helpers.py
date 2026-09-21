def clean_text(text):
    """
    Cleans the input text by removing unwanted characters and formatting.

    Args:
        text (str): The input text to be cleaned.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    cleaned_text = text.strip()

    # Replace multiple spaces with a single space
    cleaned_text = ' '.join(cleaned_text.split())

    # Additional cleaning steps can be added here

    return cleaned_text

    #add more filters later

def normalize_URL(URL, base_url=None):
    """Resolve a URL and remove fragments and non-significant trailing slashes."""
    from urllib.parse import urljoin, urlparse, urlunparse

    if not isinstance(URL, str) or not URL.strip():
        raise ValueError("URL must be a non-empty string")
    value = urljoin(base_url, URL.strip()) if base_url else URL.strip()
    parts = urlparse(value)
    path = parts.path.rstrip("/") or ("/" if parts.path == "/" else "")
    return urlunparse(parts._replace(scheme=parts.scheme.lower(), netloc=parts.netloc.lower(), path=path, fragment=""))


normalize_url = normalize_URL
