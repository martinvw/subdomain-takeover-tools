from typing import Optional

from subdomain_takeover_tools.helper.main import bootstrap
from subdomain_takeover_tools.helper.prepare import resolve_cname


def is_valid(hostname: str, cname: Optional[str]) -> Optional[bool]:
    if hostname == cname:
        cname = resolve_cname(hostname)

    if cname is None:
        return False

    # fairly basic check, but hello123.azurefd.net is vulnerable while, if the cname points to hello123.zXX.azurefd.net, then it is safe
    return cname.count('.') == 2


def main():
    bootstrap(is_valid)


if __name__ == "__main__":
    main()
