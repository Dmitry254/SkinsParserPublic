import requests
import json
from datetime import datetime
import time
import pyotp
from key import api_bit, google_code

# get a token that's valid right now
my_secret = google_code
my_token = pyotp.totp.TOTP(my_secret).now()

url = f"https://bitskins.com/api/v1/get_all_item_prices/?api_key={api_bit}&code={my_token}"
url1 = f"https://bitskins.com/api/v1/get_price_data_for_items_on_sale/?api_key={api_bit}&code={my_token}"
api = requests.get(url1)
data = json.loads(api.text)
print(data)
for item in data['data']['items']:
    print(item)
# for item in range(len(data['prices'])):
#     if data['prices'][item]['instant_sale_price'] and data['prices'][item]['price']:
#         print(data['prices'][item])

