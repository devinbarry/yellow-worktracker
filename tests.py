__author__ = 'devinbarry@users.noreply.github.com'

import unittest
import datetime
from work_tracker import _parse_line_into_date_and_comment, _parse_date_string_into_date
from work_tracker import _get_refs_from_comment, _get_nums_from_comment, _get_pertinant_words


class WorkTrackerTests(unittest.TestCase):

    def test_parse_line_into_date_and_comment(self):
        test_line = "Thu Nov 7 12:26:45 2013 +1300 Bug fix in tests.ApiTest due to change in get_client. Refs #4390"
        output = _parse_line_into_date_and_comment(test_line)
        self.assertEqual(len(output), 2)

    def test_parse_date_string_into_date(self):
        date_string = "Thu Nov 7 12:26:45 2013 +1300"
        date = _parse_date_string_into_date(date_string)
        self.assertIsInstance(date, datetime.date)

    def test_get_refs_from_comment(self):
        comment = "Bug fix in tests.ApiTest due to change in get_client. Refs #4390"
        list_out = _get_refs_from_comment(comment)
        self.assertEqual(list_out[0], 'Refs #4390')

    def test_get_refs_from_comment_multi(self):
        comment = "Bug fix in tests.ApiTest due to change in get_client. Refs #4390, Refs #2556"
        list_out = _get_refs_from_comment(comment)
        self.assertEqual(list_out[0], 'Refs #4390')
        self.assertEqual(list_out[1], 'Refs #2556')

    def test_get_refs_from_comment_multi_2(self):
        comment = "Bug fix in Refs #4567tests.ApiTest due to change in get_client. Refs #4390, Refs #2556"
        list_out = _get_refs_from_comment(comment)
        self.assertEqual(list_out[0], 'Refs #4567')
        self.assertEqual(list_out[1], 'Refs #4390')
        self.assertEqual(list_out[2], 'Refs #2556')

    def test_get_nums_from_comment(self):
        comment = "Bug fix in tests.ApiTest due to change in get_client. Refs #4390"
        list_out = _get_nums_from_comment(comment)
        self.assertEqual(list_out[0], '4390')

    def test_get_pertinant_words(self):
        comment = "Bug fix in Refs 4567tests.ApiTest due to change in get_client. Refs #4390, Refs #2556"
        list_out = _get_pertinant_words(comment)
        self.assertEqual(list_out[0], 'Refs #4390')
        self.assertEqual(list_out[1], 'Refs #2556')
        self.assertEqual(list_out[2], '4567')