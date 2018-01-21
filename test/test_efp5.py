import unittest
import efp5
from mock import patch


class TestEFP(unittest.TestCase):

    def setUp(self):
        self.subject = efp5.efp5()

        self.INVESTORS_AND_JAMES_IS_MASSIVELY_HAPPY = '9999999'
        self.RAISED_AND_JAMES_IS_MASSIVELY_HAPPY = '49,999,99.99'

        self.htmldoc = """<html>
        <head>
        </head>
        <body>

        <span>Raised</span>
        <h3>\xc2\xa349,999,99.99</h3>
        </span>

        <span>Investors</span>
        <h3>9999999</h3>
        </span>

        </body>
        </html>"""
        self.htmldoc = self.htmldoc.split()

    @patch('sys.stderr')
    def test_extract_data(self, sysStdErrMock):
        # Action
        (amount, investors) = self.subject._extract_data(self.htmldoc)

        # Assert
        self.assertEqual(amount, self.RAISED_AND_JAMES_IS_MASSIVELY_HAPPY)
        self.assertEqual(investors, self.INVESTORS_AND_JAMES_IS_MASSIVELY_HAPPY)

    @patch('urllib.urlopen')
    @patch('sys.stderr')
    def test_download_data(self, sysStdErrMock, urllibMock):

        urllibMock.side_effect = [
            fakeFile()
        ]

        # Action
        body = self.subject._download_data()

        # assert
        urllibMock.assert_called_once_with(self.subject.URL)
        self.assertEqual(body, ['thisis', 'a', 'string'])


class fakeFile:
    def read(self):
        return "thisis a\nstring"
