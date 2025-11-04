import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

URL = "https://www.autovit.ro/autoturisme/mg/zs-ev?search%5Border%5D=filter_float_price%3Aasc"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    # requests can decode gzip/deflate automatically; no need to ask for br
    "Referer": "https://www.google.com/",
    "Upgrade-Insecure-Requests": "1",
}


def make_session(timeout=10):
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        status=2,
        status_forcelist=(403, 429, 500, 502, 503, 504),
        allowed_methods=frozenset(["HEAD", "GET"]),
        backoff_factor=0.3,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s = requests.Session()
    s.headers.update(DEFAULT_HEADERS)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.timeout = timeout
    return s


def smart_fetch(url, timeout=10):
    s = make_session(timeout)
    # Warm-up to set cookies (some CDNs do this on HEAD/redirect)
    try:
        s.head(url, allow_redirects=True, timeout=timeout)
    except requests.RequestException:
        pass
    r = s.get(url, allow_redirects=True, timeout=timeout)
    if r.status_code == 403:
        # Slight header tweak and retry once
        alt = dict(DEFAULT_HEADERS)
        alt["Sec-Fetch-Mode"] = "navigate"
        alt["Sec-Fetch-Site"] = "none"
        r = s.get(url, headers=alt, allow_redirects=True, timeout=timeout)
    if r.status_code == 403:
        raise PermissionError("Still 403 (likely bot protection / Cloudflare).")
    r.raise_for_status()
    r.encoding = r.encoding or "utf-8"
    return r.text


html = smart_fetch(URL)
print(html[:500])
