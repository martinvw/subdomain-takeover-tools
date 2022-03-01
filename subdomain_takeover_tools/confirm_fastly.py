import requests

from subdomain_takeover_tools.helper.main import bootstrap, settings
from subdomain_takeover_tools.helper.prepare import prepare_domain_name

session = requests.Session()
session.headers['Fastly-Key'] = settings['fastly']['api_token']
url = "https://api.fastly.com/service/%s/version/%s/domain" % (
    settings['fastly']['service'], settings['fastly']['version']
)


def is_valid(domain, _):
    if domain is None:
        return False

    return confirm_fastly(domain)


def confirm_fastly(domain):
    setup_response = session.post(url, data={'name': domain})
    session.delete(url + '/' + prepare_domain_name(domain))
    return setup_response.status_code == 200


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
