import functools
from typing import Optional

import requests

from subdomain_takeover_tools.helper.load_token import load_token
from subdomain_takeover_tools.helper.main import bootstrap, settings
from subdomain_takeover_tools.helper.prepare import resolve_cname

API_MANAGEMENT_NET = '.azure-api.net'


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

    return confirm_azure_api_management(cname)


def confirm_azure_api_management(cname: str) -> bool:
    session, token = _get_session_and_token()

    try:
        if cname.count('.') == 2 and API_MANAGEMENT_NET in cname:
            dns_prefix = cname.replace(API_MANAGEMENT_NET, '')
            result = session.post(
                "https://management.azure.com/api/invoke",
                json={'name': dns_prefix, 'type': 'Microsoft.ApiManagement/service'},
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-Ms-Path-Query": (
                        f"/subscriptions/{settings['azure']['subscription_id']}"
                        "/providers/Microsoft.ApiManagement/checkNameAvailability"
                        "?api-version=2022-09-01-preview"
                    )
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
