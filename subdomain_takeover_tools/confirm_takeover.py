import re
import sys

from subdomain_takeover_tools.confirm_agile_crm import is_valid as agile_crm_is_valid
from subdomain_takeover_tools.confirm_azure_app_service import is_valid as azure_app_service_is_valid
from subdomain_takeover_tools.confirm_azure_edge_cdn import is_valid as azure_edge_cdn_is_valid
from subdomain_takeover_tools.confirm_azure_traffic_manager import is_valid as azure_traffic_manager_is_valid
from subdomain_takeover_tools.confirm_azure_api_management import is_valid as azure_api_managment_is_valid
from subdomain_takeover_tools.confirm_bigcartel import is_valid as bigcartel_is_valid
from subdomain_takeover_tools.confirm_cargo import is_valid as cargo_is_valid
from subdomain_takeover_tools.confirm_elb import is_valid as elb_is_valid
from subdomain_takeover_tools.confirm_fastly import is_valid as fastly_is_valid
from subdomain_takeover_tools.confirm_github import is_valid as github_is_valid
from subdomain_takeover_tools.confirm_pantheon import is_valid as pantheon_is_valid
from subdomain_takeover_tools.confirm_s3 import is_valid as s3_is_valid
from subdomain_takeover_tools.confirm_shopify import is_valid as shopify_is_valid
from subdomain_takeover_tools.confirm_surge import is_valid as surge_is_valid
from subdomain_takeover_tools.confirm_tumblr import is_valid as tumblr_is_valid
from subdomain_takeover_tools.confirm_unclaimed import is_valid as unclaimed_is_valid
from subdomain_takeover_tools.helper.prepare import get_cached, store_cache

cacheable = ["azure", "elasticbeanstalk"]


def main():
    inverse = '--inverse' in sys.argv
    strict = '--strict' in sys.argv
    full = '--full' in sys.argv

    data = sys.stdin.read()

    lines = data.strip().split('\n')
    for line in lines:
        if not line.strip():
            continue
        elif ']\t\t' not in line and '.]   ' not in line:
            raise IOError("Unexpected input s received, currently only subtake output is supported")

        (service, target, domain) = _process_line(line)

        result = _process_subtake_output(service, target, domain, inverse)

        if result:
            if full:
                print(line)
            else:
                print(domain)


def _process_line(line):
    if '\t\t' in line:
        (parts, domain) = line.split('\t\t')
    else:
        (parts, domain) = re.split(r'  +', line)
    if ': ]' in parts:
        service = parts[1:-3]
        target = ''
    else:
        (service, target) = parts[1:-2].split(': ')

    return service, target, domain


def _process_subtake_output(service, target, domain, inverse):
    result = _perform_check(service, target, domain)

    if result is None:
        return

    # xor
    return inverse != result


def _perform_check(service, target, domain):
    if service in cacheable:
        cached = get_cached(service, target)
        if cached is not None:
            return cached

    fresh_result = perform_uncached(domain, service, target)
    if service in cacheable and fresh_result is not None:
        store_cache(service, target, fresh_result)
    return fresh_result


def perform_uncached(domain, service, target):
    if service == 'agilecrm':
        return agile_crm_is_valid(domain, target)
    elif service == 'azure':
        if target.endswith('azurewebsites.net'):
            return azure_app_service_is_valid(domain, target)
        elif target.endswith('azureedge.net'):
            return azure_edge_cdn_is_valid(domain, target)
        elif target.endswith('trafficmanager.net'):
            return azure_traffic_manager_is_valid(domain, target)
        elif target.endswith('azure-api.net'):
            return azure_api_managment_is_valid(domain, target)
        elif target.endswith('cloudapp.azure.com'):
            # for now, we assume cloudapp is vulnerable
            return True
        else:
            # other Azure services are not yet supported
            return None
    elif service == 'bigcartel':
        return bigcartel_is_valid(domain, target)
    elif service == 'cargo':
        return cargo_is_valid(domain, target)
    elif service == 'elasticbeanstalk':
        return elb_is_valid(domain, target)
    elif service == 'fastly':
        return fastly_is_valid(domain, target)
    elif service == 'github':
        return github_is_valid(domain, target)
    elif service == 'pantheon':
        return pantheon_is_valid(domain, target)
    elif service == 's3 bucket':
        return s3_is_valid(domain, target)
    elif service == 'shopify':
        return shopify_is_valid(domain, target)
    elif service == 'surge':
        return surge_is_valid(domain, target)
    elif service == 'tumblr':
        return tumblr_is_valid(domain, target)
    elif service == 'unclaimed':
        return unclaimed_is_valid(domain, target)
    else:
        return None


if __name__ == "__main__":
    main()
