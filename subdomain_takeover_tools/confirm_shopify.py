import requests
import urllib3

from subdomain_takeover_tools.helper.main import bootstrap

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ONLY_ONE_STEP_LEFT = 'Only one step left!'

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
}


def is_valid(hostname, _):
    return confirm_shopify(hostname)


def confirm_shopify(hostname):
    if hostname.endswith('.myshopify.com') or hostname.endswith('.shopify.com'):
        return False

    try:
        r = requests.get('http://%s' % hostname, verify=False, timeout=15, headers=headers)
        return ONLY_ONE_STEP_LEFT in r.text
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        return False


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
