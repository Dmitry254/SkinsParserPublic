import requests
import json
import time


def set_pay_pass():
    url = f"https://market.csgo.com/api/v2/set-pay-password?&new_password={pay_pass}&key={old_acc_api}"
    buy_item_status = requests.get(url)
    buy_data = json.loads(buy_item_status.text)
    print(buy_data)


def transfer_money(balance):
    url = f"https://market.csgo.com/api/v2/money-send/{balance}/{new_acc_api}?pay_pass={pay_pass}&key={old_acc_api}"
    buy_item_status = requests.get(url)
    buy_data = json.loads(buy_item_status.text)
    print(buy_data)


if __name__ == "__main__":
    pay_pass = ""
    old_acc_api = ""
    new_acc_api = ""
    transfer_money("")
    # Сначала с какого аккаунта, потом на который аккаунт

"""
"""
