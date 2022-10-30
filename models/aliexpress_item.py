import datetime


class AliexpressItem:
    def __init__(
        self,
        name: str = None,
        max_price: int = None,
        min_price: int = None,
        image_urls: list = None,
        specs: list = None,
        average_star: float = None,
        trade_count: int = None,
        product_id: str = None,
        url: str = None,
        delivery_price: int = None,
        delivery_date=None,
        thumbnail_url: str = None,
        sku_property_json: str = None,
        discount_rate: float = None,
        favorite_count: int = None,
    ):
        self.name = name
        self.max_price = max_price
        self.min_price = min_price
        self.thumbnail_url = thumbnail_url
        self.image_urls = image_urls
        self.specs = specs
        self.average_star = average_star
        self.trade_counnt = trade_count
        self.product_id = product_id
        self.url = url
        self.delivery_date = delivery_date
        self.delivery_price = delivery_price
        self.sku_property_json = sku_property_json
        self.favorite_count = favorite_count
        self.discount_rate = discount_rate

    def to_dict(self):
        return self.__dict__.copy()

    def merge(self, item):
        for key, value in self.__dict__.items():
            if item.__dict__[key] is None:
                continue
            self.__dict__[key] = item.__dict__[key]
