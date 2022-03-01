import sys

import dns.query
import dns.resolver


def _query_authoritative_ns(domain, log=lambda msg: None):
    default = dns.resolver.get_default_resolver()
    nameserver = default.nameservers[0]

    domain_parts = domain.split('.')
    result = None

    for i in range(len(domain_parts), 0, -1):
        sub = '.'.join(domain_parts[i - 1:])

        log('Looking up %s on %s' % (sub, nameserver))
        query = dns.message.make_query(sub, rdtype=dns.rdatatype.NS)
        response = dns.query.udp(query, nameserver, timeout=30)

        rcode = response.rcode()
        if rcode == dns.rcode.NOERROR:
            pass
        elif rcode == dns.rcode.NXDOMAIN:
            if i < len(domain_parts) - 1 and i != 1:
                sys.stderr.write(sub + " does not exist, skipping\n")
                continue
            else:
                raise Exception('%s does not exist.' % sub)
        else:
            raise Exception('Error %s' % (dns.rcode.to_text(rcode)))

        if len(response.authority) > 0:
            rrsets = response.authority
        elif len(response.additional) > 0:
            rrsets = [response.additional]
        else:
            rrsets = response.answer

        # Handle all RRsets, not just the first one
        for rrset in rrsets:
            for rr in rrset:
                if rr.rdtype == dns.rdatatype.SOA:
                    log('Same server is authoritative for %s' % sub)
                elif rr.rdtype == dns.rdatatype.A:
                    nameserver = list(rr.items)[0].address
                    log('Glue record for %s: %s' % (rr.name, nameserver))
                elif rr.rdtype == dns.rdatatype.NS:
                    authority = rr.target
                    nameserver = default.resolve(authority).rrset[0].to_text()
                    log('%s [%s] is authoritative for %s; ttl %i' %
                        (authority, nameserver, sub, rrset.ttl))
                    result = rrset
                else:
                    # IPv6 glue records etc
                    # log('Ignoring %s' % (rr))
                    pass

    return result


def query_authoritative(domain, request_type='A', log=lambda msg: None):
    authority = _query_authoritative_ns(domain, log)

    default = dns.resolver.get_default_resolver()
    nameserver = default.resolve(authority[0].target).rrset[0].to_text()
    query = dns.message.make_query(domain, request_type)
    query_result = dns.query.udp(query, nameserver, timeout=30)

    result = []
    if query_result.answer:
        for rrset in query_result.answer:
            for rr in rrset:
                result.append(str(rr))

    return result


def verbose(msg):
    sys.stderr.write(msg + u'\n')


def main():
    for s in sys.argv[1:]:
        r = query_authoritative(s, 'A', verbose)
        print()
        print('Authoritative answer:', r)


if __name__ == "__main__":
    main()
