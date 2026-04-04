# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

A Python CLI toolkit that validates potential subdomain takeover findings from [subtake](https://github.com/jakejarvis/subtake). Each `confirm_*.py` module handles one service (S3, ELB, Shopify, GitHub Pages, Fastly, Azure variants, etc.) and exposes a `is_valid(domain, cname) -> bool` function plus a `main()` entry point.

## Commands

```bash
# Install in development mode
pip install -e .

# Install with dev extras (includes `bump` for version bumping)
pip install -e ".[dev]"

# Run tests
python -m pytest tests/

# Run a single test
python -m pytest tests/test_extract_domain_names.py::Test::test_extract_domain_name

# Publish to PyPI (also tags and bumps version)
python setup.py publish
```

## Architecture

### Core pattern

Every `confirm_*.py` module follows the same contract:
- `is_valid(domain, cname) -> bool | None` — returns `True` if vulnerable, `False` if not, `None` if unsupported
- `main()` — calls `bootstrap(is_valid)` from `helper/main.py`

`helper/main.py:bootstrap()` reads stdin, detects whether input is raw hostnames or subtake-format output (`[service: target]\t\tdomain`), and calls the module's `is_valid` function. It also handles `--strict` (re-check on apex + www) and `--inverse` (flip output) flags.

`helper/prepare.py` provides shared DNS utilities and the subtake output parser.

### `confirm_takeover.py` — unified dispatcher

Routes subtake output to the correct `is_valid` function based on the service name in the line. Supports `--full` flag to output the full input line instead of just the domain. Azure routing happens here: a single `azure` service tag is dispatched to `azure_app_service`, `azure_edge_cdn`, `azure_traffic_manager`, or `azure_api_management` based on the CNAME target suffix.

### Config-dependent modules

`confirm_fastly`, `confirm_github`, and `confirm_azure_*` require `~/.subdomain_takeover_tools.ini` (or `~/.subdomain_takeover_tools.ini`). The file format is documented in README.md. These modules load config at import time, so importing them without the config will raise a `KeyError`.

Azure modules use `helper/load_token.py` which relies on `DefaultAzureCredential` (Azure CLI login or environment variables).

### Adding a new service checker

1. Create `confirm_<service>.py` with `is_valid(domain, cname)` and `main()` calling `bootstrap(is_valid)`.
2. Register the entry point in `setup.py` under `console_scripts`.
3. Add dispatch logic in `confirm_takeover.py:perform_uncached()`.
