import time
import re
import json
import typing
from pprint import pprint
import datetime
import requests
from bs4 import BeautifulSoup as bs

from models.aliexpress_item import AliexpressItem
from common.logger import set_logger
from common.utility import *

logger = set_logger(__name__)

class AliexpressRequests():
    ALIEXPRESS_DOMAIN_URL = "https://ja.aliexpress.com"
    ALIEXPRESS_ITEM_URL = "https://ja.aliexpress.com/item/{product_id}.html"
    HEADERS = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
    }

    def __init__(self):
        # 為替レートを取得
        _currency_rate = fetch_currency_rate("USD", "JPY")
        if not _currency_rate:
            raise Exception("currency exchange error")
        self.currency_rate = _currency_rate
        
        
    def get_soup(self, url: str) -> bs:
        res = requests.get(url, headers=self.HEADERS)
        if not(300 > res.status_code >= 200):
            raise Exception(f"requests error: {url}")
        
        return bs(res.text, "html.parser")


    def get_item_data_dict(self, url: str) -> dict:
        res = requests.get(url, headers=self.HEADERS)
        if not(300 > res.status_code >= 200):
            raise Exception(f"requests error: {url}")
        
        m = re.search(r'data: ({[\s\S]*)csrfToken:', res.text)
        if m == None:
            raise Exception(f"window.runParams not found: {url}")
        data = m.group(1)
        
        try:
            return dict(
                data=json.loads(data[:data.rfind(",")])
            )
        except:
            raise Exception("json parse error")
        
    
    def find_all_product_ids(self, url: str) -> list:
        res = requests.get(url, headers=self.HEADERS)
        if not(300 > res.status_code >= 200):
            raise Exception(f"requests error: {url}")
        
        product_ids = re.findall(r',"productId":([0-9]*),"saleMode":', res.text)
        
        return product_ids


    def fetch_item(self, url: str) -> AliexpressItem:
        logger.info(f"fetch_item > url: {url}")
        item_dict = self.get_item_data_dict(url)
        item = self._extract_item_dict(item_dict)
        print(item.to_dict())
        # pprint(item)
        # with open("item_data_test.json", mode="w", encoding="utf-8_sig") as f:
        #     f.write(json.dumps(item, ensure_ascii=False))
        
        return item

        
    def fetch_items_url(self, url: str, page_limit: int=10) -> typing.List[AliexpressItem]:
        items = []
        for page in range(page_limit):
            product_ids = self.find_all_product_ids(f"{url}&page={page+1}")
            try:
                for product_id in product_ids:
                    items.append(
                        AliexpressItem(
                            url = self.ALIEXPRESS_ITEM_URL.format(product_id=product_id)
                            )
                        )
                #time.sleep(10)
            except Exception as e:
                logger.error(f"fetch item dict error:{e}")
                break
            
        return items
    
    
    def fetch_items(self, url: str, page_limit: int=10) -> typing.List[AliexpressItem]:
        items = self.fetch_items_url(url, page_limit)
        
        for item in items:
            if not item.url:
                logger.warning("url is not set")
                continue
            item.merge(self.fetch_item(item.url))
        
        return items
    
    
    def _extract_item_dict(self, item_dict: dict) -> AliexpressItem:
        data = item_dict.get("data")
        if not data:
            logger.error("data not found")
            raise Exception(f"extract error")
        try:
            try:
                max_price = int(data["priceModule"]["maxActivityAmount"]["value"] * self.currency_rate)
                min_price = int(data["priceModule"]["minActivityAmount"]["value"] * self.currency_rate)
            except:
                try:
                    max_price = int(data["priceModule"]["maxAmount"]["value"] * self.currency_rate)
                    min_price = int(data["priceModule"]["minAmount"]["value"] * self.currency_rate)
                except:
                    max_price = None
                    min_price = None

            try:
                discount_rate = float(data["priceModule"]["discount"] / 100)
            except:
                discount_rate = None

            try:
                delivery_date = data["shippingModule"]["freightCalculateInfo"]["freight"]["deliveryDate"]
                delivery_price = int(float(data["shippingModule"]["freightCalculateInfo"]["freight"]["freightAmount"]["value"] * self.currency_rate))
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
                        if sku_property.get("skuPropertyId") == 200007763: # shipping from情報は収集しない
                            print("shipping from is skip")
                            continue                
                        property_value_list = []
                        if sku_property.get("skuPropertyValues"):
                            for property_value in sku_property["skuPropertyValues"]:
                                property_value_list.append(
                                    dict(
                                        property_name = property_value.get("propertyValueName"),
                                        property_image_url = property_value.get("skuPropertyImagePath")
                                    )
                                )
                        sku_property_list.append(
                            dict(
                                property_name = sku_property.get("skuPropertyName"),
                                property_values = property_value_list
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
                            dict(
                                name = spec["attrName"],
                                value = spec["attrValue"]

                            )
                        )
                    except Exception as e:
                        logger.warning(f"get spec error: {e}")
            
            return AliexpressItem(
                name = data["titleModule"]["subject"], 
                max_price = max_price, 
                min_price = min_price,
                delivery_date = datetime.datetime.strptime(delivery_date, "%Y-%m-%d") if delivery_date else None,
                delivery_price = delivery_price,
                sku_property_json = json.dumps(sku_property_list, ensure_ascii=False),
                thumbnail_url = image_path_list[0],
                image_urls = ",".join(image_path_list), 
                specs = specs, 
                product_id = str(data["storeModule"]["productId"]),
                average_star = float(data["titleModule"]["feedbackRating"]["averageStar"]), 
                trade_count = int(data["titleModule"]["tradeCount"]),
                favorite_count = int(data["actionModule"]["itemWishedCount"]),
                discount_rate = discount_rate
            )
            
        except Exception as e:
            logger.error(e)
            raise Exception(f"extract error: {e}")