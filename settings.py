#Logging
def logger_print(to_log):
    print(to_log)

def logger_log_to__file(to_log):
    import os
    log_file = open(os.path.join(os.getcwd(), 'vickirex.log'), 'a+')
    log_file.write(to_log)
    log_file.close()

logger_functions = [
    {
        'name': 'print',
        'enabled': True,
        'function': logger_print,
    },
    {
        'name': 'log to file',
        'enabled': True,
        'function': logger_log_to__file,
    }
]

#Twitter apis
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

#Bittrex api
bittrex_apikey = ""
bittrex_apisecret = ""


follow_list = [ "834940874643615744"] #bot twitter id

#rules
rules = [
    {
        'condition': '"ETHBTC" in {tweet} and "long" in {tweet}',
        'execute': {
            'market': 'BTC-ETH',
            'action': 'buy',
        }
    },
    {
        'condition': '"ETHBTC" in {tweet} and "short" in {tweet}',
        'execute': {
            'market': 'BTC-ETH',
            'action': 'sell',
        }
    }
]
