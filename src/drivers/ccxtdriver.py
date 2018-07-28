import asyncio
import os
import sys
import uuid
import threading, queue
from time import sleep
import datetime, time
import pprint
import copy

import sys
sys.path.append('..')

#from owncommon.messages import Order, PairBalance, Tick, Balance, Error, OrderBook


pp = pprint.PrettyPrinter(indent=4)

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

import ccxt.async as ccxt  # noqa: E402

TIMEOUT = 5  # seconds
TICK_TIMER = 15
OD_TICK_TIMER = 10
BALANCE_TICK_TIMER = 30
TRADE_TICK_TIMER = 5
INFO_TIMER = 30

class CxxtDriver(threading.Thread):

    def __init__(self, exchange_id, config):
        threading.Thread.__init__(self)

        self.ob_constant = OD_TICK_TIMER
        self.bl_constant = BALANCE_TICK_TIMER
        self.trade_constant = TRADE_TICK_TIMER

        self.stop_tick_time = datetime.datetime.now() + datetime.timedelta(seconds=TICK_TIMER)
        self.orderbook_tick_time = datetime.datetime.now() + datetime.timedelta(seconds=self.ob_constant)
        self.balance_tick_time = datetime.datetime.now() + datetime.timedelta(seconds=self.bl_constant)
        self.trade_tick_time = datetime.datetime.now() + datetime.timedelta(seconds=self.trade_constant)
        self.info_tick_time = datetime.datetime.now() +  datetime.timedelta(seconds=INFO_TIMER)



        self.config = config
        self.orderbook_count = 0
        self.pair_info = dict()

        self.exhange = exchange_id
        self.is_auth = False
        self.name = '[ccxt %s]' % self.exhange
        self.pair_list = set()

        if self.exhange == 'liqui':
            self.ob_constant = 30
            self.bl_constant = 60

        self.ccxt_in_queue = self.config['in_queue']
        self.ccxt_out_queue = self.config['out_queue']

        #self.pair_list = self.config['pairs']


        # for i in self.config['pairs']:
        #     i['balance_tick'] = True
        #     self.pair_list.add( i['name'] )

        auth = {}
        if 'auth' in self.config.keys():
            auth = self.config['auth']
            self.is_auth = True
            self.name = '[ccxt %s %s*]' % (self.exhange, auth['apiKey'][:4])
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if self.exhange == 'hitbtc':
            loop.create_task(self.run_loop(ccxt.hitbtc( auth )))
        elif self.exhange == 'coinmarketcap':
            loop.create_task(self.run_loop(ccxt.coinmarketcap()))
        elif self.exhange == 'binance':
            loop.create_task(self.run_loop(ccxt.binance( auth )))
        elif self.exhange == 'bitmex':
            loop.create_task(self.run_loop(ccxt.bitmex(auth)))
        elif self.exhange == 'huobipro':
            loop.create_task(self.run_loop(ccxt.huobipro()))
        elif self.exhange == 'liqui':
            loop.create_task(self.run_loop(ccxt.liqui(auth)))
        elif self.exhange == 'bitfinex2':
            loop.create_task(self.run_loop(ccxt.bitfinex2( auth )))
        elif self.exhange == 'bitfinex':
            loop.create_task(self.run_loop(ccxt.bitfinex( auth )))
        elif self.exhange == 'okex':
            loop.create_task(self.run_loop(ccxt.okex( auth )))
        elif self.exhange == 'kucoin':
            loop.create_task(self.run_loop(ccxt.kucoin( auth )))
        elif self.exhange == 'bittrex':
            loop.create_task(self.run_loop(ccxt.bittrex( auth )))
        elif self.exhange == 'qryptos':
            loop.create_task(self.run_loop(ccxt.qryptos( auth )))
        elif self.exhange == 'kraken':
            loop.create_task(self.run_loop(ccxt.kraken( auth )))

        loop.run_forever()



    def get_active_symbols(self, exchange):
        return [symbol for symbol in exchange.symbols if self.is_active_symbol(exchange, symbol)]


    def is_active_symbol(self, exchange, symbol):

        return ('.' not in symbol) and (('active' not in exchange.markets[symbol]) or (exchange.markets[symbol]['active']))


    async def fetch_ticker(self, exchange, symbol):

        order_time = datetime.datetime.today().replace(hour=13, minute=40)
        order_time = time.mktime(order_time.timetuple())

        to_sen_message = None
        try:
            ticker = await exchange.fetch_ticker(symbol)
        except Exception as e:
            print('[ccxt] ERROR',exchange.id, symbol, 'tick', e)
            to_sen_message = {'message': 'error', 'exchange':exchange.id, 'type':'tick', 'symbol':symbol, 'error': e}
        else:
            to_sen_message = {'message': 'tick', 'exchange':exchange.id, 'symbol':symbol, 'tick': ticker}


        if to_sen_message:
            self.ccxt_out_queue.put(to_sen_message)

        return ticker

    async def open_order(self, exchange, order, return_queue):
        print(self.name, order.symbol, 'executing', order.get_uuid(), order.get_status()['side'], order.amount)

        if 'lot' in self.pair_info[order.symbol]:

            lot = self.pair_info[order.symbol]['lot']

            if lot != 1.0:
                old_amount =  order.amount

                a = order.amount / lot
                first_part = str(a).split('.')[0]

                order.amount = int(first_part)*lot
                order.amount = round(order.amount, 8)

                print(self.name, order.symbol, order.get_uuid(), 'order amount', old_amount, 'rounded to', order.amount, 'by', self.pair_info[order.symbol]['lot'] )
                print(self.name, order.symbol, order.get_uuid(), order.side ,order.amount, order.price )

        try:
            if exchange.id in ['liqui','bittrex','kucoin']:
                # createOrder (symbol, type, side, amount[, price[, params]])
                if order.side == 'buy':
                    #order_callback = await exchange.createOrder(symbol=order.symbol, type='limit',side='buy', amount=order.amount, price=order.price)
                    order_callback = await exchange.create_limit_buy_order(order.symbol, order.amount, order.price)
                elif order.side == 'sell':
                    order_callback = await exchange.create_limit_sell_order(order.symbol, order.amount, order.price)

            elif  exchange.id == 'okex':
                if order.side == 'buy':
                    order_callback = await exchange.createMarketBuyOrder (order.symbol,  None, {'cost': order.amount * order.price * 1.1})
                elif order.side == 'sell':
                    order_callback = await exchange.createMarketSellOrder (order.symbol,  order.amount)

            else:
                if order.side == 'buy':
                    order_callback = await exchange.createMarketBuyOrder(symbol=order.symbol, amount=order.amount)
                elif order.side == 'sell':
                    order_callback = await exchange.createMarketSellOrder(symbol=order.symbol, amount=order.amount)



        except Exception as e:
            print('[ccxt]', exchange.id, order.symbol, e)
        else:
            print('[ccxt]', '[OK]', exchange.id, order.symbol, order.side, order.uuid, order_callback['id'])

        order.status = 'created'
        return_queue.put(order)

        pass

    async def fetch_balance(self, exchange, symbol):
       
        to_sen_message = None
        if self.is_auth:

            try:
                balance = await exchange.fetch_balance()

            except Exception as e:
                print('[ccxt]', exchange.id, symbol, 'balance', e)
                to_sen_message = {'message': 'error', 'type':'balcance', 'exchange':exchange.id, 'symbol':symbol, 'error': e}
            else:
                t, b = symbol.split('/')
                if t in balance.keys():
                    to_sen_message = {'message': 'bl', 'account':self.config['auth']['apiKey'][:4]+'*', 'exchange':exchange.id, 'symbol':t, 'balance': balance[t]}
                    self.ccxt_out_queue.put(to_sen_message)

                if b in balance.keys():
                    to_sen_message = {'message': 'bl', 'account':self.config['auth']['apiKey'][:4]+'*', 'exchange':exchange.id, 'symbol':b, 'balance': balance[b]}
                    self.ccxt_out_queue.put(to_sen_message)
        print(to_sen_message)
        return balance

    async def fetch_orderbook(self, exchange, symbol):

        to_sen_message = {}
        try:
            orderbook = await exchange.fetch_order_book(symbol, 20)
        except Exception as e:
            print('[ccxt] ERROR',exchange.id, symbol, 'order_book', e)
            to_sen_message = {'message': 'error', 'exchange':exchange.id, 'symbol':symbol, 'type':'order_book', 'error':  e  }
        else:
            to_sen_message = {'message':'ob', 'exchange':exchange.id, 'symbol':symbol, 'order_book': orderbook}

        if to_sen_message:
            self.ccxt_out_queue.put(to_sen_message)

        return orderbook

    async def fetch_trades(self, exchange, symbol):

        try:
            sincet = int(time.time())
            trades = await exchange.fetch_trades ( symbol, since=sincet  )

        except Exception as e:
            print(self.name, 'ERROR',exchange.id, symbol, 'trades', e)
        else:
            
            for i in trades:
                print(self.name, 'trade', i['symbol'], i['datetime']  )

            #print(trades)
            pass

        return trades


    async def run_loop(self, exchange):

        print(self.name, 'starting loop')

        await exchange.load_markets()
        
        # self.ccxt_out_queue.put( {'message': 'active_symbols', 
        #                           'exchange':exchange.id, 
        #                           'active_symbols': self.get_active_symbols(exchange) }  )

        
        symbols_to_load = self.get_active_symbols(exchange)
        # print(self.name, self.config['mode'], len(symbols_to_load), 'symbols', exchange.rateLimit/1000 )
        
        sleep_in_pairs = exchange.rateLimit / 1000

        while True:

            if self.is_auth:
                '''loop for any symbol to find queue'''
                
                try:
                    message = self.ccxt_in_queue.get_nowait()
                except queue.Empty:
                    pass
                else:
                    if message['command'] == 'open_order':
                        print(self.name, 'open_order', exchange.id)
                        await self.open_order(exchange, message['order'], i['extern_exchange']['commands_return'])


            # =======================
            # for Tick
            # =======================
            # if 'tick' in self.config['mode']:
            #     if datetime.datetime.now() > self.stop_tick_time:
            #         self.stop_tick_time = datetime.datetime.now() + datetime.timedelta(seconds=TICK_TIMER)

            #         input_coroutines = [self.fetch_ticker(exchange, symbol) for symbol in symbols_to_load]
            #         tickers = await asyncio.gather(*input_coroutines, return_exceptions=True)

            #         for ticker, symbol in zip(tickers, symbols_to_load):
            #             if not isinstance(ticker, dict):
            #                 print(self.name, 'tick', exchange.name, symbol, ticker)

            if self.is_auth:
                # =======================
                # for Balance
                # =======================
                if datetime.datetime.now() >  self.balance_tick_time:
                    self.balance_tick_time = datetime.datetime.now() + datetime.timedelta(seconds=self.bl_constant)

                    bl_coroutines = []
                    for si in  symbols_to_load:
                        bl_coroutines.append( self.fetch_balance(exchange, si) )
                        sleep(sleep_in_pairs)
                    
                    ob = await asyncio.gather(*bl_coroutines, return_exceptions=True)

                    




            sleep(0.15)
