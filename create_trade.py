import codecs
import requests
import json
import re
import steampy
from steampy.client import SteamClient, Asset
from steampy.utils import GameOptions
from steampy.client import SteamClient
from key import steam_api


def check_trades():
    """
    Проверить есть ли активные трейды для подтверждения
    """
    url = f"https://market.csgo.com/api/v2/trade-request-give-p2p-all/?key={api_key}"
    result = requests.get(url)
    trades_info = json.loads(result.text)
    print(trades_info)
    if trades_info['offers']:
        create_trade(trades_info['offers']['hash'], trades_info['offers']['partner'], trades_info['offers']['token'],
                     trades_info['offers']['tradeoffermessage'], trades_info['offers']['items'])
    return trades_info


def create_trade(hash, partner, token, trade_offer_message, items):
    steam_client = SteamClient(steam_api)
    steam_client.login('MY_USERNAME', 'MY_PASSWORD', 'PATH_TO_STEAMGUARD_FILE')
    game = GameOptions.CS
    my_items = steam_client.get_my_inventory(game)
    partner_items = steam_client.get_partner_inventory(partner, game)
    my_first_item = next(iter(my_items.values()))
    partner_first_item = next(iter(partner_items.values()))
    my_asset = Asset(items[0]['assetid'], game)
    partner_asset = Asset(items[0]['assetid'], game)
    steam_client.make_offer([my_asset], [partner_asset], partner, trade_offer_message)


if __name__ == "__main__":
    api_key = ""
    check_trades()
    # {'success': True, 'trades': [{'dir': 'in', 'trade_id': '0', 'bot_id': '887818337', 'timestamp': 1611323660, 'secret': 'HUIH', 'nik': 'CS.FAIL CS.MONEY ITOR8842'}]}

