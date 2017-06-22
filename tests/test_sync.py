import logging
import os
from unittest import TestCase


class SyncTests(TestCase):
    def setUp(self):
        os.environ['YNAB_EMAIL'] = 'email'
        os.environ['YNAB_PASSWORD'] = 'password'
        os.environ['YNAB_BUDGET'] = 'Test'
        os.environ['NUBANK_LOGIN'] = 'nu login'
        os.environ['NUBANK_PASSWORD'] = 'nu password'
        os.environ['STARTING_POINT'] = '2017-06-22'

    def tearDown(self):
        logging.disable(logging.CRITICAL)  # Disable logging for testing

    def test_sync(self):
        # noinspection PyUnresolvedReferences
        import nubank_sync_ynab.sync

    def test_setup_logging_missing_json(self):
        from nubank_sync_ynab.sync import setup_logging
        self.assertFalse(setup_logging('nonexistent'))

    def test_setup_logging(self):
        from nubank_sync_ynab.sync import setup_logging
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(path, 'nubank_sync_ynab', 'logging.json')
        self.assertTrue(setup_logging(path))
