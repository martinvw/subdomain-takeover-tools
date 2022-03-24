import requests
from azure.identity import DefaultAzureCredential

from subdomain_takeover_tools.helper.main import bootstrap
from subdomain_takeover_tools.helper.prepare import resolve_cname

EDGE_CDN = '.azureedge.net'

credential = DefaultAzureCredential()

session = requests.Session()
(token, _) = credential.get_token('https://management.azure.com/.default')
session.headers['Authorization'] = "Bearer " + token
url = "https://management.azure.com/providers/Microsoft.Cdn/checkNameAvailability?api-version=2019-12-31"


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
            result = session.post(url, json={'name': dns_prefix, 'type': 'Microsoft.Cdn/Profiles/Endpoints'})
            return result.json()['nameAvailable']
    except KeyError:
        pass
    return False


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
