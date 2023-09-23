import requests
from azure.identity import DefaultAzureCredential

from subdomain_takeover_tools.helper.main import bootstrap, settings
from subdomain_takeover_tools.helper.prepare import resolve_cname

EDGE_CDN = '.azure-api.net'

credential = DefaultAzureCredential()

session = requests.Session()
(token, _) = credential.get_token('https://management.azure.com/.default')
session.headers['Authorization'] = "Bearer " + token
url = "https://management.azure.com/api/invoke"


def is_valid(hostname, cname):
    if hostname == cname:
        cname = resolve_cname(hostname)

    if cname is None:
        return False

    return confirm_azure_edge_cdn(cname)


def confirm_azure_edge_cdn(cname):
    try:
        if cname.count('.') == 2 and EDGE_CDN in cname:
            dns_prefix = cname.replace(EDGE_CDN, '')
            result = session.post(url, json={'name': dns_prefix, 'type': 'Microsoft.ApiManagement/service'}, headers={
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
