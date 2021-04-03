import datetime
import json
import logging.config
import os
import base64

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
NUBANK_TOKEN = os.getenv('NUBANK_TOKEN')
NUBANK_CERT = os.getenv('NUBANK_CERT')
NUBANK_CARD_ACCOUNT = os.getenv('NUBANK_CARD_ACCOUNT')
NUBANK_NUCONTA_ACCOUNT = os.getenv('NUBANK_NUCONTA_ACCOUNT')
STARTING_POINT = datetime.datetime.strptime(os.getenv('STARTING_POINT'), '%Y-%m-%d').date()

IN_EVENT = ['TransferInEvent', 'TransferOutReversalEvent']

if __name__ == '__main__':
    with open('cert.p12', 'wb') as f:
        cert_content = base64.b64decode(NUBANK_CERT)
        f.write(cert_content)

    log_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.json')
    setup_logging(log_config_file)
    ynab = YNAB(YNAB_EMAIL, YNAB_PASSWORD, YNAB_BUDGET)
    nu = Nubank()
    nu.authenticate_with_refresh_token(NUBANK_TOKEN, './cert.p12')

    transactions = filter_transactions(nu.get_card_statements(), STARTING_POINT)

    print(f'Found {len(transactions)} card transactions')
    for transaction in transactions:
        ynab.add_transaction(
            payee=transaction['description'],
            date=parse_transaction_date(transaction),
            value=-int(transaction['amount']) / 100,
            id=transaction['id'],
            subcategory=transaction['category'].capitalize(),
            account=NUBANK_CARD_ACCOUNT
        )
    
    account_transactions = filter_transactions(nu.get_account_statements(), STARTING_POINT)

    print(f'Found {len(account_transactions)} account transactions')
    for transaction in account_transactions:
        print(transaction)
        payee = transaction['title']
        if not transaction.get('__typename') in IN_EVENT:
            transaction['amount'] = transaction['amount'] * -1
            if 'destinationAccount' in transaction:
                payee = transaction['destinationAccount']['name']
        else:
            if 'originAccount' in transaction:
                payee = transaction['originAccount']['name']
        ynab.add_transaction(
            payee=payee,
            date=parse_transaction_date(transaction),
            value=transaction['amount'],
            id=transaction['id'],
            subcategory='',
            account=NUBANK_NUCONTA_ACCOUNT
        )

    ynab.sync()
