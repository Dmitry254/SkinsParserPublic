import requests
import json
from datetime import datetime


def check_history(api_key):
    now = datetime.now()
    time_end = datetime.now().timestamp()
    date = datetime(year=int(now.year)-1, month=int(now.month), day=int(now.day), hour=int(now.hour),
                    minute=int(now.minute), second=int(now.second)).timestamp()
    url_his = f"https://market.csgo.com/api/v2/history?key={api_key}&date={date}&date_end={time_end}"
    result = requests.get(url_his)
    data = json.loads(result.text)
    for item_his in reversed(range(len(data['data']))):
        try:
            if data['data'][item_his]['event'] == "sell":
                if "Galil AR" in data['data'][item_his]['market_hash_name']:
                    print(data['data'][item_his])
        except:
            continue


if __name__ == "__main__":
    api_key = ""
    check_history(api_key)
