from loading import LoadSettigs, get_robot_settings
from deribit import Client
from base_classes import Order
from mysql_client import ClientDB


class Strategy:
    def __init__(self,
                 client: Client,
                 client_db: ClientDB) -> None:
        self.client = client
        self.client_db = client_db
        self.order = Order('', "buy", False, 0.0, 1000.0)
        self.gap, self.gap_ignore = get_robot_settings()

    def insert_order(self, order_info, price, amount):
        self.order.id = order_info["order_id"]
        self.order.type = order_info['direction']
        self.order.run = True
        self.order.price = price
        self.order.amount = amount
        self.client_db.insert(self.order.id, self.order.type, "open",
                              self.order.amount, self.order.price)

    def update_order(self, order_info, type):
        self.order.price = order_info['price']
        self.order.amount = order_info['amount']
        if (amount := order_info['filled_amount']) > 0:
            self.order.amount = amount
        self.client_db.update(order_info['order_id'],
                              type,
                              order_info['price'],
                              order_info['filled_amount'])

    def buy_orders(self, price, amount):
        order_info = self.client.buy("BTC-PERPETUAL", amount, "limit", False,
                                     price, True)
        self.insert_order(order_info, price, amount)

    def sell_orders(self, price, amount):
        order_info = self.client.sell("BTC-PERPETUAL", amount, "limit", False,
                                      price, True)
        self.insert_order(order_info, price, amount)

    def cancel_order(self, curr_price, direction, order):
        print(f'cancel order {direction}')
        self.client.cancel(self.order.id)
        self.update_order(order, 'cancelled')
        if direction == 'buy':
            price = curr_price-self.gap/2.0
            self.buy_orders(price, self.order.amount)
        else:
            price = curr_price+self.gap
            self.sell_orders(price, self.order.amount)

    def loop(self):
        while True:
            curr_price = self.client.get_mark_price()
            order = self.client.get_order_state(self.order.id)
            self.gap, self.gap_ignore = get_robot_settings()
            if order['order_state'] != 'filled':
                stop_buy_price = self.order.price + self.gap + self.gap_ignore
                stop_sell_price = self.order.price - self.gap - self.gap_ignore
                if self.order.type == 'buy' and curr_price > stop_buy_price:
                    self.cancel_order(curr_price, self.order.type, order)
                elif self.order.type == 'sell' and curr_price < stop_sell_price:
                    self.cancel_order(curr_price, self.order.type, order)
            else:
                print(f'{self.order.type} order ({self.order.id}) '
                      'is filled, open new order')
                self.update_order(order, 'filled')
                if self.order.type == 'buy':
                    self.sell_orders(curr_price+self.gap, self.order.amount)
                else:
                    self.buy_orders(curr_price-self.gap/2.0, self.order.amount)

    def run(self):
        price = self.client.get_mark_price()-self.gap/2.0
        self.buy_orders(price, self.order.amount)
        self.loop()


def main():
    settings = LoadSettigs()
    credentials = settings.get_credentials()
    db_settings = settings.get_db_settings()
    client_db = ClientDB(db_settings)
    client_db.create_db()
    client = Client(
                    credentials.client_id,
                    credentials.client_secret,
                    credentials.client_url)
    strategy = Strategy(client, client_db)
    strategy.run()


if __name__ == '__main__':
    main()
