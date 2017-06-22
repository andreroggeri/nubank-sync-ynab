import datetime
import logging

from pynYNAB.ClientFactory import nYnabClientFactory
from pynYNAB.connection import nYnabConnection
from pynYNAB.schema.budget import Account, Transaction, Payee


class YNAB:

    def __init__(self, email, password, budget, ynab_connection=nYnabConnection, sync=True):
        connection = ynab_connection(email, password)
        connection.init_session()
        self.client = nYnabClientFactory().create_client(
            email=email,
            password=password,
            nynabconnection=connection,
            budgetname=budget,
            sync=sync
        )
        self.delta = 0
        self.account = self.get_nubank_account()

    def get_nubank_account(self):
        try:
            logging.info('Searching for Nubank account')
            return next(acc for acc in self.client.budget.be_accounts if acc.account_name == 'Nubank')
        except StopIteration:
            logging.info('Nubank account not found, creating a new one')
            account = Account()
            account.account_name = 'Nubank'
            self.client.budget.be_accounts.append(account)
            self.delta += 1
            return account

    def get_payee(self, payee_name):
        try:
            return next(payee for payee in self.client.budget.be_payees if payee.name == payee_name)
        except StopIteration:
            logging.info('Creating new payee "{}"'.format(payee_name))
            payee = Payee()
            payee.name = payee_name
            self.client.budget.be_payees.append(payee)
            self.delta += 1
            return payee

    def get_subcategory(self, category_name):
        try:
            return next(category for category in self.client.budget.be_subcategories if category.name == category_name)
        except StopIteration:
            return None

    def has_matching_transaction(self, transaction_id):
        for t in self.client.budget.be_transactions:
            if t.memo and transaction_id in t.memo:
                return True
        return False

    def add_transaction(self, **kwargs):
        payee = self.get_payee(kwargs['payee'])
        subcategory = self.get_subcategory(kwargs['subcategory'])
        if self.has_matching_transaction(kwargs['id']):
            print('Update this transaction')
        else:
            transaction = Transaction()
            transaction.date = kwargs['date']
            transaction.memo = 'AUTO IMPORT - {}'.format(kwargs['id'])
            transaction.imported_payee = payee.name
            transaction.entities_payee_id = payee.id
            transaction.entities_subcategory_id = subcategory.id if subcategory else None
            transaction.imported_date = datetime.datetime.now().date()
            transaction.source = "Imported"
            transaction.amount = kwargs['value']
            transaction.entities_account_id = self.account.id
            self.client.budget.be_transactions.append(transaction)
            self.delta += 1

    def sync(self):
        if self.delta > 0:
            logging.info('Pushing {} changes'.format(self.delta))
            self.client.push(self.delta)
            self.delta = 0
        else:
            logging.info('No changes to push.')
