from typing import Optional

from subdomain_takeover_tools.helper.http_fingerprint import fetch_body
from subdomain_takeover_tools.helper.main import bootstrap

UNRECOGNIZED_DOMAIN = 'Unrecognized domain <strong>'

EXCLUDE = ('.mashery.com',)


def is_valid(hostname: str, _: Optional[str]) -> Optional[bool]:
    if hostname.endswith(EXCLUDE):
        return False

    (_status, body) = fetch_body(hostname)
    if body is None:
        return False

    return UNRECOGNIZED_DOMAIN in body


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
