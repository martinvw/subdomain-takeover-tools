import functools
from typing import Optional

import requests

from subdomain_takeover_tools.helper.load_token import load_token
from subdomain_takeover_tools.helper.main import bootstrap
from subdomain_takeover_tools.helper.prepare import resolve_cname

EDGE_CDN = '.azureedge.net'
_CDN_URL = "https://management.azure.com/providers/Microsoft.Cdn/checkNameAvailability?api-version=2019-12-31"


@functools.lru_cache(maxsize=None)
def _get_session_and_token() -> tuple:
    session = requests.Session()
    token = load_token()
    return session, token


def is_valid(hostname: str, cname: Optional[str]) -> Optional[bool]:
    if hostname == cname:
        cname = resolve_cname(hostname)

    if cname is None:
        return False

    return confirm_azure_edge_cdn(cname)


def confirm_azure_edge_cdn(cname: str) -> bool:
    session, token = _get_session_and_token()

    try:
        if cname.count('.') == 2 and EDGE_CDN in cname:
            dns_prefix = cname.replace(EDGE_CDN, '')
            result = session.post(
                _CDN_URL,
                json={
                    'name': dns_prefix,
                    'type': 'Microsoft.Cdn/Profiles/Endpoints'
                },
                headers={
                    "Authorization": f"Bearer {token}"
                }
            )
            return result.json()['nameAvailable']
    except KeyError:
        pass
    return False


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
