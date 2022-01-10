# Subdomain Takeover Tools

This set of tools helps me in validating the initial outcome of [subtake](https://github.com/jakejarvis/subtake).

## Confirming takeovers

All scripts support the following two parameters:

- `--strict`:  only report as vulnerable if the issue is not also applicable on `hostname.tld` and `www.hostname.tld`.
- `--inverse`: do inverse reporting, so report all subdomains that are not vulnerable

## Confirming S3 

Subtake has some false positives on Google Cloud buckets as S3 buckets, also some access denied's end up in the results.

The script `confirm-s3.py` will make sure that the bucket is actually vulnerable.

```bash
grep "\[s3 bucket: " subtake-output.txt | confirm_s3
```

### Confirming ELB

Some patterns of elb are vulnerable while others are not, to filter them we can use our script:

```bash
grep "\[elasticbeanstalk: " subtake-output.txt | confirm_elb
```

*Note:* the parameter `--strict` is accepted here but will not lead to expected results.


### Confirming Shopify

It seems that 

```bash
grep "\[shopify: " subtake-output.txt | confirm_shopify
```

## Separate tools

### Extracting domain names

As part of my process I want to know the domains involved in my findings.

Example usage:

```bash
< subtake-output.txt | cut -f3 | python3 extract_domain_names.py | sort -u > involved.domains
```
