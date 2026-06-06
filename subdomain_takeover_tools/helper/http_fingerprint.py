import warnings
from typing import Optional, Tuple

import requests
import urllib3

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
}


def fetch_body(domain: str, timeout: int = 15) -> Tuple[Optional[int], Optional[str]]:
    """GET the domain over https (falling back to http) and return
    (status_code, body_text). Returns (None, None) when neither scheme is
    reachable. TLS verification is disabled because unclaimed hosts routinely
    serve mismatched certificates."""
    for scheme in ('https', 'http'):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", urllib3.exceptions.InsecureRequestWarning)
                r = requests.get(f'{scheme}://{domain}', verify=False, timeout=timeout,
                                 headers=headers, allow_redirects=True)
            return r.status_code, r.text
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout,
                requests.exceptions.TooManyRedirects):
            continue
    return None, None
