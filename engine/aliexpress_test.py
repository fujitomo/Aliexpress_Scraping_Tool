from engine.aliexpress import *


def test_fetch_item():
    aliexpress = AliexpressScraping()
    res = aliexpress.fetch_item(
        "https://ja.aliexpress.com/item/1005002652152358.html?algo_pvid=dc375bb3-9ab1-4197-baa2-3a19482683c3&algo_exp_id=dc375bb3-9ab1-4197-baa2-3a19482683c3-0&pdp_ext_f=%7B%22sku_id%22%3A%2212000021564424315%22%7D"
    )
    print(res.__dict__)


def test_fetch_items():
    aliexpress = AliexpressScraping()
    aliexpress.login()
    items = aliexpress.fetch_items(
        url="https://ja.aliexpress.com/category/26/toys-hobbies.html?spm=a2g0o.home.109.1.18555c72uawouN",
        page_limit=3,
    )
    print(len(items))
