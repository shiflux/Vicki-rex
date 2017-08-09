import tweepy
import bittrex_api
from settings import *
from bittrex_api import Bittrex
import datetime
import os
import sys

from time import sleep

bt_api = None


def logger(info):
    string_to_log = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' ' + info + '\n'
    print(string_to_log)
    log_file = open(os.path.join(os.getcwd(), 'vickirex.log'), 'a+')
    log_file.write(string_to_log)
    log_file.close()


logger.functions = []


class VickiListener(tweepy.StreamListener):

    def on_status(self, status):
        logger("New Tweet! " + " / " + status.text)
        for rule in rules:
            if eval(rule['condition'].format(tweet='status.text')):
                execute_action(rule['execute'])

    def on_error(self, status):
        logger("Error " + str(status))
        if status == 401:
            logger("Unathorized")
            sys.exit()


def get_balance(currency):
    global bt_api
    response = bt_api.get_balance(currency)
    if response["success"]:
        return response["result"]["Balance"]
    else:
        return -1


def open_order(market, quantity, price, _type):
    logger("Opening order...")
    global bt_api
    if _type == 'buy':
        response = bt_api.buy_limit(market, quantity, price)
    elif _type == 'sell':
        response = bt_api.sell_limit(market, quantity, price)
    if response["success"]:
        logger('Order ' + _type +' placed. Quantity:  ' + str(quantity) + '. Price: ' + str(price))
    else:
        logger('Error placing ' + _type +' order. Quantity:  ' + str(quantity) + '. Price: ' + str(price) + ' ' + response['message'])
        return False
    return True


def cancel_open_orders(market):
    logger("Canceling open orders...")
    response = bt_api.get_open_orders(market)
    if len(response["result"]) is 0:
        return
    else:
        for r in response["result"]:
            logger("Canceling order" + r["OrderUuid"])
            bt_api.cancel(r["OrderUuid"])

def get_current_price(market, order_type):
    logger("Getting current price...")
    response = bt_api.get_orderbook(market, order_type)
    if response["result"] is None:
        return None
    logger("Current price is " + str(response["result"][0]["Rate"]))
    return response["result"][0]["Rate"]


def buy(market):
    currency = market.split('-')[0]
    cancel_open_orders(market)
    sleep(3)
    balance = get_balance(currency)
    while balance > 0:
        currentprice = get_current_price(market, bittrex_api.SELL_ORDERBOOK)
        if open_order(market, float("{0:.5f}".format((balance/currentprice)/1.0025)), currentprice, 'buy'):
            sleep(3)
            balance = get_balance(currency)
        else:
            return


def sell(market):
    currency = market.split('-')[1]
    cancel_open_orders(market)
    sleep(3)
    balance = get_balance(currency)
    while balance > 0:
        currentprice = get_current_price(market, bittrex_api.BUY_ORDERBOOK)
        if open_order(market, balance, currentprice, 'sell'):
            sleep(3)
            balance = get_balance(currency)
        else:
            return


def execute_action(execute):
    global bt_api
    if bt_api is None:
        bt_api = Bittrex(bittrex_apikey, bittrex_apisecret)

    if execute['action'] == 'buy':
        currency = execute['market'].split('-')[0]
        balance = get_balance(currency)
        if balance is not None and balance > 0:
            buy(execute['market'])
        else:
            logger('Invalid balance! ' + currency)
            return
    elif execute['action'] == 'sell':
        currency = execute['market'].split('-')[1]
        balance = get_balance(currency)
        if balance is not None and balance > 0:
            sell(execute['market'])
        else:
            logger('Invalid balance! ' + currency)
            return


def start():
    for lf in logger_functions:
        if lf['enabled']:
            logger.functions.append(lf['function'])
    logger("Starting bot")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    myVickiListener = VickiListener()
    myStream = tweepy.Stream(auth=api.auth, listener=myVickiListener)

    logger("Listening to " + str(follow_list))
    while True:
        try:
            myStream.filter(follow=follow_list)
        except KeyboardInterrupt:
            logger("Tuning off, interrupted.")
            myStream.disconnect()
            return
        except:
            logger("Unexpected error:" + str(sys.exc_info()[0]))
            continue

start()

