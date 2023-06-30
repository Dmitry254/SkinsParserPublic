import json
import traceback
import time
from json import JSONDecodeError
import random

import requests
import telebot  # pip install PyTelegramBotAPI
from key1 import api_tg, api_keys
from datetime import datetime, timedelta

try:
    bot = telebot.TeleBot(api_tg)
except:
    traceback.print_exc()
    pass


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        user_markup = telebot.types.ReplyKeyboardMarkup(True)
        user_markup.row('/trades', '/balances', '/test')
        bot.send_message(message.chat.id, "Что делаем?", reply_markup=user_markup)
    except:
        traceback.print_exc()
        pass


@bot.message_handler(commands=['trades'])
def trades_message(message):
    try:
        trades_info = count_trades()
        bot.send_message(message.chat.id, trades_info)
    except:
        traceback.print_exc()
        pass


@bot.message_handler(commands=['balances'])
def balances_message(message):
    try:
        balances_info = get_balances()
        bot.send_message(message.chat.id, balances_info)
    except:
        traceback.print_exc()
        pass


@bot.message_handler(commands=['test'])
def test_message(message):
    try:
        problem = test_online()
        bot.send_message(message.chat.id, problem)
    except:
        traceback.print_exc()
        pass


def count_trades():
    text = ""
    count_bots = 0
    total_bots = len(api_keys)
    try:
        days_list = ["Вчера", "Сегодня"]
        for day_info in days_list:
            current_day = int((datetime.today() + timedelta(days=days_list.index(day_info)-1)).strftime("%d"))
            current_month = int((datetime.today() + timedelta(days=days_list.index(day_info) - 1)).strftime("%m"))
            current_year = int((datetime.today() + timedelta(days=days_list.index(day_info) - 1)).strftime("%Y"))
            text += day_info + '\n'
            while count_bots != total_bots:
                try:
                    api_key = api_keys[count_bots]
                    bot_number = count_bots + 1
                    buy_count = 0
                    sell_count = 0
                    date = datetime(current_year, current_month, current_day).timestamp()
                    url = f"https://market.csgo.com/api/v2/history?key={api_key}&date={date}"
                    result = requests.get(url)
                    data = json.loads(result.text)
                    for item in reversed(range(len(data['data']))):
                        if data['data'][item]['event'] == "buy" and data['data'][item]['stage'] == "2":
                            buy_count += 1
                        if data['data'][item]['event'] == "sell" and data['data'][item]['stage'] == "2":
                            sell_count += 1
                    text += f"Бот {bot_number}: покупок {buy_count}, продаж {sell_count}\n"
                    count_bots += 1
                except JSONDecodeError:
                    pass
            count_bots = 0
        return text
    except:
        traceback.print_exc()
        return "Неизвестная ошибка"


def get_balances():
    count_bots = 0
    total_bots = len(api_keys)
    try:
        text = ""
        while count_bots != total_bots:
            try:
                key = api_keys[count_bots]
                item_count = 0
                item_sum = 0
                url = f"https://market.csgo.com/api/v2/get-money?key={key}"
                api = requests.get(url)
                data = json.loads(api.text)
                url1 = f"https://market.csgo.com/api/v2/items?key={key}"
                api1 = requests.get(url1)
                data1 = json.loads(api1.text)
                if data1['items']:
                    for item in data1['items']:
                        if item['status'] == "1":
                            item_count += 1
                            item_sum += item['price'] * 0.95
                item_sum = int(item_sum)
                text += f"На {api_keys.index(key) + 1} боте {data['money']}р.\n Продаётся {item_count} вещей на {item_sum}р.\n"
                if key != api_keys[-1]:
                    text += "- " * 27 + "\n"
                count_bots += 1
            except JSONDecodeError:
                pass
        return text
    except:
        traceback.print_exc()
        return "Неизвестная ошибка"


def test_online():
    count_bots = 0
    total_bots = len(api_keys)
    try:
        text = ""
        while count_bots != total_bots:
            api_key = api_keys[count_bots]
            try:
                url = f"https://market.csgo.com/api/v2/test?key={api_key}"
                api = requests.get(url)
                data = json.loads(api.text)
                if data['success']:
                    tests = list(data['status'].values())
                    if False in tests:
                        text += f"Есть проблема на {api_keys.index(api_key) + 1} боте\n"
                count_bots += 1
            except JSONDecodeError:
                pass
        if "проблема" in text:
            return text
        else:
            return "Всё хорошо"
    except:
        traceback.print_exc()
        return "Неизвестная ошибка"


def random_no():
    no_text = random.choice(["Неа"])
    return no_text


try:
    bot.polling(none_stop=True, interval=0)
except:
    traceback.print_exc()
    time.sleep(60)
    pass
