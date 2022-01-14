from unittest import TestCase

from subdomain_takeover_tools.extract_domain_names import extract_domain_name


class Test(TestCase):
    def test_extract_domain_name(self):
        self.assertEqual(
            "github.com",
            extract_domain_name("test.github.com")
        )

    def test_extract_domain_name_co_uk(self):
        self.assertEqual(
            "github.co.uk",
            extract_domain_name("test.test.github.co.uk")
        )
