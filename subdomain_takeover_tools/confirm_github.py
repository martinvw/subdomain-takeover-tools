import requests

from subdomain_takeover_tools.helper.main import bootstrap, settings
from subdomain_takeover_tools.helper.prepare import prepare_domain_name

session = requests.Session()
session.auth = (settings['github']['username'], settings['github']['access_token'])
url = "https://api.github.com/repos/%s/%s/pages" % (settings['github']['username'], settings['github']['repo'])


def is_valid(domain, _):
    if domain is None:
        return False

    return confirm_github(domain)


def confirm_github(domain):
    if domain.endswith('.github.com') or domain.endswith('.github.io') or domain.endswith('.githubapp.com'):
        return False

    domain = prepare_domain_name(domain)

    configure_cname_response = session.put(url, json={'cname': domain})
    session.put(url, json={'cname': None})
    return configure_cname_response.status_code == 204


def main():
    session.post(url, json={
        'source': {
            'branch': 'main',
            'path': '/'
        }
    })

    bootstrap(is_valid)


if __name__ == "__main__":
    main()
