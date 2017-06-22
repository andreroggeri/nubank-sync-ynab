from datetime import datetime
from unittest import TestCase

from pynYNAB.schema import Catalog, Budget, Payee, Transaction

from ynab import YNAB


class MockConnection:
    def __init__(self, email, password):
        self.user_id = '1234'
        self.catalog = Catalog()
        self.budget = Budget()

    def dorequest(self, request_dic, opname):
        if opname == 'syncCatalogData':
            return {'changed_entities': {k: [] for k in self.catalog.listfields}, 'server_knowledge_of_device': 0,
                    'current_server_knowledge': 123}
        if opname == 'syncBudgetData':
            return {'changed_entities': {k: [] for k in self.budget.listfields}, 'server_knowledge_of_device': 0,
                    'current_server_knowledge': 123}

    def init_session(self):
        pass


class YNABTests(TestCase):
    def setUp(self):
        self.ynab = YNAB('user', 'password', 'Test', MockConnection, False)

    def test_can_create(self):
        self.assertTrue(self.ynab)

    def test_can_find_nubank_account(self):
        acc = self.ynab.get_nubank_account()
        self.assertEqual(self.ynab.delta, 1)
        self.assertTrue(acc)

    def test_can_find_payee(self):
        payee = Payee()
        payee.name = 'Test Payee'
        self.ynab.client.budget.be_payees.append(payee)
        payee = self.ynab.get_payee('Test Payee')

        self.assertTrue(payee)
        self.assertEqual(self.ynab.delta, 1)

    def test_can_create_payee(self):
        payee = self.ynab.get_payee('Test Payee')
        self.assertTrue(payee)
        self.assertEqual(self.ynab.delta, 2)  # Nubank Account + Payee

    def test_find_matching_transaction(self):
        t = Transaction()
        t.memo = '001'
        self.ynab.client.budget.be_transactions.append(t)

        self.assertTrue(self.ynab.has_matching_transaction('001'))
        self.assertFalse(self.ynab.has_matching_transaction('002'))

    def test_add_transaction(self):
        self.ynab.add_transaction(
            payee='John Snow',
            date=datetime(2017, 6, 21).date(),
            id='001',
            value=10.0,
            subcategory='Bla Bla'
        )

        self.assertEqual(self.ynab.delta, 3)  # New Account + New transaction + New Payee

        self.ynab.add_transaction(
            payee='John Snow',
            date=datetime(2017, 6, 21).date(),
            id='001',
            value=10.0,
            subcategory='Bla Bla'
        )

        self.assertEqual(self.ynab.delta, 3)  # No Changes !

    def test_sync(self):
        self.assertEqual(self.ynab.delta, 1)
        self.ynab.sync()
        self.assertEqual(self.ynab.delta, 0)
        self.ynab.sync()
