from engine.aliexpress_requests import *


def test_fetch_item():
    aliexpress = AliexpressRequests()
    res = aliexpress.get_item_data_dict(
        "https://ja.aliexpress.com/item/1005002652152358.html?algo_pvid=dc375bb3-9ab1-4197-baa2-3a19482683c3&algo_exp_id=dc375bb3-9ab1-4197-baa2-3a19482683c3-0&pdp_ext_f=%7B%22sku_id%22%3A%2212000021564424315%22%7D"
    )
    print(res)


def test_get_items_dict():
    aliexpress = AliexpressRequests()
    res = aliexpress.find_all_product_ids(
        "https://ja.aliexpress.com/category/26/toys-hobbies.html?trafficChannel=main&catName=toys-hobbies&CatId=26&ltype=wholesale&SortType=default&g=y&isrefine=y"
    )
    print(res)

    assert len(res) == 60


def test_fetch_items():
    aliexpress = AliexpressRequests()
    res = aliexpress.fetch_items(
        "https://ja.aliexpress.com/category/26/toys-hobbies.html?spm=a2g0o.home.109.1.18555c72uawouN",
        page_limit=3,
    )
    print(res)
