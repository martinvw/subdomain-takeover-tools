from typing import Optional

from subdomain_takeover_tools.helper.http_fingerprint import fetch_body
from subdomain_takeover_tools.helper.main import bootstrap

NO_APPLICATIONS = "404 Not Found: No applications registered for host '"

EXCLUDE = ('.meteor.com',)


def is_valid(hostname: str, _: Optional[str]) -> Optional[bool]:
    if hostname.endswith(EXCLUDE):
        return False

    (_status, body) = fetch_body(hostname)
    if body is None:
        return False

    return NO_APPLICATIONS in body


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
