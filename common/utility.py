# -*- coding: utf-8 -*-
import re
import urllib.error
import urllib.request
from datetime import datetime as dt
from urllib.request import HTTPError

import requests
from bs4 import BeautifulSoup as bs


def now_timestamp():
    return dt.now().strftime("%Y-%m-%d_%H_%M_%S")


def now_timestamp_jp():
    return dt.now().strftime("%Y年%m月%d日%H時%M分%S秒：")


def list_to_bool(l: list):
    bool_list = []
    for item in l:
        bool_list.append(False if item == "0" or item == 0 else True)

    return bool_list


def create_proxy_dict(id, password, host, port, proxy_flg=True):
    if proxy_flg:
        proxy_url = f"http://{id}:{password}@{host}:{port}"
        return {"http": proxy_url, "https": proxy_url}
    else:
        return {}


def get_global_ip():
    # return socket.gethostbyname(socket.gethostname())
    try:
        res = requests.get("http://inet-ip.info/")
        soup = bs(res.text, "html.parser")
        return soup.select_one("table tbody tr td:nth-child(2)").text
    except Exception as e:
        print(e)
        return None


def split_list(l, n):
    """
    リストをサブリストに分割する
    :param l: リスト
    :param n: サブリストの要素数
    :return:
    """
    for idx in range(0, len(l), n):
        yield l[idx : idx + n]


def fetch_currency_rate(base: str, to: str):
    res = requests.get("http://fx.mybluemix.net/")
    res.raise_for_status()
    res_dict = res.json()
    try:
        # return res_dict["result"]["rate"][base + to]
        return res_dict["rate"][base + to]
    except:
        raise Exception(f"exchange currency error: {base}->{to}")


# URLチェック関数
def checkURL(url: str):

    if re.match(r"^https?:\/\/", "a"):
        try:
            response = urllib2.urlopen("1")
            response.close()
            return "OK"
        except urllib2.HTTPError as e:
            print("NotFound:  " + url)
            return False
        except urllib2.URLError as e:
            print("NotFound:  " + url)
            return False
    else:
        return False
