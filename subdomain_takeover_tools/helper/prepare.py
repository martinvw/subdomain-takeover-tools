import re

import dns.exception
import dns.resolver

cache = {}

# nuclei output looks like:
#   [github-takeover] [http] [high] https://example.com ["example.github.io"]
# where the trailing extracted-results array is optional.
NUCLEI_LINE_RE = re.compile(
    r'^\[(?P<service>[^\]]+)\]\s+\[[^\]]+\]\s+\[[^\]]+\]\s+(?P<url>\S+)(?:\s+\[(?P<extracted>.*)\])?\s*$'
)


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


def is_nuclei_line(line):
    return NUCLEI_LINE_RE.match(line) is not None


def parse_nuclei_line(line):
    match = NUCLEI_LINE_RE.match(line)
    service = match.group('service')
    domain = prepare_domain_name(match.group('url'))

    extracted = match.group('extracted')
    if extracted:
        values = re.findall(r'"([^"]*)"', extracted)
        target = values[0] if values else extracted.strip()
    else:
        target = ''

    return service, target, domain


def process_nuclei_output(is_valid, line, check, inverse, strict):
    (_, target, domain) = parse_nuclei_line(line)
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


def resolve_ips(hostname):
    """Resolve hostname to its final set of IPv4 addresses, following any CNAME
    chain. Returns an empty set when the host does not resolve."""
    try:
        answers = dns.resolver.resolve(hostname, 'A')
        return {str(rdata) for rdata in answers}
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer,
            dns.resolver.NoNameservers, dns.exception.Timeout):
        return set()
