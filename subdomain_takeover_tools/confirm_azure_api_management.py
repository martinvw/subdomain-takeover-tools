import requests

from subdomain_takeover_tools.helper.main import bootstrap, settings
from subdomain_takeover_tools.helper.prepare import resolve_cname
from subdomain_takeover_tools.helper.load_token import load_token

EDGE_CDN = '.azure-api.net'

token = None
session = requests.Session()
url = "https://management.azure.com/api/invoke"


def is_valid(hostname, cname):
    if hostname == cname:
        cname = resolve_cname(hostname)

    if cname is None:
        return False

    return confirm_azure_edge_cdn(cname)


def confirm_azure_edge_cdn(cname):
    global token
    if token is None:
        token = load_token()

    try:
        if cname.count('.') == 2 and EDGE_CDN in cname:
            dns_prefix = cname.replace(EDGE_CDN, '')
            result = session.post(url, json={'name': dns_prefix, 'type': 'Microsoft.ApiManagement/service'}, headers={
                "Authorization": "Bearer " + token,
                "X-Ms-Path-Query":
                    "/subscriptions/" + settings['azure']['subscription_id']
                    + "/providers/Microsoft.ApiManagement/checkNameAvailability?api-version=2022-09-01-preview"
            })
            return result.json()['nameAvailable']
    except KeyError:
        pass
    return False


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
