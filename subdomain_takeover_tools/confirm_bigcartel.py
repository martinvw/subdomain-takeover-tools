from subdomain_takeover_tools.helper.main import bootstrap


def is_valid(_, cname):
    if cname is None:
        return False

    if not cname.endswith('.bigcartel.com'):
        return False

    return cname.count('.') == 2


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
