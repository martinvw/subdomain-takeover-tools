from azure.mgmt.trafficmanager import TrafficManagerManagementClient

from subdomain_takeover_tools.helper.credential_wrapper import CredentialWrapper
from subdomain_takeover_tools.helper.main import bootstrap, settings
from subdomain_takeover_tools.helper.prepare import resolve_cname

TRAFFICMANAGER_NET = '.trafficmanager.net'

credential = CredentialWrapper()
tm_client = TrafficManagerManagementClient(credential, settings['azure']['subscription_id'])


def is_valid(hostname, cname):
    if hostname == cname:
        cname = resolve_cname(hostname)

    if cname is None:
        return False

    return confirm_azure_traffic_manager(cname)


def confirm_azure_traffic_manager(cname):
    if TRAFFICMANAGER_NET in cname:
        dns_prefix = cname.replace(TRAFFICMANAGER_NET, '')
        result = tm_client.profiles.check_traffic_manager_relative_dns_name_availability(
            dns_prefix,
            "microsoft.network/trafficmanagerprofiles"
        )
        return result.name_available
    return False


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
