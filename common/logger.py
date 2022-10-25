import os
import logging 
from datetime import datetime
import glob

LOG_FORMAT='%(asctime)s - %(levelname)s - %(filename)s - %(name)s - %(funcName)s - %(message)s'
LOG_DIR_NAME='logs'
MAX_LOG_COUNT=100

def set_logger(name):
    logger= logging.getLogger(name)
    logger.setLevel(logging.INFO)
        
    # LOGフォルダがない場合は作成
    if not os.path.exists(LOG_DIR_NAME):
        os.mkdir(LOG_DIR_NAME)
    
    # ログの設定
    now_time = datetime.now()
    formatter = logging.Formatter(LOG_FORMAT)
    
    # ファイル出力用のHandlerを設定
    fh = logging.FileHandler(filename=f'{LOG_DIR_NAME}/{now_time:log_%Y%m%d%H%M%S}.log',encoding="utf-8")
    fh.setFormatter(formatter)
    fh.setLevel=logging.INFO

    # コンソール出力用のHandlerを設定
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    sh.setLevel=logging.INFO

    # Logerに登録    
    logger.addHandler(fh)
    logger.addHandler(sh)
    
    return logger

def delete_backlog():
    # 過去ログは削除
    files=sorted(glob.glob(f'{LOG_DIR_NAME}/*'), key=lambda f: os.stat(f).st_mtime, reverse=False)
    for i,file in enumerate(files):
        os.remove(file)
        if i > len(files) - MAX_LOG_COUNT :
            break