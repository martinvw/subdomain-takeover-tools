import requests
from subdomain_takeover_tools.helper.main import bootstrap, settings
from subdomain_takeover_tools.helper.prepare import prepare_domain_name

from subdomain_takeover_tools.helper.prepare import prepare_domain_name


def is_valid(_, cname):
    if cname is None:
        return False

    return prepare_domain_name(cname) == 'cname.agilecrm.com'


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
