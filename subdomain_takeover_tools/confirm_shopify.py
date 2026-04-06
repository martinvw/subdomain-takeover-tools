import warnings
from typing import Optional

import requests
import urllib3

from subdomain_takeover_tools.helper.main import bootstrap

ONLY_ONE_STEP_LEFT = 'Only one step left!'

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
}


def is_valid(hostname: str, _: Optional[str]) -> Optional[bool]:
    return confirm_shopify(hostname)


def confirm_shopify(hostname: str) -> bool:
    if hostname.endswith('.myshopify.com') or hostname.endswith('.shopify.com'):
        return False

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", urllib3.exceptions.InsecureRequestWarning)
            r = requests.get(f'http://{hostname}', verify=False, timeout=15, headers=headers)
        return ONLY_ONE_STEP_LEFT in r.text
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        return False


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
