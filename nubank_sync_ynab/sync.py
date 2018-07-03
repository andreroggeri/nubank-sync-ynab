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
    log_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.json')
    setup_logging(log_config_file)
    ynab = YNAB(YNAB_EMAIL, YNAB_PASSWORD, YNAB_BUDGET)
    nu = Nubank(NUBANK_LOGIN, NUBANK_PASSWORD)
    transactions = filter_transactions(nu.get_card_statements(), STARTING_POINT)
    for transaction in transactions:
        ynab.add_transaction(
            payee=transaction['description'],
            date=parse_transaction_date(transaction),
            value=-int(transaction['amount']) / 100,
            id=transaction['id'],
            subcategory=transaction['category'].capitalize()
        )

    ynab.sync()
