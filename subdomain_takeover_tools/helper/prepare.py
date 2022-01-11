import re

import dns.resolver


def prepare_domain_name(host_in):
    host = re.sub(r'https?://', '', host_in)
    host = re.sub(r'/.*$', '', host)
    host = re.sub(r'\.$', '', host)
    return host


def process_subtake_output(is_valid, line, check, inverse, strict):
    (parts, domain) = line.split('\t\t')
    if ': ]' in parts:
        target = ''
    else:
        (_, target) = parts[1:-2].split(': ')
    check(is_valid, domain, target, inverse, strict)


def resolve_cname(hostname):
    cnames = dns.resolver.resolve(hostname, 'CNAME')

    if len(cnames) == 0:
        raise ResourceWarning("CNAME not found")
    else:
        return prepare_domain_name(str(cnames[0]))
