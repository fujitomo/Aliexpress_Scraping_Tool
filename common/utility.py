"""汎用機能

* 汎用関数

Todo:
    * なし

"""

# -*- coding: utf-8 -*-
import re
import urllib.error
import urllib.request
from datetime import datetime as dt
from urllib.request import HTTPError

import requests
from bs4 import BeautifulSoup as bs


def now_timestamp():
    """現在日付取得
    
    Returns:
    str: 現在日付
       
    """
    return dt.now().strftime("%Y-%m-%d_%H_%M_%S")


def now_timestamp_jp():
    """現在日付取得(日本語形式)
    
    Returns:
    str: 現在日付
       
    """
    return dt.now().strftime("%Y年%m月%d日%H時%M分%S秒：")

def fetch_currency_rate(base: str, to: str):
    """base通貨とto通貨の為替レートを取得する
    
    Attributes
    base: base通貨
    to: to通貨
 
    Returns:
      為替レート
       
    """
    res = requests.get("http://fx.mybluemix.net/")
    res.raise_for_status()
    res_dict = res.json()
    try:
        # return res_dict["result"]["rate"][base + to]
        return res_dict["rate"][base + to]
    except:
        raise Exception(f"exchange currency error: {base}->{to}")

