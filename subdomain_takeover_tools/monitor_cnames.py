import sys

from subdomain_takeover_tools.authoritative_resolve import query_authoritative, DoesNotExist


def main():
    for line in sys.stdin:
        line = line.strip()
        # Skip blank lines and '#' comments so input files can be annotated
        if not line or line.startswith("#"):
            continue
        (subdomain, target, record_type) = line.split(",")
        validate(subdomain, target, record_type)


def validate(subdomain, target, record_type):
    try:
        result = query_authoritative(subdomain, request_type=record_type)
    except DoesNotExist:
        print("Record '%s' was removed" % subdomain)
        return
    except Exception as e:
        print("Validation of '%s' failed: %s" % (subdomain, e))
        return

    message = check(subdomain, target, record_type, result)
    if message:
        print(message)


def check(subdomain, target, record_type, result):
    """Compare the resolved records against the expected target(s).

    ``target`` may list several expected values separated by ``;``. The check is
    a presence check: it reports drift when a listed target is no longer among
    the resolved records, and ignores any additional records. Returns a message
    string to print, or ``None`` when everything is as expected.
    """
    if not result:
        return "No result for %s" % subdomain

    actual = {_normalize(r, record_type) for r in result}
    expected = {_normalize(t, record_type) for t in target.split(";") if t.strip()}

    missing = expected - actual
    if missing:
        return "Record '%s' was changed, %s no longer present (now points to %s)" % (
            subdomain,
            ", ".join(sorted(missing)),
            ", ".join(sorted(actual)),
        )
    return None


def _normalize(value, record_type):
    """Normalise a record value for comparison.

    DNS is case-insensitive and dnspython emits a trailing dot on hostnames, so
    both are stripped. For MX records the ``str(rr)`` form is ``"<pref> <host>"``;
    only the mail exchange host is compared, the priority is ignored.
    """
    value = value.strip().rstrip(".").lower()
    if record_type.upper() == "MX":
        value = value.split()[-1]
    return value


if __name__ == "__main__":
    main()
