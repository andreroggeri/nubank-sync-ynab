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

    def get_account(self, account_name):
        try:
            logging.info('Searching for ' + account_name + ' account')
            return next(acc for acc in self.client.budget.be_accounts if acc.account_name == account_name)
        except StopIteration:
            logging.info(account_name + ' account not found, creating a new one')
            account = Account()
            account.account_name = account_name
            self.client.budget.be_accounts.append(account)
            self.delta += 1
            return account

    def get_payee(self, payee_name):
        logging.info('Searching for payee with name "{}"'.format(payee_name))
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
        logging.info('Checking if transaction {} is already imported'.format(transaction_id))
        for t in self.client.budget.be_transactions:
            if t.memo and transaction_id in t.memo:
                logging.info('{} found'.format(transaction_id))
                return True
        logging.info('{} not found'.format(transaction_id))
        return False

    def add_transaction(self, **kwargs):
        logging.info('Adding transaction')
        payee = self.get_payee(kwargs['payee'])
        subcategory = self.get_subcategory(kwargs['subcategory'])
        account = self.get_account(kwargs['account'])

        if not self.has_matching_transaction(kwargs['id']):
            logging.info('Creating transaction')
            transaction = Transaction()
            transaction.date = kwargs['date']
            transaction.memo = 'AUTO IMPORT - {}'.format(kwargs['id'])
            transaction.imported_payee = payee.name
            transaction.entities_payee_id = payee.id
            transaction.entities_subcategory_id = subcategory.id if subcategory else None
            transaction.imported_date = datetime.datetime.now().date()
            transaction.source = "Imported"
            transaction.amount = kwargs['value']
            transaction.entities_account_id = account.id
            self.client.budget.be_transactions.append(transaction)
            self.delta += 1

    def sync(self):
        if self.delta > 0:
            logging.info('Pushing {} changes'.format(self.delta))
            self.client.push(self.delta)
            self.delta = 0
        else:
            logging.info('No changes to push.')
