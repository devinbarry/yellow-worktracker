__author__ = 'devinbarry@users.noreply.github.com'

import unittest
import datetime
from work_tracker import _parse_line_into_date_and_comment, _parse_date_string_into_date


class WorkTrackerTests(unittest.TestCase):

    def test_parse_line_into_date_and_comment(self):
        test_line = "Thu Nov 7 12:26:45 2013 +1300 Bug fix in tests.ApiTest due to change in get_client. Refs #4390"
        output = _parse_line_into_date_and_comment(test_line)
        self.assertEqual(len(output), 2)

    def test_parse_date_string_into_date(self):
        date_string = "Thu Nov 7 12:26:45 2013 +1300"
        date = _parse_date_string_into_date(date_string)
        self.assertIsInstance(date, datetime.datetime)