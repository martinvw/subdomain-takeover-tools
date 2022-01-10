import requests
import urllib3

from helper.main import main

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ONLY_ONE_STEP_LEFT = 'Only one step left!'

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
}


def is_valid(hostname, _):
    try:
        r = requests.get('http://%s' % hostname, verify=False, timeout=15, headers=headers)
        return ONLY_ONE_STEP_LEFT in r.text
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        return False


if __name__ == "__main__":
    main(is_valid)
