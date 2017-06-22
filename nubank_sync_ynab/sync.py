import datetime
import json
import logging.config
import os

from pynubank import Nubank

from nubank_sync_ynab.util import filter_transactions, parse_transaction_date
from nubank_sync_ynab.ynab import YNAB


def setup_logging(filename):
    try:
        with open(filename) as f:
            config = json.loads(f.read())
            logging.config.dictConfig(config)
        return True
    except FileNotFoundError:
        print('Missing logging.json, logging not configured.')
        return False


YNAB_EMAIL = os.getenv('YNAB_EMAIL')
YNAB_PASSWORD = os.getenv('YNAB_PASSWORD')
YNAB_BUDGET = os.getenv('YNAB_BUDGET')
NUBANK_LOGIN = os.getenv('NUBANK_LOGIN')
NUBANK_PASSWORD = os.getenv('NUBANK_PASSWORD')
STARTING_POINT = datetime.datetime.strptime(os.getenv('STARTING_POINT'), '%Y-%m-%d').date()

if __name__ == '__main__':
    setup_logging('logging.json')
    ynab = YNAB(YNAB_EMAIL, YNAB_PASSWORD, YNAB_BUDGET)
    nu = Nubank(NUBANK_LOGIN, NUBANK_PASSWORD)
    stmts = nu.get_account_statements()
    transactions = filter_transactions(stmts['transactions'], STARTING_POINT)
    for t in transactions:
        ynab.add_transaction(
            payee=t['merchant_name'],
            date=parse_transaction_date(t),
            value=-float(t['precise_amount']),
            id=t['id'],
            subcategory=t['category'].capitalize()
        )

    ynab.sync()
