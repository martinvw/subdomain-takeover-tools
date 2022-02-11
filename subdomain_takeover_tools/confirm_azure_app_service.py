import dns.resolver

from subdomain_takeover_tools.helper.main import bootstrap
from subdomain_takeover_tools.helper.prepare import resolve_cname, prepare_domain_name


def is_valid(hostname, cname):
    if hostname == cname:
        cname = resolve_cname(hostname)

    if cname is None:
        return False

    return confirm_azure_app_service(cname, hostname)


def confirm_azure_app_service(cname, hostname):
    cname = prepare_domain_name(cname)

    if cname.count('.') == 2:
        try:
            dns.resolver.resolve('asuid.' + hostname, 'TXT')
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout):
            return True
    return False


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
