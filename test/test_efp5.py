import unittest
import efp5
import time
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
        # Setup
        urllibMock.side_effect = [
            fakeFile()
        ]

        # Action
        body = self.subject._download_data()

        # assert
        urllibMock.assert_called_once_with(self.subject.URL)
        self.assertEqual(body, ['thisis', 'a', 'string'])

    @patch('os.path.exists')
    @patch('__builtin__.open')
    @patch('sys.stderr')
    def test_write_locaal_data_for_first_time(self, sysStdErrMock, openMock, pathexistsMock):
        # Setup
        pathexistsMock.side_effect = [
            False
        ]

        openMock.side_effect = [
            fakeFile()
        ]

        # Action
        efp5_json = self.subject._write_local_data(self.RAISED_AND_JAMES_IS_MASSIVELY_HAPPY,
                                                   self.INVESTORS_AND_JAMES_IS_MASSIVELY_HAPPY)

        # assert
        self.assertEqual(len(efp5_json), 1)
        self.assertEqual(len(efp5_json[0]), 4)
        self.assertTrue(efp5_json[0][0] > time.time() - 1)
        self.assertEqual(efp5_json[0][2], self.RAISED_AND_JAMES_IS_MASSIVELY_HAPPY)
        self.assertEqual(efp5_json[0][3], self.INVESTORS_AND_JAMES_IS_MASSIVELY_HAPPY)


class fakeFile:
    def read(self):
        return "thisis a\nstring"

    def write(self, x=None):
        pass

    def close(self):
        pass
