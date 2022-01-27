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

    def test_extract_domain_names(self):
        self.assertEqual(
            "github.com\ngithub.io",
            extract_domain_name("*.github.(com|io)")
        )

    def test_brackets_in_the_front(self):
        self.assertEqual(
            "endlessgroup.org",
            extract_domain_name("(*).endlessgroup.org")
        )

    def test_brackets_in_the_front_2(self):
        self.assertEqual(
            "sharefile.com",
            extract_domain_name("(yoursubdomain).sharefile.com/sf/v3/")
        )
