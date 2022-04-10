import sys

from subdomain_takeover_tools.authoritative_resolve import query_authoritative, DoesNotExist


def main():
    for line in sys.stdin:
        (subdomain, target) = line.strip().split(",")
        validate(subdomain, target)


def validate(subdomain, target):
    try:
        result = query_authoritative(subdomain, request_type='CNAME')
        if len(result) != 1:
            print("No result for %s" % subdomain)
        elif result[0] != target:
            print("Record '%s' was changed, points to %s" % (subdomain, result[0]))
    except DoesNotExist:
        print("Record '%s' was removed" % subdomain)
    except Exception as e:
        print("Validation of '%s' failed: %s" % (subdomain, e))
        return None


if __name__ == "__main__":
    main()
