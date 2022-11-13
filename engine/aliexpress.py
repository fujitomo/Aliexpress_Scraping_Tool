"""Aliexpressスクレイピング処理

* Chromeドライバで行う
* 検索結果一覧画面から行う事前提の処理

Todo:
    * なし

"""

import datetime
import json
import math
import re
import time
import typing
from pprint import pprint

import eel

from common.logger import set_logger
from common.selenium_manager import SeleniumManager
from common.utility import *
from models.aliexpress_item import AliexpressItem

logger = set_logger(__name__)

class AliexpressScraping:
    """Aliexpressスクレイピングクラス
    Note:
        ChromeドライバでAliexpressのスクレイピングを行う
    """
    
    ALIEXPRESS_DOMAIN_URL = "https://ja.aliexpress.com"
    LOGIN_URL = "https://login.aliexpress.com/"

    def __init__(self):
        """初期化
        """
        self.manager = SeleniumManager(use_headless=False)
        self.chrome = self.manager.chrome
        # 為替レートを取得
        _currency_rate = fetch_currency_rate("USD", "JPY")
        if not _currency_rate:
            raise Exception("currency exchange error")
        self.currency_rate = _currency_rate

    def quit(self):
        """アプリ終了処理
        """
        self.chrome.quit()

    def login(self):
        """アプリ終了処理
        """
        self.chrome.get(self.LOGIN_URL)
        try:
            while True:
                if self.chrome.find_elements_by_css_selector(".fm-logined") >= 1:
                    self.chrome.find_element_by_css_selector(".fm-button").click()
                    logger.info("already login")
                    break
                if self.chrome.current_url in self.ALIEXPRESS_DOMAIN_URL:
                    logger.info("login completed")
                    break
                time.sleep(3)
                logger.info("waitting for login")
        except Exception as e:
            logger.error(f"login error: {e}")

    def fetch_item(self, url: str) -> AliexpressItem:
        """商品ページからスクレイピングして結果を返す
        Attributes
          url: スクレイピング対象のURL(商品ページ)
        Returns:
          AliexpressItem:スクレイピング結果
        """
        logger.info(f"fetch_item > url: {url}")
        self.chrome.get(url)
        item_dict = self.chrome.execute_script("return window.runParams")
        item = self._extract_item_dict(item_dict)
        # pprint(item)
        # with open("item_data_test.json", mode="w", encoding="utf-8_sig") as f:
        #     f.write(json.dumps(item, ensure_ascii=False))

        return item

    def fetch_items_url(
        self, url: str, page_limit: int = 10
    ) -> typing.List[AliexpressItem]:
        """商品一覧ページからスクレイピングして結果を返す
        Attributes
          url: スクレイピング対象のURL(検索結果一覧ページ)
          page_limit: 検索結果一覧で何ページ分までスクレイピングするかの限界値
        Returns:
          List[AliexpressItem]:スクレイピング結果
        """
        items = []
        # ページ数取得
                
        for page in range(page_limit):
            self.manager.chrome.get(f"{url}&page={page+1}")
            items_dict = self.manager.chrome.execute_script("return window.runParams")
            try:
                for item in items_dict["mods"]["itemList"]["content"]:
                    items.append(
                        AliexpressItem(
                            url=self.ALIEXPRESS_DOMAIN_URL
                            + item["productDetailUrl"][
                                : item["productDetailUrl"].find("?")
                            ]
                        )
                    )
                    # ページリミットをオーバーするページ数になる場合に処理を抜ける
                    page_size = items_dict["pageInfo"]["pageSize"]
                    total_pages = int(math.ceil(items_dict["pageInfo"]["totalResults"] / page_size))
                    if page >= int(items_dict['pageInfo']['pageSize']):
                       return items
                   
                # time.sleep(10)
            except Exception as e:
                logger.error(f"fetch item dict error:{e}")
                break

        return items

    @eel.expose
    def fetch_items(
        self, url: str, page_limit: int = 10
    ) -> typing.List[AliexpressItem]:
        """指定したURLをスクレイピングしてAliexpressItem情報を返す
        Attributes
          url: スクレイピング対象のURL(検索結果一覧ページ)
          page_limit: 検索結果一覧で何ページ分までスクレイピングするかの限界値
        Returns:
          List[AliexpressItem]:スクレイピング結果
        """
        items = self.fetch_items_url(url, page_limit)

        eel.view_log_js(
            f"------------------------------------アイテム情報取得開始------------------------------------"
        )
        eel.view_log_js(f"{now_timestamp_jp()}アイテムは全部で{len(items)}個です。")

        count = 1
        for item in items:
            if not item.url:
                logger.warning("url is not set")
                continue
            item.merge(self.fetch_item(item.url))
            eel.view_log_js(
                f"{now_timestamp_jp()}{count}/{len(items)}個目のアイテム情報を取得しました。"
            )
            count += 1

        eel.view_log_js(
            f"------------------------------------アイテム情報取得完了------------------------------------"
        )

        return items

    def _extract_item_dict(self, item_dict: dict) -> AliexpressItem:
        """取得した情報を加工して結果を返す
        Attributes
          item_dict: スクレイピング対象のURL(検索結果一覧ページ)
        Returns:
          AliexpressItem:スクレイピング情報を加工した結果
        """
        data = item_dict.get("data")
        if not data:
            logger.error("data not found")
            raise Exception(f"extract error")
        try:
            try:
                max_price = int(
                    data["priceModule"]["maxActivityAmount"]["value"]
                    * self.currency_rate
                )
                min_price = int(
                    data["priceModule"]["minActivityAmount"]["value"]
                    * self.currency_rate
                )
            except:
                try:
                    max_price = int(
                        data["priceModule"]["maxAmount"]["value"] * self.currency_rate
                    )
                    min_price = int(
                        data["priceModule"]["minAmount"]["value"] * self.currency_rate
                    )
                except:
                    max_price = None
                    min_price = None

            try:
                discount_rate = float(data["priceModule"]["discount"] / 100)
            except:
                discount_rate = None

            try:
                delivery_date = data["shippingModule"]["freightCalculateInfo"][
                    "freight"
                ]["deliveryDate"]
                delivery_price = int(
                    float(
                        data["shippingModule"]["freightCalculateInfo"]["freight"][
                            "freightAmount"
                        ]["value"]
                        * self.currency_rate
                    )
                )
            except:
                delivery_date = None
                delivery_price = None

            try:
                image_path_list = list(data["imageModule"]["imagePathList"])
            except:
                image_path_list = []

            # バリエーション情報の取得
            sku_property_list = []
            if data["skuModule"].get("productSKUPropertyList"):
                for sku_property in data["skuModule"]["productSKUPropertyList"]:
                    try:
                        if (
                            sku_property.get("skuPropertyId") == 200007763
                        ):  # shipping from情報は収集しない
                            print("shipping from is skip")
                            continue
                        property_value_list = []
                        if sku_property.get("skuPropertyValues"):
                            for property_value in sku_property["skuPropertyValues"]:
                                property_value_list.append(
                                    dict(
                                        property_name=property_value.get(
                                            "propertyValueName"
                                        ),
                                        property_image_url=property_value.get(
                                            "skuPropertyImagePath"
                                        ),
                                    )
                                )
                        sku_property_list.append(
                            dict(
                                property_name=sku_property.get("skuPropertyName"),
                                property_values=property_value_list,
                            )
                        )
                    except Exception as e:
                        logger.warning(f"sku_property error: {e}")

            # 仕様
            specs = []
            if data["specsModule"].get("props"):
                for spec in data["specsModule"]["props"]:
                    try:
                        specs.append(
                            dict(name=spec["attrName"], value=spec["attrValue"])
                        )
                    except Exception as e:
                        logger.warning(f"get spec error: {e}")

            return AliexpressItem(
                name=data["titleModule"]["subject"],
                max_price=max_price,
                min_price=min_price,
                delivery_date=datetime.datetime.strptime(delivery_date, "%Y-%m-%d")
                if delivery_date
                else None,
                delivery_price=delivery_price,
                sku_property_json=json.dumps(sku_property_list, ensure_ascii=False),
                thumbnail_url=image_path_list[0],
                image_urls=",".join(image_path_list),
                specs=specs,
                product_id=str(data["storeModule"]["productId"]),
                average_star=float(
                    data["titleModule"]["feedbackRating"]["averageStar"]
                ),
                trade_count=int(data["titleModule"]["tradeCount"]),
                favorite_count=int(data["actionModule"]["itemWishedCount"]),
                discount_rate=discount_rate,
            )

        except Exception as e:
            logger.error(e)
            raise Exception(f"extract error: {e}")
