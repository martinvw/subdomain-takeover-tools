# Subdomain Takeover Tools

[![Latest Package version](https://badge.fury.io/py/subdomain-takeover-tools.svg)](https://badge.fury.io/py/subdomain-takeover-tools)
[![Build status](https://img.shields.io/pypi/status/subdomain_takeover_tools.svg?maxAge=2592000)](https://pypi.python.org/pypi/subdomain_takeover_tools)
[![Supported versions](https://img.shields.io/pypi/pyversions/subdomain_takeover_tools.svg?maxAge=2592000)](https://pypi.python.org/pypi/subdomain_takeover_tools)

A set of tools to validate the initial outcome of [subtake](https://github.com/jakejarvis/subtake).

## Installation

1. Install using pip:

   ``pip install subdomain_takeover_tools``

   for windows:

   ``py -m pip install subdomain_takeover_tools``

   Alternatively, you can download or clone this repo and call ``pip install -e .``.

## Confirming takeovers

All scripts support the following two parameters:

- `--strict`:  only report as vulnerable if the issue is not also applicable on `hostname.tld` and `www.hostname.tld`.
- `--inverse`: do inverse reporting, so report all subdomains that are not vulnerable

Some scripts require a config file to be present, the location is `.subdomain_takeover_tools.ini`, an example of the file can be found below:

```ini
[azure]
subscription_id=44713cf2-8656-11ec-a8a3-0242ac120002
```

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
cut -f3 < subtake-output.txt | extract_domain_names | sort -u > involved.domains
```

Note that `extract_domain_names` also support groups, such as `domain.(co.id|in.th|ph|vn)`, this will be expanded automatically.

### Resolving from the authoritative DNS authority

For validation of the results I want to validate whether the DNS record is still accurate.

To do this we fetch the authoritative result's step by step from the authoritative DNS servers.

```bash
authoritative_resolve "github.com" "martinvw.nl"
```

### Exporting and enriching

The `subtake_enrich_and_export` will split the existing output and add some additional columms:

- has a wildcard
- domain name
- tld
- still vulnerable
- authoritative results

```bash
subtake_enrich_and_export < subtakee-output.txt
```
