from typing import Optional

from subdomain_takeover_tools.helper.http_fingerprint import fetch_body
from subdomain_takeover_tools.helper.main import bootstrap

# All three substrings must be present; the bare *.surveysparrow.com host is
# itself the takeover surface (claim the workspace), so it is not excluded.
FINGERPRINTS = ('Account not found.', 'ouch!', 'SurveySparrow')


def is_valid(hostname: str, _: Optional[str]) -> Optional[bool]:
    (_status, body) = fetch_body(hostname)
    if body is None:
        return False

    return all(fingerprint in body for fingerprint in FINGERPRINTS)


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
