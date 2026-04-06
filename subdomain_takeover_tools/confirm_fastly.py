import functools
from typing import Optional

import requests

from subdomain_takeover_tools.helper.main import bootstrap, settings
from subdomain_takeover_tools.helper.prepare import prepare_domain_name


@functools.lru_cache(maxsize=None)
def _get_session() -> tuple:
    session = requests.Session()
    session.headers['Fastly-Key'] = settings['fastly']['api_token']
    url = (
        f"https://api.fastly.com/service/{settings['fastly']['service']}"
        f"/version/{settings['fastly']['version']}/domain"
    )
    return session, url


def is_valid(domain: str, _: Optional[str]) -> Optional[bool]:
    if domain is None:
        return False
    return confirm_fastly(domain)


def confirm_fastly(domain: str) -> bool:
    session, url = _get_session()
    # Fastly has no read-only availability API; we probe by creating then
    # immediately deleting the domain entry — success means no customer owns it.
    setup_response = session.post(url, data={'name': domain})
    session.delete(f"{url}/{prepare_domain_name(domain)}")
    return (
        "is owned by another customer" not in setup_response.text
        and "is already taken by another customer" not in setup_response.text
    )


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
