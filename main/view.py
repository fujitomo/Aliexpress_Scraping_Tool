import datetime
import os
import re
import sys
import urllib.error
import urllib.request

import eel
import fire
import pandas as pd
# 環境変数(.env)の読み込み
from dotenv import load_dotenv

import desktop
import main.search as search
from common.logger import set_logger
from common.utility import now_timestamp, now_timestamp_jp
from engine.aliexpress import AliexpressScraping
from engine.aliexpress_requests import AliexpressRequests

app_name = "html"
end_point = "index.html"
size = (780, 700)

load_dotenv()

# プロジェクトルートをPATHに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


# ログ出力設定
logger = set_logger(__name__)

@ eel.expose
def selenium(url: str, page_limit: int = 5):
    try:
        logger.info(f"url: {url} | page_limit: {page_limit}")
        
        if not checkURL(url) :
            eel.view_log_js("入力したURLに問題があります。")
            eel.button_process_del()
            return
                 
        aliexpress = AliexpressScraping()
        items = aliexpress.fetch_items(url, page_limit)

        items_dict = []
        
        eel.view_log_js(f"{now_timestamp_jp()}アイテム情報のCSV情報出力開始")
        for item in items:
            items_dict.append(item.to_dict())
                
        df = pd.DataFrame.from_dict(items_dict, dtype=object)
        df.to_csv(f"item_{now_timestamp()}.csv", mode="w", encoding="utf-8_sig")
        eel.view_log_js(f"{now_timestamp_jp()}アイテム情報のCSV情報出力完了")
        
        eel.view_log_js(f"全ての処理が完了です。")
        # desktop.exit()
    except Exception as e:
        eel.view_log_js(f"{now_timestamp_jp()}[システムエラー]{e}")
    finally:
        eel.button_process_del()
        aliexpress.quit();

# URLチェック関数
def checkURL(url: str):

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
    
@ eel.expose
def requests(url: str, page_limit: int = 5):
    logger.info(f"url: {url} | page_limit: {page_limit}")
    aliexpress = AliexpressRequests()
    items = aliexpress.fetch_items(url, page_limit)

    items_dict = []
    for item in items:
        items_dict.append(item.to_d1ict())
    df = pd.DataFrame.from_dict(items_dict, dtype=object)
    df.to_csv(f"item_{now_timestamp()}.csv", mode="w", encoding="utf-8_sig")



#if __name__ == "__main__":
#    fire.Fire()
    
desktop.start(app_name, end_point, size)
# desktop.start(size=size,appName=app_name,endPoint=end_point)

