import asyncio
from typing import Optional, Any

import websockets
import json


def loop(api, request):
    response = asyncio.get_event_loop().run_until_complete(
        api(json.dumps(request)))
    return response


class Client:
    def __init__(self,
                 id: Optional[str] = None,
                 secret: Optional[str] = None,
                 url: Optional[str] = None
                 ) -> None:
        self.client_id = id
        self.client_secret = secret
        self.client_url = url
        self.json = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": None,
        }

    async def private_api(self, request):
        options: dict[str, Optional[str]] = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        self.json["method"] = "public/auth"
        self.json["params"] = options

        async with websockets.connect(self.client_url) as websocket:
            await websocket.send(json.dumps(self.json))
            while websocket.open:
                response = await websocket.recv()

                if "private/subscribe" in request:
                    await websocket.send(request)
                    while websocket.open:
                        response = await websocket.recv()
                        response = json.loads(response)
                        print(response)

                else:
                    await websocket.send(request)
                    response = await websocket.recv()
                    response = json.loads(response)
                    break
            return response

    async def public_api(self, request):
        async with websockets.connect(self.client_url) as websocket:
            await websocket.send(request)
            response = await websocket.recv()
            response = json.loads(response)
            return response

    async def public_sub(self, request):
        async with websockets.connect(self.client_url) as websocket:
            await websocket.send(request)
            while websocket.open:
                response = await websocket.recv()
                response = json.loads(response)
                print(response)

    def buy(self, instrument_name, amount, order_type, reduce_only,
            price=None, post_only=None):
        options: dict[str, Any] = {
            "instrument_name": instrument_name,
            "amount": amount,
            "type": order_type,
            "reduce_only": reduce_only
        }

        if price:
            options["price"] = price
        if post_only:
            options["time_in_force"] = "good_til_cancelled"
            options["post_only"] = post_only

        self.json["method"] = "private/buy"
        self.json["params"] = options
        res = loop(self.private_api, self.json)
        print(res)
        print('buy order price = ', res['result']['order']['price'])
        return res['result']['order']

    def sell(self, instrument_name, amount, order_type, reduce_only,
             price=None, post_only=None):
        options = {
            "instrument_name": instrument_name,
            "amount": amount,
            "type": order_type,
            "reduce_only": reduce_only,
        }

        if price:
            options["price"] = price
        if post_only:
            options["post_only"] = post_only

        self.json["method"] = "private/sell"
        self.json["params"] = options
        res = loop(self.private_api, self.json)
        print(res)
        if 'error' in res:
            print(res['error'])
        print('sell: ', res['result']['order']['price'])
        return res['result']['order']

    def edit(self, order_id, amount, price):
        options = {
            "order_id": order_id,
            "amount": amount,
            "price": price
        }

        self.json["method"] = "private/edit"
        self.json["params"] = options
        return loop(self.private_api, self.json)

    def cancel(self, order_id):
        options = {"order_id": order_id}
        self.json["method"] = "private/cancel"
        self.json["params"] = options
        return loop(self.private_api, self.json)

    def cancel_all(self):
        self.json["method"] = "private/cancel_all"
        return loop(self.private_api, self.json)

    def get_mark_price(self):
        options = {
            "instrument_name": "BTC-PERPETUAL",
            "depth": 1
        }
        self.json["method"] = "public/get_order_book"
        self.json["params"] = options
        result = loop(self.public_api, self.json)
        return float(result["result"]["mark_price"])

    def get_order_state(self, ordered_id):
        options = {"order_id": ordered_id}
        self.json["method"] = "/private/get_order_state"
        self.json["params"] = options
        res = loop(self.private_api, self.json)
        return res["result"]
