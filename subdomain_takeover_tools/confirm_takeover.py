import re
import sys
from typing import Callable, Optional

from subdomain_takeover_tools.confirm_agile_crm import is_valid as agile_crm_is_valid
from subdomain_takeover_tools.confirm_azure_api_management import is_valid as azure_api_management_is_valid
from subdomain_takeover_tools.confirm_azure_app_service import is_valid as azure_app_service_is_valid
from subdomain_takeover_tools.confirm_azure_edge_cdn import is_valid as azure_edge_cdn_is_valid
from subdomain_takeover_tools.confirm_azure_front_door import is_valid as azure_front_door_is_valid
from subdomain_takeover_tools.confirm_azure_traffic_manager import is_valid as azure_traffic_manager_is_valid
from subdomain_takeover_tools.confirm_bigcartel import is_valid as bigcartel_is_valid
from subdomain_takeover_tools.confirm_cargo import is_valid as cargo_is_valid
from subdomain_takeover_tools.confirm_elb import is_valid as elb_is_valid
from subdomain_takeover_tools.confirm_fastly import is_valid as fastly_is_valid
from subdomain_takeover_tools.confirm_framer import is_valid as framer_is_valid
from subdomain_takeover_tools.confirm_github import is_valid as github_is_valid
from subdomain_takeover_tools.confirm_godaddy import is_valid as godaddy_is_valid
from subdomain_takeover_tools.confirm_greatpages import is_valid as greatpages_is_valid
from subdomain_takeover_tools.confirm_leadpages import is_valid as leadpages_is_valid
from subdomain_takeover_tools.confirm_mashery import is_valid as mashery_is_valid
from subdomain_takeover_tools.confirm_meteor import is_valid as meteor_is_valid
from subdomain_takeover_tools.confirm_multiscreensite import is_valid as multiscreensite_is_valid
from subdomain_takeover_tools.confirm_pantheon import is_valid as pantheon_is_valid
from subdomain_takeover_tools.confirm_s3 import is_valid as s3_is_valid
from subdomain_takeover_tools.confirm_shopify import is_valid as shopify_is_valid
from subdomain_takeover_tools.confirm_surge import is_valid as surge_is_valid
from subdomain_takeover_tools.confirm_surveysparrow import is_valid as surveysparrow_is_valid
from subdomain_takeover_tools.confirm_wix import is_valid as wix_is_valid
from subdomain_takeover_tools.confirm_tumblr import is_valid as tumblr_is_valid
from subdomain_takeover_tools.confirm_unclaimed import is_valid as unclaimed_is_valid
from subdomain_takeover_tools.helper.prepare import get_cached, store_cache, is_nuclei_line, parse_nuclei_line

cacheable = ["azure", "elasticbeanstalk"]

# Maps a nuclei takeover template id (the value shown in the [..] tag of nuclei
# output) to the internal service name used as a key in VALIDATORS. Derived from
# the projectdiscovery/nuclei-templates repo (http/takeovers/ and dns/), checked
# 2026-06-06. Only templates with a matching validator are listed; everything
# else falls through to "unsupported".
NUCLEI_SERVICE_MAP: dict[str, str] = {
    'agilecrm-takeover': 'agilecrm',
    'azure-takeover-detection': 'azure',
    'bigcartel-takeover': 'bigcartel',
    'cargo-takeover': 'cargo',
    'cargocollective-takeover': 'cargo',
    'elasticbeanstalk-takeover': 'elasticbeanstalk',
    'framer-takeover': 'framer',
    'github-takeover': 'github',
    'greatpages-takeover': 'greatpages',
    'leadpages-takeover': 'leadpages',
    'mashery-takeover': 'mashery',
    'meteor-takeover': 'meteor',
    'pantheon-takeover': 'pantheon',
    'aws-bucket-takeover': 's3 bucket',
    'surge-takeover': 'surge',
    'surveysparrow-takeover': 'surveysparrow',
    'wix-takeover': 'wix',
}


def _azure_is_valid(domain: str, target: str) -> Optional[bool]:
    if target.endswith('.azurewebsites.net'):
        return azure_app_service_is_valid(domain, target)
    elif target.endswith('.azureedge.net'):
        return azure_edge_cdn_is_valid(domain, target)
    elif target.endswith('.trafficmanager.net'):
        return azure_traffic_manager_is_valid(domain, target)
    elif target.endswith('.azure-api.net'):
        return azure_api_management_is_valid(domain, target)
    elif target.endswith('.azurefd.net'):
        return azure_front_door_is_valid(domain, target)
    elif target.endswith('.cloudapp.azure.com'):
        # for now, we assume cloudapp is vulnerable
        return True
    # other Azure services are not yet supported
    elif target.endswith('.blob.core.windows.net') or target.endswith('.azurehdinsight.net') or target.endswith(
            '.azurecontainer.io') or target.endswith('.database.windows.net') or target.endswith(
        '.azurecr.io') or target.endswith('.servicebus.windows.net') or target.endswith(
        '.visualstudio.com') or target.endswith('.search.windows.net') or target.endswith(
        '.azuredatalakestore.net') or target.endswith('.azuredatalakestore.net'):
        return None
    else:
        # this is really unsupported and most likely a false positive
        return False


VALIDATORS: dict[str, Callable[[str, str], Optional[bool]]] = {
    'agilecrm': agile_crm_is_valid,
    'azure': _azure_is_valid,
    'bigcartel': bigcartel_is_valid,
    'cargo': cargo_is_valid,
    'GoDaddy': godaddy_is_valid,
    'elasticbeanstalk': elb_is_valid,
    'fastly': fastly_is_valid,
    'framer': framer_is_valid,
    'github': github_is_valid,
    'greatpages': greatpages_is_valid,
    'leadpages': leadpages_is_valid,
    'mashery': mashery_is_valid,
    'meteor': meteor_is_valid,
    'multiscreensite': multiscreensite_is_valid,
    'pantheon': pantheon_is_valid,
    's3 bucket': s3_is_valid,
    'shopify': shopify_is_valid,
    'surge': surge_is_valid,
    'surveysparrow': surveysparrow_is_valid,
    'tumblr': tumblr_is_valid,
    'unclaimed': unclaimed_is_valid,
    'wix': wix_is_valid,
}


def main():
    inverse = '--inverse' in sys.argv
    strict = '--strict' in sys.argv
    full = '--full' in sys.argv
    include_unsupported = '--include-unsupported' in sys.argv

    data = sys.stdin.read()

    lines = data.strip().split('\n')
    for line in lines:
        if not line.strip():
            continue
        if is_nuclei_line(line):
            (service, target, domain) = parse_nuclei_line(line)
            service = _normalize_nuclei_service(service)
        elif ']\t\t' in line or ']   ' in line:
            (service, target, domain) = _process_line(line)
        else:
            raise IOError("Unexpected input received, only subtake and nuclei output are supported")

        result = _process_subtake_output(service, target, domain, inverse)

        # result is None only when the service is unsupported (no validator);
        # --include-unsupported surfaces those instead of dropping them.
        if result or (result is None and include_unsupported):
            if full:
                print(line)
            else:
                print(domain)


def _process_line(line: str) -> tuple:
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


def _normalize_nuclei_service(template_id: str) -> str:
    return NUCLEI_SERVICE_MAP.get(template_id, template_id)


def _process_subtake_output(service: str, target: str, domain: str, inverse: bool) -> Optional[bool]:
    result = _perform_check(service, target, domain)

    if result is None:
        return None

    # xor
    return inverse != result


def _perform_check(service: str, target: str, domain: str) -> Optional[bool]:
    if service in cacheable:
        cached = get_cached(service, target)
        if cached is not None:
            return cached

    fresh_result = perform_uncached(domain, service, target)
    if service in cacheable and fresh_result is not None:
        store_cache(service, target, fresh_result)
    return fresh_result


def perform_uncached(domain: str, service: str, target: str) -> Optional[bool]:
    validator = VALIDATORS.get(service)
    if validator is None:
        return None
    return validator(domain, target)


if __name__ == "__main__":
    main()
