import unittest
import efp5
import time
from mock import patch, Mock, call, ANY


class TestEFP(unittest.TestCase):

    def setUp(self):
        self.subject = efp5.efp5()

        self.INVESTORS_AND_JAMES_IS_MASSIVELY_HAPPY = '9999999'
        self.RAISED_AND_JAMES_IS_MASSIVELY_HAPPY = '49,999,99.99'
        self.INVESTORS_AFTER_SMASHING_THE_TARGET = '22422'
        self.RAISED_AFTER_SMASHING_THE_TARGET = '10,427,295.00'

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
            fakeFileStub()
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
            fakeFileStub()
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

    @patch('os.path.exists')
    @patch('__builtin__.open')
    @patch('sys.stderr')
    def test_write_locaal_data_with_existing_data(self, sysStdErrMock, openMock, pathexistsMock):
        # Setup
        pathexistsMock.side_effect = [
            True
        ]

        openMock.side_effect = [
            # for the read
            fakeFileStub(type='json'),
            # for the write
            fakeFileStub()
        ]

        # Action
        efp5_json = self.subject._write_local_data(self.RAISED_AND_JAMES_IS_MASSIVELY_HAPPY,
                                                   self.INVESTORS_AND_JAMES_IS_MASSIVELY_HAPPY)

        # assert
        self.assertEqual(len(efp5_json), 2)
        self.assertEqual(len(efp5_json[0]), 4)
        self.assertEqual(efp5_json[0][2], self.RAISED_AFTER_SMASHING_THE_TARGET)
        self.assertEqual(efp5_json[0][3], self.INVESTORS_AFTER_SMASHING_THE_TARGET)
        self.assertTrue(efp5_json[1][0] > time.time() - 1)
        self.assertEqual(efp5_json[1][2], self.RAISED_AND_JAMES_IS_MASSIVELY_HAPPY)
        self.assertEqual(efp5_json[1][3], self.INVESTORS_AND_JAMES_IS_MASSIVELY_HAPPY)

    @patch('os.path.exists')
    def test_connect_to_dropbox_errors_if_no_token(self, pathExistsMock):
        # Subject
        pathExistsMock.side_effect = [
            False
        ]
        e = None

        # Action
        try:
            self.subject._connect_to_dropbox()
        except Exception, e:
            pass

        # Assert
        self.assertEqual(e.message, 'No dropbox-api file')

    @patch('dropbox.Dropbox')
    @patch('__builtin__.open')
    @patch('os.path.exists')
    def test_connect_to_dropbox_with_token(self, pathExistsMock, openMock, dropboxMock):
        # Setup
        pathExistsMock.side_effect = [
            True
        ]

        openMock.side_effect = [
            fakeFileStub('token')
        ]
        self.subject._check_dropbox_connection = Mock()

        # Action
        self.subject._connect_to_dropbox()

        # Assert
        dropboxMock.assert_called_once_with('this-is-a-token')
        self.subject._check_dropbox_connection.assert_called_once()

    def test_check_dropbox_connection_without_assert(self):
        # Setup
        dbx = Mock()

        # Action
        return_value = self.subject._check_dropbox_connection(dbx)

        # Assert
        self.assertTrue(return_value)

    def test_check_dropbox_connection_with_a_problem(self):
        # Setup
        dbx = Mock()
        dbx.users_get_current_account.side_effect = [
            Exception('original exception message')
        ]
        e = None

        # Action
        try:
            return_value = self.subject._check_dropbox_connection(dbx)
            raise('Expected this method to fail')
        except Exception, e:
            pass

        # Assert
        self.assertEqual(e.message, 'Unable to connect to drop-box\noriginal exception message')

    @patch('__builtin__.open')
    def test_upload_file_to_dropbox(self, openMock):
        # Setup
        dbx = Mock()
        openMock.side_effect = [
            fakeFileStub(type='string')
        ]

        # Action
        self.subject._upload_file_to_dropbox(dbx, 'this_file', 'this_folder', 'this_subfolder')

        # Assert
        dbx.files_upload.assert_called_once_with("thisis a\nstring", 'this_folder/this_subfolder/this_file',
                                                 mode=self.subject.DROPBOX_OVERWRITE)

    @patch('os.path.exists')
    @patch('__builtin__.open')
    def test_convert_json_to_csv_if_csv_file_is_missing(self, openMock, pathExistsMock):
        # Setup
        pathExistsMock.side_effect = [
            False
        ]
        self.subject._write_csv_entry = Mock()

        # Action
        self.subject._convert_json_to_csv(
            [
                [123.4324, "Sat 20th", "11,199,999.99", "24,999"],
                [125.4324, "Sun 21st", "12,200,000.00", "25,000"]
            ])

        # Assert
        self.assertEqual(self.subject._write_csv_entry.call_count, 2)
        openMock.assert_called_once_with('brewdog-efp5.csv', 'w')
        self.subject._write_csv_entry.assert_has_calls([
            call(ANY, [123.4324, "Sat 20th", "11,199,999.99", "24,999"]),
            call(ANY, [125.4324, "Sun 21st", "12,200,000.00", "25,000"])
        ])

    @patch('os.path.exists')
    @patch('__builtin__.open')
    def test_convert_json_to_csv_if_csv_exists_already(self, openMock, pathExistsMock):
        # Setup
        pathExistsMock.side_effect = [
            True
        ]
        self.subject._write_csv_entry = Mock()

        # Action
        self.subject._convert_json_to_csv(
            [
                [123.4324, "Sat 20th", "11,199,999.99", "24,999"],
                [125.4324, "Sun 21st", "12,200,000.00", "25,000"]
            ])

        # Assert
        self.assertEqual(self.subject._write_csv_entry.call_count, 1)
        openMock.assert_called_once_with('brewdog-efp5.csv', 'a')
        self.subject._write_csv_entry.assert_has_calls([
            call(ANY, [125.4324, "Sun 21st", "12,200,000.00", "25,000"])
        ])

    def test_write_csv_entry(self):
        # Setup
        fileHandle = Mock()
        entry = [125.4324, "Sun 21st", "12,200,000.00", "25,000"]

        # Action
        self.subject._write_csv_entry(fileHandle, entry)

        # Assert
        fileHandle.write.assert_called_once_with('125.4324,Sun 21st,12200000.00,25000\r\n')

    def test_everything_together(self):
        # Setup
        self.subject._download_data = Mock(side_effect=['data-from-web-request'])
        self.subject._extract_data = Mock(side_effect=[(47.50, 1)])
        self.subject._write_local_data = Mock(side_effect=[["this-is-json"]])
        self.subject._convert_json_to_csv = Mock()
        self.subject._connect_to_dropbox = Mock(side_effect=['dropbox-object()'])
        self.subject._upload_file_to_dropbox = Mock()

        # Action
        self.subject.check_progress_write_data_and_upload_to_dropbox()

        # Assert
        self.assertEqual(self.subject._download_data.call_count, 1)
        self.subject._extract_data.assert_called_once_with('data-from-web-request')
        self.subject._write_local_data.assert_called_once_with(47.50, 1)
        self.subject._convert_json_to_csv.assert_called_once_with(["this-is-json"])
        self.assertEqual(self.subject._connect_to_dropbox.call_count, 1)
        self.subject._upload_file_to_dropbox.assert_has_calls([
            call('dropbox-object()', 'brewdog-efp5.json'),
            call('dropbox-object()', 'brewdog-efp5.csv')
        ])


class fakeFileStub:
    def __init__(self, type='string'):
        self.type = type

    def readline(self):
        return 'this-is-a-token\r\n'

    def read(self):
        if self.type == 'json':
            return """[ [12345678.00, "Monday 1st January", "10,427,295.00", "22422"] ]"""
        else:
            return "thisis a\nstring"

    def write(self, x=None):
        pass

    def close(self):
        pass

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        pass
