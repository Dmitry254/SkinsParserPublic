import codecs
import requests
import re
import steampy
from steampy.client import SteamClient
from key import steam_api


def accept_gift_trades():
    account_login, account_password, mafile_path = search_file_and_names(username)
    steam_client = SteamClient(steam_api)
    data = steam_client.get_trade_offers(steam_api)
    for trade in data['response']['trade_offers_received']:
        if not trade['items_to_give']:
            steam_client.login(account_login, account_password, mafile_path)
            steam_client.accept_trade_offer(trade['tradeofferid'])


def search_file_and_names(username):
    file_path = f"C:\Bot\{username}"
    file = codecs.open(f"{file_path}\{username}.txt", mode='r', encoding='utf-8', errors='ignore')
    account_data = file.readline()
    account_login, account_password = account_data.split(':')[1:]
    account_login = re.sub(r'[^A-Za-z-0-9]', '', account_login)
    account_password = re.sub(r'[^A-Za-z-0-9-@]', '', account_password)
    mafile_path = f"{file_path}\{username}.mafile"
    file.close()
    return account_login, account_password, mafile_path


if __name__ == "__main__":
    username = ""
    accept_gift_trades(username)

