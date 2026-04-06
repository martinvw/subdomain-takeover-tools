import functools
from typing import Optional

import requests

from subdomain_takeover_tools.helper.main import bootstrap, settings
from subdomain_takeover_tools.helper.prepare import prepare_domain_name


@functools.lru_cache(maxsize=None)
def _get_session() -> tuple:
    session = requests.Session()
    session.auth = (settings['github']['username'], settings['github']['access_token'])
    url = (
        f"https://api.github.com/repos/{settings['github']['username']}"
        f"/{settings['github']['repo']}/pages"
    )
    return session, url


def is_valid(domain: str, _: Optional[str]) -> Optional[bool]:
    if domain is None:
        return False
    return confirm_github(domain)


def confirm_github(domain: str) -> bool:
    if domain.endswith('.github.com') or domain.endswith('.github.io') or domain.endswith('.githubapp.com'):
        return False

    domain = prepare_domain_name(domain)

    session, url = _get_session()
    # GitHub Pages has no read-only availability API; we probe by setting the
    # custom domain CNAME then immediately resetting it to None.
    configure_cname_response = session.put(url, json={'cname': domain})
    session.put(url, json={'cname': None})
    return configure_cname_response.status_code == 204


def main():
    session, url = _get_session()
    session.post(url, json={
        'source': {
            'branch': 'main',
            'path': '/'
        }
    })
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
