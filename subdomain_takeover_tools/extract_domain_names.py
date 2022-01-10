import sys
import tldextract


def process():
    for line in sys.stdin:
        r = tldextract.extract(line)
        sys.stdout.write('.'.join(r[-2:]) + '\n')


if __name__ == "__main__":
    process()
