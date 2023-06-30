import json
import time
import psutil
import requests
import os
from datetime import datetime
from key import *


def count_trades():
    global buy_count
    global sell_count
    current_year = int(datetime.today().strftime("%Y"))
    current_mount = int(datetime.today().strftime("%m"))
    current_day = int(datetime.today().strftime("%d"))
    date = datetime(current_year, current_mount, current_day).timestamp()
    buy_count = 0
    sell_count = 0
    url = f"https://market.csgo.com/api/v2/history?key={api_key}&date={date}"
    result = requests.get(url)
    data = json.loads(result.text)
    for item in reversed(range(len(data['names_list']))):
        if data['names_list'][item]['event'] == "buy" and data['names_list'][item]['stage'] == "2":
            buy_count += 1
        if data['names_list'][item]['event'] == "sell" and data['names_list'][item]['stage'] == "2":
            sell_count += 1
    print(f"Получено трейдов: {buy_count}\nОтправлено трейдов: {sell_count}")


def check_trades():
    try:
        url = f"https://market.csgo.com/api/v2/trades/?key={api_key}"
        result = requests.get(url)
        trades_info = json.loads(result.text)
        return trades_info
    except:
        pass


def open_sda():
    info = check_trades()
    start = False
    close = False
    if info['success']:
        for item in range(len(info['trades'])):
            if info['trades'][item]['dir'] == 'in':
                start = True
    for process in psutil.process_iter():
        try:
            if process.name() == process_name:
                start = False
                close = True
                break
        except:
            continue
    if info['success'] and start:
        os.startfile(f"E:\SDA\{process_name}")
    if not info['success'] and close:
        os.system(f"TASKKILL /F /IM {process_name}")


if __name__ == "__main__":
    count_trades()
    while True:
        open_sda()
        time.sleep(5)
