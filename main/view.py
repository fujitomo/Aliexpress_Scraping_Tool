"""UIからのコールされる処理

* END_POINTからコールされる
* config.iniで最大取得ページ数を設定可能

Todo:
    * URLチェックを細かく行う予定

"""
import configparser
import os
import re
import sys
import urllib.error
import urllib.request

import eel
import pandas as pd
# 環境変数(.env)の読み込み
from dotenv import load_dotenv

import desktop
from common.logger import set_logger
from common.utility import now_timestamp
from engine.aliexpress import AliexpressScraping
from engine.aliexpress_requests import AliexpressRequests

APP_NAME = "html"
END_POINT = "index.html"
CONFIG_FILE_PATH = "./config.ini"
SIZE = (780, 700)

load_dotenv()

# プロジェクトルートをATHに追加
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# ログ出力設定
logger = set_logger(__name__)

@eel.expose
def selenium(url: str):
    """selenium処理

    Attributes
       url: スクレイピング対象のURL(検索結果一覧ページ)
    """
    try:
        page_limit = 5
        is_file = os.path.isfile(CONFIG_FILE_PATH)

        if is_file:
            ini = configparser.ConfigParser()
            ini.read(CONFIG_FILE_PATH, "UTF-8")
            page_limit = int(ini["config"]["page_limit"])
        else:
            pass  # パスが存在しないかファイルではない

        logger.info(f"url: {url} | page_limit: {page_limit}")
        
        if not checkURL(url):
            eel.view_log_js("入力したURLに問題があります。")
            eel.button_process_del()
            return

        aliexpress = AliexpressScraping()
        items = aliexpress.fetch_items(url, page_limit)

        items_dict = []

        eel.view_log_js(f"{now_timestamp()}アイテム情報のCSV情報出力開始")
        for item in items:
            items_dict.append(item.to_dict())

            df = pd.DataFrame.from_dict(items_dict, dtype=object)
            df.to_csv(f"item_{now_timestamp()}.csv", mode="w", encoding="utf-8_sig")
            eel.view_log_js(f"{now_timestamp()}アイテム情報のCSV情報出力完了")

            eel.view_log_js(f"全ての処理が完了です。")
            # desktop.exit()

    except Exception as e:
        eel.view_log_js(f"{now_timestamp()}([システムエラー]{e}")
    finally:
        eel.button_process_del()
        aliexpress.quit()

def checkURL(url: str):
    """スクレイピング対象のURLかをチェック

    Attributes
       url: スクレイピング対象のURL(検索結果一覧ページ)
       
    Returns:
        bool:スクレイピング対象のURLの場合true、違う場合はfalse
    """
    if re.match(r"^https?:\/\/", url):
        try:
            response = urllib.request.urlopen(url)
            response.close()
            return "OK"
        except urllib.request.HTTPError as e:
            return False
        except urllib.request.URLError as e:
            return False
        except:
            return False
    else:
        return False


# @eel.expose
# def requests(url: str, page_limit: int = 5):
#     logger.info(f"url: {url} | page_limit: {page_limit}")
#     aliexpress = AliexpressRequests()
#     items = aliexpress.fetch_items(url, page_limit)

#     items_dict = []
#     for item in items:
#         items_dict.append(item.to_d1ict())
#     df = pd.DataFrame.from_dict(items_dict, dtype=object)
#     df.to_csv(f"item_{now_timestamp()}.csv", mode="w", encoding="utf-8_sig")


# if __name__ == "__main__":
#    fire.Fire()
desktop.start(APP_NAME, END_POINT, SIZE)
# desktop.start(size=size,appName=app_name,endPoint=end_point)
