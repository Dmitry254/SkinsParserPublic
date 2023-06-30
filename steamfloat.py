import requests
import json
import traceback


url = "https://partner.steam-api.com/IEconMarketService/GetPopular/v1/?"
api = requests.get(url)
data = json.loads(api.apparent_encoding)
print(data)


def count_trades():
    text = ""
    try:
        days_list = ["Вчера", "Сегодня"]
        for day_info in days_list:
            current_day = int(datetime.today().strftime("%d")) - 1 + days_list.index(day_info)
            text += day_info + '\n'
            for api_key in api_keys:
                bot_number = api_keys.index(api_key) + 1
                buy_count = 0
                sell_count = 0
                current_year = int(datetime.today().strftime("%Y"))
                current_mount = int(datetime.today().strftime("%m"))
                date = datetime(current_year, current_mount, current_day).timestamp()
                url = f"https://market.csgo.com/api/v2/history?key={api_key}&date={date}"
                result = requests.get(url)
                data = json.loads(result.text)
                for item in reversed(range(len(data['names_list']))):
                    if data['names_list'][item]['event'] == "buy" and data['names_list'][item]['stage'] == "2":
                        buy_count += 1
                    if data['names_list'][item]['event'] == "sell" and data['names_list'][item]['stage'] == "2":
                        sell_count += 1
                text += f"Бот {bot_number}: покупок {buy_count}, продаж {sell_count}\n"
        return text
    except:
        traceback.print_exc()
        return "Ошибочка, попроси ещё раз"
