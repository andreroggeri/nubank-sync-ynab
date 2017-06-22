from datetime import datetime
from unittest import TestCase

from freezegun import freeze_time

from nubank_sync_ynab import util


class UtilTests(TestCase):
    def test_parse_transaction_date(self):
        transaction = {'time': '2017-06-21T10:00:00Z'}
        parsed = util.parse_transaction_date(transaction)

        self.assertEqual(parsed, datetime(2017, 6, 21).date())

    @freeze_time('2017-06-21')
    def test_filter_transactions(self):
        transactions = [
            {'time': '2017-06-211T10:00:00Z'},
            {'time': '2017-06-201T10:00:00Z'},
            {'time': '2017-06-19T10:00:00Z'},
            {'time': '2017-06-19T10:00:00Z'},
            {'time': '2017-06-18T10:00:00Z'},
            {'time': '2017-06-17T10:00:00Z'},
            {'time': '2017-06-01T10:00:00Z'}
        ]
        starting_point = datetime(2017, 6, 19).date()
        filtered = util.filter_transactions(transactions, starting_point)
        self.assertEqual(transactions[:4], filtered)
        starting_point = datetime(2017, 1, 1).date()
        filtered = util.filter_transactions(transactions, starting_point, 10)
        self.assertEqual(transactions[:-1], filtered)
