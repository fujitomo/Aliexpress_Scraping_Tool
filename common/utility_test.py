from common.utility import *


def test_exchange():
    res = fetch_currency_rate("USD", "JPY")
    print(res)
