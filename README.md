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

   Alternatively, you can download or clone this repo and call `pip install -e .`.

## Confirming takeovers

All scripts support the following two parameters:

- `--strict`:  only report as vulnerable if the issue is not also applicable on `hostname.tld` and `www.hostname.tld`.
- `--inverse`: do inverse reporting, so report all subdomains that are not vulnerable

### Supported input formats

In addition to plain hostnames, the scripts accept the output of two scanners and auto-detect which one is used per line:

- [subtake](https://github.com/jakejarvis/subtake): `[service: target]<tab><tab>domain`
- [nuclei](https://github.com/projectdiscovery/nuclei) takeover templates: `[template-id] [protocol] [severity] url ["extracted-cname"]`

For the unified `confirm_takeover` dispatcher, nuclei template ids such as `github-takeover` and `aws-bucket-takeover` are mapped to the matching service validator automatically. Findings for services without a validator are considered *unsupported* and dropped by default. The dispatcher accepts two extra parameters:

- `--full`: output the full input line instead of just the domain.
- `--include-unsupported`: also emit unsupported findings (services with no validator), so a single pass over nuclei output keeps both confirmed-vulnerable and not-yet-disproven findings.

Some scripts require a config file to be present, the location is `.subdomain_takeover_tools.ini`, an example of the file can be found below:

```ini
[azure]
subscription_id=44713cf2-8656-11ec-a8a3-0242ac120002
[github]
username=martinvw
access_token=44713cf2-8656-11ec-a8a3-0242ac120002
repo=44713cf2-8656-11ec-a8a3-0242ac120002
[fastly]
api_token=44713cf2-8656-11ec-a8a3-0242ac120002
service=44713cf2-8656-11ec-a8a3-0242ac120002
version=3
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

Please note that some regions are not enabled by default, when you receive the following error:

> botocore.exceptions.ClientError: An error occurred (InvalidClientTokenId) when calling the CheckDNSAvailability operation: The security token included in the request is invalid.

This could mean you have not yet enabled these, opt-in, regions, see https://console.aws.amazon.com/billing/home?#/account

### Confirming Shopify

It seems that all current shopify examples are vulnerable, the following check just validates the DNS.

```bash
grep "\[shopify: " subtake-output.txt | confirm_shopify
```

### Filtering Pantheon

Please note that for pantheon this repo currently only provides an initial check to eliminate some FALSE positives.

```bash
grep "\[pantheon: " subtake-output.txt | confirm_pantheon
```

### Filtering Cargo Collective

Please note that for Cargo Collective this repo currently only provides an initial check to eliminate some FALSE positives.

```bash
grep "\[cargo: " subtake-output.txt | confirm_cargo
```

### HTTP-fingerprint validators

The following services are validated by fetching the candidate host over HTTP(S) and looking
for the provider's "domain not connected / unclaimed" error page. They need no config or
credentials, and they short-circuit (return not-vulnerable) for the provider's own hostnames,
which filters the bulk of self-referential false positives:

| Command | Service | Fingerprint |
| --- | --- | --- |
| `confirm_framer` | Framer | `Site Not Found \| Framer` |
| `confirm_leadpages` | Leadpages | "This page couldn't be found…" |
| `confirm_meteor` | Meteor / Galaxy | "No applications registered for host" |
| `confirm_surveysparrow` | SurveySparrow | "Account not found." |
| `confirm_greatpages` | GreatPages | "Página não encontrada (Erro 404)" |
| `confirm_wix` | Wix | "Error ConnectYourDomain occurred" |
| `confirm_mashery` | Mashery | "Unrecognized domain" |

```bash
grep "\[framer: " subtake-output.txt | confirm_framer
```

These are also wired into the unified `confirm_takeover` dispatcher via their nuclei template
ids (`framer-takeover`, `leadpages-takeover`, `meteor-takeover`, `surveysparrow-takeover`,
`greatpages-takeover`, `wix-takeover`, `mashery-takeover`).

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
