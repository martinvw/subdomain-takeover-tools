import sys

from subdomain_takeover_tools.authoritative_resolve import query_authoritative
from subdomain_takeover_tools.extract_domain_names import extract_domain_name

_header = ['service', 'target', 'subdomain', 'domain', 'tld', 'wildcard', 'Still valid', 'Validated',
           'Authoritative resolve', 'Service Label']
_pre_validated = ['azure-app-services', 'azure-trafficmanager', 'azure-ip', 'azure-edge', 'bigcartel', 'fastly',
                  'agilecrm', 'elasticbeanstalk', 's3 bucket', 'shopify', 'tumblr', 'unclaimed', "github"]


def main():
    sys.stdout.write(print_as(_header) + '\n')
    for line in sys.stdin:
        sys.stdout.write(print_as(enrich(line)) + '\n')


def print_as(param):
    return ','.join(param)


def has_wildcard(original, original_resolved):
    wildcard = "iughxdfdfguh." + '.'.join(original.split('.')[1:])
    random_resolved = resolve(wildcard)
    return _compare(original_resolved, random_resolved)


def resolve(original):
    try:
        return query_authoritative(original)
    except Exception:
        return None


def enrich(line):
    (service, target, subdomain) = _split_line(line)
    authoritative_result = resolve(subdomain)
    wildcard = has_wildcard(subdomain, authoritative_result)
    active = still_active(authoritative_result, target)
    service = _narrow_down_service(service, target)
    is_validated = _is_validated(service)

    return [
        service,
        target[:-1],
        subdomain,
        extract_domain_name(subdomain),
        subdomain.split('.')[-1],
        str(wildcard),
        str(active),
        is_validated,
        print_authoritative_result(authoritative_result)
    ]


def print_authoritative_result(authoritative_result):
    if authoritative_result is None:
        return "-"

    return '"' + ";".join(authoritative_result) + '"'


def still_active(authoritative_result, target):
    if authoritative_result is None:
        return None

    return target in authoritative_result


def _is_validated(service):
    if service in _pre_validated:
        return 'TRUE'
    else:
        return ''


def _split_line(line):
    (parts, subdomain) = line.strip().split('\t\t')
    (service, target) = parts[1:-1].split(': ')
    return [service, target, subdomain]


def _narrow_down_service(service, target):
    if target.endswith('.azurewebsites.net.'):
        return 'azure-app-services'
    elif target.endswith('.azureedge.net.'):
        return 'azure-edge'
    elif target.endswith('.cloudapp.azure.com.'):
        return 'azure-ip'
    elif target.endswith('.blob.core.windows.net.'):
        return 'azure-blob-storage'
    elif target.endswith('.azure-api.net.'):
        return 'azure-API'
    elif target.endswith('.trafficmanager.net.'):
        return 'azure-trafficmanager'
    else:
        return service


def _compare(original_resolved, random_resolved):
    if original_resolved is None or random_resolved is None:
        return False

    return _first_result(random_resolved) == _first_result(original_resolved)


def _first_result(resolved):
    if len(resolved) == 0:
        return None

    result_list = []
    for res in resolved:
        result_list.append(str(res))

    result_list.sort()

    return result_list[0]


if __name__ == "__main__":
    main()
