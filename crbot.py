from pyrogram import Client, filters
from configparser import ConfigParser
from binance.enums import *
from binance.client import Client as cl
from decimal import Decimal
import config
import json
import requests
import re
import datetime
import sqlite3
import pandas as pd
import time



bot = config.bot


# wlist = ['BTCUSD', 'ETHUSD', 'BNBUSD']
# admin = [5564551967]

cli = cl(config.apiKey,config.apiSecret)
print("logged in")
app = config.app
app.start()


# CHANGE TH
copyfrom = config.copyfrom
copyto = config.copyto


@app.on_message(filters.chat(copyfrom))
async def get_messages(client, message):
    final = 0
    if message.chat.id == copyfrom[0]:
        file = open('config.txt', 'r').read().splitlines()
        #get_pair = [x for x in file if re.match(f"{x}", message.text)]
        #print(get_pair)
        exchange_info = cli.get_exchange_info()
        gp = [s['symbol'] for s in exchange_info['symbols'] if re.match(f'(?i){s["symbol"]}|#{s["symbol"]}|{s["baseAsset"]}/{s["quoteAsset"]}|#{s["baseAsset"]}/{s["quoteAsset"]}', message.text)]
        try:
            pair = gp[0]
            if pair in file:
                print("BLACKLISTED PAIR")
            else:
                if "buy" in message.text or "BUY" in message.text or "long" in message.text or "LONG" in message.text or "Long" in message.text or "Buy" in message.text:
                    print(pair)
                    ##await bot.send_message(copyto, message.text)
                    await buy(pair)
                    ##await updater(pair)
                elif "sell" in message.text or "SELL" in message.text or "short" in message.text or "SHORT" in message.text or "Short" in message.text or "Sell" in message.text:
                    print(pair)
                    ##await bot.send_message(copyto, message.text)
                    await sell(pair)
                    ##await updater(pair)
                else:
                    print("none")
                    return final
        except IndexError:
            return final
    else:
        print("sorry")


async def sell(pair):
    print("x")

    qtty = quantitycal(symbol=pair, investment=config.investment)
    print(qtty)
    tickers = cli.get_symbol_ticker(symbol=pair)
    num_a = float(tickers["price"])
    print("QAUNTITY", qtty)
    order = cli.futures_create_order(
        symbol=f'{pair}',
        side='SELL',
        type='MARKET',
        quantity=qtty)
    print(order)
    print(num_a)
    vat = num_a + (num_a * 1 / 100)
    sl = vat
    print(sl)
    vat2 = num_a - (num_a * 0.6 / 100)
    tp = vat2
    print(tp)
    ## STOP LOSS
    buy_stop_market = cli.futures_create_order(
        symbol=pair,
        side='BUY',
        positionSide='SHORT',
        type='STOP_MARKET',
        stopPrice=sl,
        closePosition=True,
        timeInForce='GTE_GTC',
        workingType='MARK_PRICE',
        priceProtect=True
    )
    print(buy_stop_market)
    ## TAKE PROFIT
    buy_gain_market = cli.futures_create_order(
        symbol=pair,
        side='BUY',
        positionSide='SHORT',
        type='TAKE_PROFIT_MARKET',
        stopPrice=tp,
        closePosition=True,
        timeInForce='GTE_GTC',
        workingType='MARK_PRICE',
        priceProtect=True
    )
    print(buy_gain_market)

balance = cli.get_asset_balance(asset='BTC')
balance2 = cli.get_asset_balance(asset='USDT')
# info = cli.get_account()
# print(info)
# print(balance)
# print(balance2)


async def buy(pair):
    print("x")
    qtty = quantitycal(symbol=pair, investment=config.investment)
    print(qtty)
    tickers = cli.get_symbol_ticker(symbol=pair)
    num_a = float(tickers["price"])
    order = cli.create_order(
        symbol=f'{pair}',
        side='BUY',
        type='MARKET',
        timeInForce='GTE_GTC',
        quantity=qtty)
    print(order)
    print(num_a)
    getn = str(num_a)[::-1].find('.')
    print(getn)
    vat = num_a - (num_a * 1 / 100)
    sl = round(vat, getn)
    print(sl)
    vat2 = num_a + (num_a * 0.6 / 100)
    tp = round(vat2, getn)
    print(tp)
    ## STOP LOSS
    sell_stop_market = cli.futures_create_order(
        symbol=pair,
        side='SELL',
        positionSide='LONG',
        type='STOP_MARKET',
        stopPrice=sl,
        closePosition=True,
        timeInForce='GTE_GTC',
        workingType='MARK_PRICE',
        priceProtect=True
    )
    print(sell_stop_market)
    ## TAKE PROFIT
    sell_gain_market = cli.futures_create_order(
        symbol=pair,
        side='SELL',
        positionSide='LONG',
        type='TAKE_PROFIT_MARKET',
        stopPrice=tp,
        closePosition=True,
        timeInForce='GTE_GTC',
        workingType='MARK_PRICE',
        priceProtect=True
    )
    print(sell_gain_market)


def pricecalc(symbol, limit):
    raw_price = float(cli.get_symbol_ticker(symbol=symbol)['price'])
    dec_len = len(str(raw_price).split('.')[1])
    price = raw_price * limit
    return round(price, dec_len)


def rround(lotsize):
    splitted = str(lotsize).split('.')
    if float(splitted[0]) == 1:
        return 0
    else:
        return len(splitted[1])


def quantitycal(symbol, investment):
    info = cli.get_symbol_info(symbol=symbol)
    lotsize = float([i for i in info['filters'] if i['filterType'] == 'LOT_SIZE'][0]['minQty'])
    if symbol == 'BTCUSDT':
        price = float(cli.get_symbol_ticker(symbol=symbol)['price'])
        qty = round(investment / price, 5)

    else:
        price = float(cli.get_symbol_ticker(symbol=symbol)['price'])
        print(price)
        qty = round(investment/price, rround(lotsize))
    return qty

# qtty = quantitycal(symbol='ETHUSDT', investment=config.investment)
# print("QAUNTITY", qtty)


async def updater(pair):
    i = 0
    num_a = float(17813)
    while True:
        if i < 5:
            tickers = cli.get_symbol_ticker(symbol=pair)
            num_b = float(tickers["price"])
            numm = ((num_a - num_b) / num_b) * 100
            print(int(numm))
            print(tickers["price"])
            i += 1
            continue

        print("ok")
        break


print("Bot started")
bot.run()