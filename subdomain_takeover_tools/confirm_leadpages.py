from typing import Optional

from subdomain_takeover_tools.helper.http_fingerprint import fetch_body
from subdomain_takeover_tools.helper.main import bootstrap

FINGERPRINTS = (
    "This page couldn't be found, so let's get you turned around!",
    "The page you're looking for may have moved.",
    "Double check that you have the right web address and give it another go!",
)

EXCLUDE = ('.leadpages.net', '.leadpages.com')


def is_valid(hostname: str, _: Optional[str]) -> Optional[bool]:
    if hostname.endswith(EXCLUDE):
        return False

    (_status, body) = fetch_body(hostname)
    if body is None:
        return False

    return any(fingerprint in body for fingerprint in FINGERPRINTS)


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
