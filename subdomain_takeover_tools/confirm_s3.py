import boto3
import requests
from botocore.exceptions import ClientError
from typing import Optional

from subdomain_takeover_tools.helper.main import bootstrap


def is_valid(name: str, _: Optional[str]) -> Optional[bool]:
    return confirm_s3(name)


def confirm_s3(name: str) -> bool:
    if name.endswith('.amazonaws.com'):
        return False

    try:
        s3 = boto3.resource('s3')
        s3.meta.client.head_bucket(Bucket=name)
        return False
    except ClientError as e:
        response_code = e.response['Error']['Code']
        if '404' == response_code:
            return _confirm_http_response(name)
        elif '403' == response_code:
            return False
    return False


def _confirm_http_response(name):
    try:
        r = requests.head("http://" + name, timeout=30)
        if 'x-amz-error-detail-BucketName' in r.headers and r.headers['x-amz-error-detail-BucketName'].upper() == name:
            return True

        # S3-compatible but not vulnerable services
        if r.headers.get('Server', '').upper() in ('OBS', 'TENGINE'):
            return False

        r = requests.get("http://" + name, timeout=30)
        if '<BucketName>' not in r.text and 'BucketName: ' not in r.text and '"BucketName"' not in r.text:
            return False

        return name in r.text
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        return False


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
