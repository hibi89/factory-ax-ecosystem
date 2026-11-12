"""Static guards for standalone owner draft UI; real browser check is separate."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

HTML_PATH = Path(__file__).resolve().parents[1] / 'web' / 'supplier_profile.html'


class Guard(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.ids = []
        self.forms = []
        self.meta = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'script':
            self.scripts.append(d)
        if tag == 'form':
            self.forms.append(d)
        if tag == 'meta':
            self.meta.append(d)
        if 'id' in d:
            self.ids.append(d['id'])


class ProfileContract(unittest.TestCase):
    def setUp(self):
        self.html = HTML_PATH.read_text(encoding='utf-8')
        self.tags = Guard()
        self.tags.feed(self.html)

    def test_csp_disallows_connect(self):
        self.assertTrue(any(m.get('http-equiv') == 'Content-Security-Policy'
                            and "connect-src 'none'" in m.get('content', '') for m in self.tags.meta))

    def test_no_remote_script_or_form(self):
        self.assertEqual(self.tags.forms, [])
        self.assertEqual(len(self.tags.scripts), 1)
        self.assertNotIn('src', self.tags.scripts[0])

    def test_draft_is_not_approval(self):
        self.assertIn('approved_by:null', self.html)
        self.assertIn('DRAFT_NOT_APPROVED', self.html)

    def test_owner_policy_fields_visible(self):
        for field in ('policyId','version','from','to','partialProduction','partialInspection','partialShipment','returns','rework','tolerance','draft'):
            self.assertIn(field, self.tags.ids)


if __name__ == '__main__':
    unittest.main()
