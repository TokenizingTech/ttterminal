
from time import sleep
import threading, queue
import asyncio
import datetime
import json

from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, pyqtSignal

import ccxt.async as ccxt 

from .ccxtdriver import CxxtDriver

TIMEOUT = 5  # seconds
TICK_TIMER = 15
OD_TICK_TIMER = 10
BALANCE_TICK_TIMER = 5
TRADE_TICK_TIMER = 5
INFO_TIMER = 30

class DriverWorkerObject(QtCore.QObject):

    sig_balance = pyqtSignal(str)

    def __ini__(self):
        print(self.name, 'init')
    #     self.background_job()

    def get_active_symbols(self, exchange):
        return [symbol for symbol in exchange.symbols if self.is_active_symbol(exchange, symbol)]


    def is_active_symbol(self, exchange, symbol):

        return ('.' not in symbol) and (('active' not in exchange.markets[symbol]) or (exchange.markets[symbol]['active']))


    async def fetch_balance(self, exchange):
       
        to_sen_message = None
        if self.is_auth:

            try:
                balance = await exchange.fetch_balance()
                #print(balance.keys())

            except Exception as e:
                print(self.name, exchange.id, 'balance', e)
                to_sen_message = {'message': 'error', 'type':'balcance', 'exchange':exchange.id, 'error': e}
            else:
                for i in balance:
                    if i not in  ['info', 'free', 'used', 'total']:
                        to_sen_message = {'message': 'bl', 'account':self.config['auth']['apiKey'][:4]+'*', 'exchange':exchange.id, 'symbol':i, 'balance': balance[i]}
                        #print(to_sen_message)
                        self.sig_balance.emit( json.dumps(to_sen_message) )
                        #self.ccxt_out_queue.put(to_sen_message)
        return balance

    @QtCore.pyqtSlot()
    def background_job(self):

        self.ob_constant = OD_TICK_TIMER
        self.bl_constant = BALANCE_TICK_TIMER
        self.trade_constant = TRADE_TICK_TIMER

        self.stop_tick_time = datetime.datetime.now() + datetime.timedelta(seconds=TICK_TIMER)
        self.orderbook_tick_time = datetime.datetime.now() + datetime.timedelta(seconds=self.ob_constant)
        self.balance_tick_time = datetime.datetime.now() + datetime.timedelta(seconds=self.bl_constant)
        self.trade_tick_time = datetime.datetime.now() + datetime.timedelta(seconds=self.trade_constant)
        self.info_tick_time = datetime.datetime.now() +  datetime.timedelta(seconds=INFO_TIMER)

        

        self.ccxt_in_queue = self.config['in_queue']
        self.ccxt_out_queue = self.config['out_queue']

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
    
    async def run_loop(self, exchange):

        print(self.name, 'starting loop')

        await exchange.load_markets()

        
        #print(currencies)
        
        symbols_to_load = self.get_active_symbols(exchange)        
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
                    bl_coroutines.append( self.fetch_balance(exchange) )
                    ob = await asyncio.gather(*bl_coroutines, return_exceptions=True)
                                    



            #sleep(sleep_in_pairs)
            sleep(0.15)

