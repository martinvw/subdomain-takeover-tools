import io
import sys
from unittest import TestCase
from unittest.mock import patch

from subdomain_takeover_tools import confirm_takeover
from subdomain_takeover_tools.confirm_takeover import _normalize_nuclei_service
from subdomain_takeover_tools.helper.prepare import is_nuclei_line, parse_nuclei_line


def _run_dispatcher(sample, argv):
    """Run confirm_takeover.main() over `sample` with `argv`, stubbing the actual
    network check so the three result states are deterministic:
      vulnerable.* -> True, invalid.* -> False, anything else -> None (unsupported)."""

    def fake_perform_check(service, target, domain):
        if domain.startswith('vulnerable'):
            return True
        if domain.startswith('invalid'):
            return False
        return None

    out = io.StringIO()
    with patch.object(confirm_takeover, '_perform_check', fake_perform_check), \
            patch.object(sys, 'argv', argv), \
            patch.object(sys, 'stdin', io.StringIO(sample)), \
            patch.object(sys, 'stdout', out):
        confirm_takeover.main()
    return [line for line in out.getvalue().splitlines() if line]


class TestNucleiParsing(TestCase):
    def test_detects_nuclei_line(self):
        self.assertTrue(is_nuclei_line(
            '[github-takeover] [http] [high] https://example.com ["example.github.io"]'
        ))

    def test_detects_nuclei_line_without_extracted(self):
        self.assertTrue(is_nuclei_line(
            '[surveysparrow-takeover] [http] [high] https://foo.surveysparrow.com'
        ))

    def test_does_not_detect_subtake_line(self):
        self.assertFalse(is_nuclei_line('[github: example.github.io]\t\texample.com'))

    def test_does_not_detect_plain_hostname(self):
        self.assertFalse(is_nuclei_line('example.com'))

    def test_parse_line(self):
        self.assertEqual(
            ('github-takeover', 'projectdiscovery.github.io', 'app.root.example.net'),
            parse_nuclei_line(
                '[github-takeover] [http] [high] https://app.root.example.net ["projectdiscovery.github.io"]'
            )
        )

    def test_parse_line_strips_scheme_and_path(self):
        (_, _, domain) = parse_nuclei_line(
            '[aws-bucket-takeover] [http] [high] http://auth-s3.bmw.com ["auth-s3.bmw.com"]'
        )
        self.assertEqual('auth-s3.bmw.com', domain)

    def test_parse_line_without_extracted(self):
        self.assertEqual(
            ('surveysparrow-takeover', '', 'foo.surveysparrow.com'),
            parse_nuclei_line(
                '[surveysparrow-takeover] [http] [high] https://foo.surveysparrow.com'
            )
        )

    def test_parse_line_takes_first_extracted_value(self):
        (_, target, _) = parse_nuclei_line(
            '[github-takeover] [http] [high] https://example.com ["a.github.io","b.github.io"]'
        )
        self.assertEqual('a.github.io', target)

    def test_normalize_known_service(self):
        self.assertEqual('github', _normalize_nuclei_service('github-takeover'))

    def test_normalize_aliased_service(self):
        self.assertEqual('s3 bucket', _normalize_nuclei_service('aws-bucket-takeover'))

    def test_normalize_azure(self):
        # the azure template id lives in dns/ and is not named "*-takeover"
        self.assertEqual('azure', _normalize_nuclei_service('azure-takeover-detection'))

    def test_normalize_http_fingerprint_services(self):
        self.assertEqual('framer', _normalize_nuclei_service('framer-takeover'))
        self.assertEqual('leadpages', _normalize_nuclei_service('leadpages-takeover'))
        self.assertEqual('meteor', _normalize_nuclei_service('meteor-takeover'))
        self.assertEqual('surveysparrow', _normalize_nuclei_service('surveysparrow-takeover'))
        self.assertEqual('greatpages', _normalize_nuclei_service('greatpages-takeover'))
        self.assertEqual('wix', _normalize_nuclei_service('wix-takeover'))
        self.assertEqual('mashery', _normalize_nuclei_service('mashery-takeover'))

    def test_normalize_unknown_service_falls_back_to_template_id(self):
        self.assertEqual('nonexistent-takeover', _normalize_nuclei_service('nonexistent-takeover'))


SAMPLE = (
    '[github-takeover] [http] [high] https://vulnerable.example.com ["x.github.io"]\n'
    '[github-takeover] [http] [high] https://invalid.example.com ["x.github.io"]\n'
    '[nonexistent-takeover] [http] [high] https://unsupported.example.com ["x.example.net"]\n'
)


class TestIncludeUnsupported(TestCase):
    def test_default_drops_unsupported_and_invalid(self):
        self.assertEqual(
            ['vulnerable.example.com'],
            _run_dispatcher(SAMPLE, ['confirm_takeover'])
        )

    def test_include_unsupported_adds_none_results(self):
        self.assertEqual(
            ['vulnerable.example.com', 'unsupported.example.com'],
            _run_dispatcher(SAMPLE, ['confirm_takeover', '--include-unsupported'])
        )

    def test_include_unsupported_does_not_resurrect_invalid(self):
        # the confirmed-invalid line must still be filtered out
        self.assertNotIn(
            'invalid.example.com',
            _run_dispatcher(SAMPLE, ['confirm_takeover', '--include-unsupported'])
        )
