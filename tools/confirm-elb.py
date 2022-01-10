import boto3

from helper.main import main


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


if __name__ == "__main__":
    main(is_valid)
