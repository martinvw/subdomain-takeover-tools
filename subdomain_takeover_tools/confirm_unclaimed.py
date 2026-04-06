import functools
import sys
import time
from typing import Optional

import dns
import requests
from tldextract import tldextract

from subdomain_takeover_tools.helper.main import bootstrap, settings
from subdomain_takeover_tools.helper.prepare import prepare_domain_name, get_cached, store_cache

tld_blacklist = [
    '.cn',
    '.gov',
    '.int',
    '.mil',
    '.edu',
    '.aws',
    '.lb'  # only third level is allowed
]


def is_valid(domain: str, cname: Optional[str]) -> Optional[bool]:
    if cname is None:
        return False

    if not cname_still_valid(domain, cname):
        return False

    return confirm_unclaimed(cname)


def cname_still_valid(domain: str, cname: str) -> bool:
    try:
        answers = dns.resolver.resolve(domain, "CNAME")
        for rdata in answers:
            if rdata.target.to_text(omit_final_dot=True) == cname:
                return True
    except dns.exception.DNSException:
        pass

    return False


def confirm_unclaimed(cname: str) -> Optional[bool]:
    domain_name = _extract_single_domain_name(prepare_domain_name(cname))

    cached = get_cached('unclaimed', domain_name)
    if cached is not None:
        return cached

    return store_cache('unclaimed', domain_name, confirm_uncached(domain_name))


def confirm_uncached(domain_name: str) -> Optional[bool]:
    for blacklisted in tld_blacklist:
        if domain_name.endswith(blacklisted):
            return False
    if settings['transip'] is not None:
        return confirm_unclaimed_transip(domain_name)
    else:
        sys.stderr.write("No supported unclaimed configuration is setup, please consult the documentation")
        return None


@functools.lru_cache(maxsize=None)
def _get_transip_session() -> requests.Session:
    session = requests.Session()
    session.headers['Content-Type'] = 'application/json'
    session.headers['Authorization'] = f"Bearer {settings['transip']['access_token']}"
    return session


def confirm_unclaimed_transip(domain_name: str) -> bool:
    time.sleep(5)
    r = _get_transip_session().get(f"https://api.transip.nl/v6/domain-availability/{domain_name}")
    data = r.json()
    if 'availability' not in data:
        raise Exception("Request failed: " + r.content.decode())

    return data['availability']['status'] == 'free'


def _extract_single_domain_name(subdomain: str) -> str:
    return tldextract.extract(subdomain).registered_domain


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
