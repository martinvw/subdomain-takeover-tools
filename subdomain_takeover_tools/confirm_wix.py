from typing import Optional

from subdomain_takeover_tools.helper.http_fingerprint import fetch_body
from subdomain_takeover_tools.helper.main import bootstrap

# Both substrings must be present (matching the nuclei template's AND condition).
FINGERPRINTS = ('Error ConnectYourDomain occurred', 'wixErrorPagesApp')

EXCLUDE = ('.wixdns.net', '.wix.com', '.wix-code.com', '.wixanswers.com')


def is_valid(hostname: str, _: Optional[str]) -> Optional[bool]:
    if hostname.endswith(EXCLUDE):
        return False

    (_status, body) = fetch_body(hostname)
    if body is None:
        return False

    return all(fingerprint in body for fingerprint in FINGERPRINTS)


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
