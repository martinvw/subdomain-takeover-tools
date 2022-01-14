import sys
import tldextract


def main():
    for line in sys.stdin:
        sys.stdout.write(extract_domain_name(line) + '\n')


def extract_domain_name(subdomain):
    r = tldextract.extract(subdomain)
    return '.'.join(r[-2:])


if __name__ == "__main__":
    main()
