import sys
import time

import dns
import requests
from tldextract import tldextract

from subdomain_takeover_tools.helper.main import bootstrap, settings
from subdomain_takeover_tools.helper.prepare import prepare_domain_name

# once we include additional support we might need to lazy initialize
transip_session = requests.Session()
transip_session.headers['Content-Type'] = 'application/json'
transip_session.headers['Authorization'] = 'Bearer ' + settings['transip']['access_token']

tld_blacklist = [
    '.cn',
    '.gov',
    '.int',
    '.mil',
    '.edu',
    '.aws'
]


def is_valid(domain, cname):
    if cname is None:
        return False

    if not cname_still_valid(domain, cname):
        return False

    return confirm_unclaimed(cname)


def cname_still_valid(domain, cname):
    try:
        answers = dns.resolver.resolve(domain, "CNAME")
        for rdata in answers:
            if rdata.target.to_text(omit_final_dot=True) == cname:
                return True
    except dns.exception.DNSException:
        pass

    return False


def confirm_unclaimed(cname):
    domain_name = _extract_single_domain_name(prepare_domain_name(cname))

    for blacklisted in tld_blacklist:
        if domain_name.endswith(blacklisted):
            return False

    if settings['transip'] is not None:
        return confirm_unclaimed_transip(domain_name)
    else:
        sys.stderr.write("No supported unclaimed configuration is setup, please consult the documentation")


def confirm_unclaimed_transip(domain_name):
    time.sleep(5)
    r = transip_session.get("https://api.transip.nl/v6/domain-availability/" + domain_name)
    data = r.json()
    if 'availability' not in data:
        raise Exception("Request failed: " + r.content.decode())

    return data['availability']['status'] == 'free'


def _extract_single_domain_name(subdomain):
    r = tldextract.extract(subdomain)
    return '.'.join(r[-2:])


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
