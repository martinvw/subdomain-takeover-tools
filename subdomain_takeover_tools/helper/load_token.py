import configparser
import functools
import json
import os
import tempfile
import time

from azure.core.exceptions import AzureError

# ARM scope used for every management.azure.com call.
ARM_SCOPE = 'https://management.azure.com/.default'

# Shared on-disk token cache. The same path is used by the sibling repo so a
# single access token can serve both; writes are therefore atomic (see below).
_CACHE_DIR = os.path.expanduser('~/.cache/subdomain-takeovers')
_CACHE_FILE = os.path.join(_CACHE_DIR, 'azure_mgmt_token.json')

# Refresh once the token is within this many seconds of expiring.
_EXPIRY_MARGIN = 300

# Read the shared ini with interpolation OFF: a client_secret may contain '%',
# which BasicInterpolation would otherwise choke on.
_settings = configparser.ConfigParser(interpolation=None)
_settings.read(os.path.expanduser('~/.subdomain_takeover_tools.ini'))


def _with_retry(exceptions, attempts=3, delay=1):
    """Retry the wrapped call on the given exceptions, re-raising the last one."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt + 1 < attempts:
                        time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator


# Exported so request-making callers can retry on request failures (requests'
# own exceptions subclass IOError, so this also covers connect/read timeouts).
request_retry = _with_retry(IOError)


def build_credential():
    """Prefer an explicit service principal from the ini, else fall back to the
    Azure CLI / DefaultAzureCredential chain with the dead probes excluded."""
    az = _settings['azure'] if _settings.has_section('azure') else {}
    tenant = az.get('tenant_id')
    cid = az.get('client_id')
    secret = az.get('client_secret')

    if tenant and cid and secret:
        from azure.identity import ClientSecretCredential
        return ClientSecretCredential(tenant, cid, secret)

    from azure.identity import DefaultAzureCredential
    return DefaultAzureCredential(
        exclude_managed_identity_credential=True,
        exclude_workload_identity_credential=True,
        exclude_shared_token_cache_credential=True,
    )


def _read_cache():
    """Return a still-valid cached token, or None. A missing/unreadable/corrupt
    cache is treated as a miss."""
    try:
        with open(_CACHE_FILE) as handle:
            data = json.load(handle)
        token = data['token']
        expires_on = float(data['expires_on'])
    except (OSError, ValueError, KeyError, TypeError):
        return None

    if token and (expires_on - time.time()) > _EXPIRY_MARGIN:
        return token
    return None


def _write_cache(token, expires_on):
    """Best-effort atomic write of the token cache with mode 0600. Two repos may
    write this path, so write to a temp file and os.replace() it into place."""
    try:
        os.makedirs(_CACHE_DIR, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=_CACHE_DIR)
        try:
            with os.fdopen(fd, 'w') as handle:
                json.dump({'token': token, 'expires_on': expires_on}, handle)
            os.chmod(tmp_path, 0o600)
            os.replace(tmp_path, _CACHE_FILE)
        except BaseException:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
    except OSError:
        # Caching is an optimisation; never let it break token retrieval.
        pass


@_with_retry(AzureError)
def _fetch_token():
    credential = build_credential()
    return credential.get_token(ARM_SCOPE)


def load_token():
    """Return a management.azure.com access token string, reusing the on-disk
    cache when one is still comfortably valid."""
    cached = _read_cache()
    if cached:
        return cached

    access_token = _fetch_token()
    _write_cache(access_token.token, access_token.expires_on)
    return access_token.token
