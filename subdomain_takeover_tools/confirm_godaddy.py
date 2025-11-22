import requests

from subdomain_takeover_tools.extract_domain_names import extract_domain_name
from subdomain_takeover_tools.helper.main import bootstrap


def is_valid(name, target):
    if target == "" or target is None:
        domain = extract_domain_name(name)
    else:
        domain = extract_domain_name(target)

    return confirm_godaddy(domain)


def confirm_godaddy(name):
    try:
        r = requests.get("https://" + name + "/lander", timeout=30, allow_redirects=True)

        if "is for sale!" in r.text:
            return True

        r = requests.get("https://api.aws.parking.godaddy.com/v1/domains/domain?domain=" + name, timeout=30,
                         allow_redirects=True)

        if "FOR_SALE" in r.text or "/forsale/" in r.text or "is for sale" in r.text or '"hasAuction":true' in r.text:
            return True

        r = requests.get(
            "https://api.aws.parking.godaddy.com/v1/parking/landers/" + name + "?trafficTarget=reseller&abp=1&gdabp=true",
            timeout=30,
            allow_redirects=True)

        if "FOR_SALE" in r.text or "/forsale/" in r.text or "is for sale" in r.text or '"hasAuction":true' in r.text:
            return True

        return False
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        return False


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
