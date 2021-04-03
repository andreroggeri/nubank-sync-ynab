import datetime


def filter_transactions(transactions, starting_date, days=30):
    """
    Its necessary to specify the starting date, otherwise we'll mess up with the previous data
    We don't want to sync the whole Nubank history onto YNAB
    The last 30 days should be enough if you sync regularly
    """

    delta = (datetime.datetime.now() - datetime.timedelta(days=days)).date()
    delta = starting_date if delta < starting_date else delta

    def transaction_filter(transaction):
        transaction_date = parse_transaction_date(transaction)
        return transaction_date >= delta

    return list(filter(transaction_filter, transactions))


def parse_transaction_date(transaction) -> datetime.date:
    if 'time' in transaction:
        date_key = 'time'
    else:
        date_key = 'postDate'
    return datetime.datetime.strptime(transaction[date_key][:10], "%Y-%m-%d").date()
