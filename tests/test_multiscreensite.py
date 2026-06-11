from unittest import TestCase
from unittest.mock import patch

from subdomain_takeover_tools import confirm_multiscreensite as module

FINGERPRINT = module.FINGERPRINT
PUBLISHED = '<html>a real published site</html>'


class TestMultiscreensite(TestCase):
    def test_no_fingerprint_is_not_vulnerable(self):
        with patch.object(module, 'fetch_body', return_value=(200, PUBLISHED)):
            self.assertFalse(module.is_valid('foo.example.com', ''))

    def test_unreachable_host_is_not_vulnerable(self):
        with patch.object(module, 'fetch_body', return_value=(None, None)):
            self.assertFalse(module.is_valid('foo.example.com', ''))

    def test_excluded_provider_domain_short_circuits_without_http(self):
        with patch.object(module, 'fetch_body') as fetch:
            self.assertFalse(module.is_valid('foo.multiscreensite.com', ''))
            fetch.assert_not_called()

    def test_www_does_not_resolve_is_vulnerable(self):
        with patch.object(module, 'fetch_body', return_value=(200, FINGERPRINT)), \
                patch.object(module, 'resolve_ips', return_value=set()):
            self.assertTrue(module.is_valid('foo.example.com', ''))

    def test_www_on_different_host_is_vulnerable(self):
        def resolve(hostname):
            return {'1.1.1.1'} if hostname.startswith('www.') else {'2.2.2.2'}

        with patch.object(module, 'fetch_body', return_value=(200, FINGERPRINT)), \
                patch.object(module, 'resolve_ips', side_effect=resolve):
            self.assertTrue(module.is_valid('foo.example.com', ''))

    def test_published_www_on_same_host_is_false_positive(self):
        # the experiences.grab.com case: bare host unpublished, www is a live site
        def fetch(hostname, *args, **kwargs):
            if hostname.startswith('www.'):
                return 200, PUBLISHED
            return 200, FINGERPRINT

        with patch.object(module, 'fetch_body', side_effect=fetch), \
                patch.object(module, 'resolve_ips', return_value={'1.1.1.1'}):
            self.assertFalse(module.is_valid('foo.example.com', ''))

    def test_unpublished_www_on_same_host_is_vulnerable(self):
        with patch.object(module, 'fetch_body', return_value=(200, FINGERPRINT)), \
                patch.object(module, 'resolve_ips', return_value={'1.1.1.1'}):
            self.assertTrue(module.is_valid('foo.example.com', ''))

    def test_www_host_with_fingerprint_is_vulnerable(self):
        with patch.object(module, 'fetch_body', return_value=(200, FINGERPRINT)) as fetch:
            self.assertTrue(module.is_valid('www.example.com', ''))
            # only the bare host is fetched; no www-of-www comparison
            self.assertEqual(fetch.call_count, 1)
