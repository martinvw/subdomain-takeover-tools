import dns.resolver

from subdomain_takeover_tools.helper.main import bootstrap
from subdomain_takeover_tools.helper.prepare import resolve_cname


def is_valid(hostname, cname):
    if hostname == cname:
        cname = resolve_cname(hostname)

    if cname is None:
        return False

    if cname.count('.') == 2:
        try:
            dns.resolver.resolve('asuid.' + hostname, 'TXT')
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return True

    return False


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
