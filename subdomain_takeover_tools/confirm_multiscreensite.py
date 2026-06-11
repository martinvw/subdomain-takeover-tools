from typing import Optional

from subdomain_takeover_tools.helper.http_fingerprint import fetch_body
from subdomain_takeover_tools.helper.main import bootstrap
from subdomain_takeover_tools.helper.prepare import resolve_ips

# Duda (multiscreensite) serves this on a host that points at the platform but has
# no published site claiming it.
FINGERPRINT = "This site is not published or does not have a domain assigned to it."

EXCLUDE = ('.multiscreensite.com',)


def is_valid(hostname: str, _: Optional[str]) -> Optional[bool]:
    if hostname.endswith(EXCLUDE):
        return False

    (_status, body) = fetch_body(hostname)
    if body is None or FINGERPRINT not in body:
        return False

    # The non-www host shows the "not published" page, so it looks vulnerable. But a
    # published www variant on the same host means the domain is already claimed in a
    # Duda account, which protects the bare host too -> false positive.
    if hostname.startswith('www.'):
        return True

    www = 'www.' + hostname

    www_ips = resolve_ips(www)
    if not www_ips:
        # No www to protect the bare host.
        return True

    host_ips = resolve_ips(hostname)
    if www_ips.isdisjoint(host_ips):
        # www points somewhere else, so it doesn't claim this host.
        return True

    (_www_status, www_body) = fetch_body(www)
    if www_body is not None and FINGERPRINT not in www_body:
        # www serves a published site on the same host -> domain is claimed.
        return False

    return True


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
