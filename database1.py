import sqlite3


class DB:
    def __init__(self):
        self.comm = sqlite3.connect('buyed_items_cs.db')
        self.c = self.comm.cursor()
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS buyed_items_cs(id float primary key, link text,
            name text, buy_price float, sold_price float, avg_price float)''')
        self.comm.commit()
        self.comm = sqlite3.connect('parsed_items_cs.db')
        self.c = self.comm.cursor()
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS parsed_items(id float primary key, link text,
            name text, buy_price float, avg_price float)''')
        self.comm.commit()

    def insert_buy_data(self, item_id, link, name, buy_price, sold_price, avg_price):
        self.c.execute('''INSERT INTO CompsProfit(item_id, link, name, buy_price, sold_price, avg_price) 
        VALUES (?, ?, ?, ?, ?, ?)''', (item_id, link, name, buy_price, sold_price, avg_price))
        self.comm.commit()

    def insert_parsed_data(self, item_id, link, name, buy_price, avg_price):
        self.c.execute('''INSERT INTO CompsProfit(item_id, link, name, buy_price, avg_price) 
        VALUES (?, ?, ?, ?, ?)''', (item_id, link, name, buy_price, avg_price))
        self.comm.commit()