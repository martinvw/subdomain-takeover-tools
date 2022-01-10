import requests
import boto3
from botocore.exceptions import ClientError

from helper.main import main


def is_valid(name, _):
    try:
        s3 = boto3.resource('s3')
        s3.meta.client.head_bucket(Bucket=name)
        return False
    except ClientError as e:
        response_code = e.response['Error']['Code']
        if '404' == response_code:
            return confirm_s3(name)
        elif '403' == response_code:
            return False


def confirm_s3(name):
    try:
        r = requests.head("http://" + name)
        if 'x-amz-error-detail-BucketName' in r.headers:
            return True

        r = requests.get("http://" + name)
        return '<BucketName>' in r.text or 'BucketName: ' in r.text or '"BucketName"' in r.text
    except requests.exceptions.ConnectionError:
        return False


if __name__ == "__main__":
    main(is_valid)
