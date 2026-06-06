from unittest import TestCase
from unittest.mock import patch

from subdomain_takeover_tools import (
    confirm_framer,
    confirm_greatpages,
    confirm_leadpages,
    confirm_mashery,
    confirm_meteor,
    confirm_surveysparrow,
    confirm_wix,
)

# (module, a vulnerable hostname, body that proves the takeover,
#  an excluded provider-owned hostname or None when the service has none)
CASES = [
    (confirm_framer, 'scale.example.com',
     '<title>Site Not Found | Framer</title>', 'foo.framer.app'),
    (confirm_leadpages, 'get.example.com',
     "<h2>The page you're looking for may have moved.</h2>", 'foo.leadpages.net'),
    (confirm_meteor, 'app.example.com',
     "404 Not Found: No applications registered for host 'app.example.com'", 'foo.meteor.com'),
    (confirm_greatpages, 'lp.example.com',
     '<h1>Página não encontrada (Erro 404)</h1>', 'cname.greatpages.com.br'),
    (confirm_surveysparrow, 'foo.surveysparrow.com',
     '<div class="ouch!">SurveySparrow says: Account not found.</div>', None),
    (confirm_wix, 'shop.example.com',
     'Error ConnectYourDomain occurred ... wixErrorPagesApp', 'foo.wixdns.net'),
    (confirm_mashery, 'api.example.com',
     'Unrecognized domain <strong>api.example.com</strong>', 'foo.mashery.com'),
]


class TestHttpFingerprintValidators(TestCase):
    def test_fingerprint_present_is_vulnerable(self):
        for module, host, body, _excluded in CASES:
            with self.subTest(module=module.__name__):
                with patch.object(module, 'fetch_body', return_value=(200, body)):
                    self.assertTrue(module.is_valid(host, ''))

    def test_body_without_fingerprint_is_not_vulnerable(self):
        for module, host, _body, _excluded in CASES:
            with self.subTest(module=module.__name__):
                with patch.object(module, 'fetch_body', return_value=(200, 'just a normal page')):
                    self.assertFalse(module.is_valid(host, ''))

    def test_unreachable_host_is_not_vulnerable(self):
        for module, host, _body, _excluded in CASES:
            with self.subTest(module=module.__name__):
                with patch.object(module, 'fetch_body', return_value=(None, None)):
                    self.assertFalse(module.is_valid(host, ''))

    def test_excluded_provider_domain_short_circuits_without_http(self):
        for module, _host, _body, excluded in CASES:
            if excluded is None:
                continue
            with self.subTest(module=module.__name__):
                with patch.object(module, 'fetch_body') as fetch:
                    self.assertFalse(module.is_valid(excluded, ''))
                    fetch.assert_not_called()

    def test_surveysparrow_requires_all_fingerprints(self):
        # only one of the three substrings present -> not a confirmed takeover
        with patch.object(confirm_surveysparrow, 'fetch_body',
                          return_value=(200, 'Account not found.')):
            self.assertFalse(confirm_surveysparrow.is_valid('foo.surveysparrow.com', ''))

    def test_wix_requires_both_fingerprints(self):
        with patch.object(confirm_wix, 'fetch_body',
                          return_value=(200, 'Error ConnectYourDomain occurred')):
            self.assertFalse(confirm_wix.is_valid('shop.example.com', ''))
