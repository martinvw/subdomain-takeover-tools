import sys

import requests
from helper.prepare import prepare_domain_name, process_subtake_output
import tldextract


def main(is_valid):
    inverse = '--inverse' in sys.argv
    strict = '--strict' in sys.argv

    data = sys.stdin.read()

    lines = data.strip().split('\n')
    for line in lines:
        if ']\t\t' in line:
            process_subtake_output(is_valid, line, check, inverse, strict)
        else:
            host = prepare_domain_name(line)
            check(is_valid, host, host, inverse, strict)


def check(is_valid, domain, cname, inverse, strict):
    result = is_valid(domain, cname)

    if result and strict:
        r = tldextract.extract(domain)
        host = '.'.join(r[-2:])

        host_result = True

        if host != domain:
            try:
                valid = is_valid(host, None)
                # print("Checked '%s', result: %s" % (host, valid))
                host_result = host_result and valid
            except requests.exceptions.ConnectionError:
                pass

        if 'www.' + host != domain:
            try:
                valid_www = is_valid('www.' + host, None)
                # print("Checked 'www.%s', result: %s" % (host, valid_www))
                host_result = host_result and valid_www
            except requests.exceptions.ConnectionError:
                pass

        result = result and not host_result

    # xor
    if inverse != result:
        print(domain)
