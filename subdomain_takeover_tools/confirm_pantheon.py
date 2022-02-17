from subdomain_takeover_tools.helper.main import bootstrap
from subdomain_takeover_tools.helper.prepare import prepare_domain_name


def is_valid(_, cname):
    if cname is None:
        return False

    return confirm_pantheon(cname)


def confirm_pantheon(cname):
    cname = prepare_domain_name(cname)

    if _check_postfix(cname) and cname.count('.') == 2:
        (prefix, _, _) = cname.split('.')

        return prefix.startswith('dev-') or prefix.startswith('test-') or prefix.startswith(
            'test2-') or prefix.startswith('live-') or prefix.startswith('stage-') or prefix.startswith('pre-live-')
    return False


def _check_postfix(cname):
    return cname.endswith('getpantheon.com') or cname.endswith('gotpantheon.com') or cname.endswith('pantheonsite.io')


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
