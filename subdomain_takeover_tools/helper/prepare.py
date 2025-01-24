import re

import dns.resolver

cache = {}


def prepare_domain_name(host_in):
    host = re.sub(r'https?://', '', host_in)
    host = re.sub(r'/.*$', '', host)
    host = re.sub(r'\.$', '', host)
    return host


def get_cached(cname, target):
    key = (cname, target)
    if key in cache:
        return cache[key]
    else:
        return None


def store_cache(cname, target, result):
    if result is None:
        return None

    key = (cname, target)
    cache[key] = result

    return result


def process_subtake_output(is_valid, line, check, inverse, strict):
    (parts, domain) = line.split('\t\t')
    if ': ]' in parts:
        target = ''
    else:
        (_, target) = parts[1:-2].split(': ')
    check(is_valid, domain, target, inverse, strict)


def resolve_cname(hostname):
    try:
        cnames = dns.resolver.resolve(hostname, 'CNAME')

        if len(cnames) == 0:
            raise ResourceWarning("CNAME not found")
        else:
            return prepare_domain_name(str(cnames[0]))
    except dns.resolver.NXDOMAIN:
        return None
