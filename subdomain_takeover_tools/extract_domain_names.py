import sys
import tldextract
import re


def main():
    for line in sys.stdin:
        sys.stdout.write(extract_domain_name(line) + '\n')


def extract_domain_name(subdomain):
    if "(" in subdomain:
        return _handle_pattern(subdomain)
    else:
        return _extract_single_domain_name(subdomain)


def _handle_pattern(subdomain):
    end_result = ''
    result = re.search(r'^(.*)\(([a-z.|]+)\)', subdomain)
    prefix = result.group(1)
    postfixes = result.group(2).split('|')
    for postfix in postfixes:
        end_result = end_result + _extract_single_domain_name(prefix + postfix) + '\n'

    return end_result.strip()


def _extract_single_domain_name(subdomain):
    r = tldextract.extract(subdomain)
    return '.'.join(r[-2:])


if __name__ == "__main__":
    main()
