import boto3

from subdomain_takeover_tools.helper.main import bootstrap
from subdomain_takeover_tools.helper.prepare import prepare_domain_name


def is_valid(_, cname):
    if cname is None:
        return False

    return confirm_elb(cname)


def confirm_elb(cname):
    cname = prepare_domain_name(cname)

    if cname.count('.') == 3:
        (prefix, region, _, _) = cname.split('.')
        # Invalid length for parameter CNAMEPrefix, value: 3, valid min length: 4
        if len(prefix) < 4:
            return False

        client = boto3.client('elasticbeanstalk', region_name=region)
        result = client.check_dns_availability(CNAMEPrefix=prefix)

        if result['Available']:
            return True
    return False


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
