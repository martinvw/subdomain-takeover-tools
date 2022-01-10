import boto3

from subdomain_takeover_tools.helper.main import bootstrap


def is_valid(_, cname):
    if cname is None:
        return False

    if cname.count('.') == 3:
        (prefix, region, _, _) = cname.split('.')

        client = boto3.client('elasticbeanstalk', region_name=region)
        result = client.check_dns_availability(CNAMEPrefix=prefix)

        if result['Available']:
            return True

    return False


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()