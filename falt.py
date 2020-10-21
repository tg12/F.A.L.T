'''THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE AND
NON-INFRINGEMENT. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR ANYONE
DISTRIBUTING THE SOFTWARE BE LIABLE FOR ANY DAMAGES OR OTHER LIABILITY,
WHETHER IN CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''

# Bitcoin Cash (BCH)   qpz32c4lg7x7lnk9jg6qg7s4uavdce89myax5v5nuk
# Ether (ETH) -        0x843d3DEC2A4705BD4f45F674F641cE2D0022c9FB
# Litecoin (LTC) -     Lfk5y4F7KZa9oRxpazETwjQnHszEPvqPvu
# Bitcoin (BTC) -      34L8qWiQyKr8k4TnHDacfjbaSqQASbBtTd

# contact :- github@jamessawyer.co.uk



# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE AND
# NON-INFRINGEMENT. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR ANYONE
# DISTRIBUTING THE SOFTWARE BE LIABLE FOR ANY DAMAGES OR OTHER LIABILITY,
# WHETHER IN CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

###### Dont forget to tip your server! 
###### Bitcoin Cash (BCH)   qpz32c4lg7x7lnk9jg6qg7s4uavdce89myax5v5nuk
###### Ether (ETH) -        0x843d3DEC2A4705BD4f45F674F641cE2D0022c9FB
###### Litecoin (LTC) -     Lfk5y4F7KZa9oRxpazETwjQnHszEPvqPvu
###### Bitcoin (BTC) -      14Dm7L3ABPtumPDcj3REAvs4L6w9YFRnHK

import traceback
import calendar
import datetime
import random
import time
import json
import requests
import math
import pandas
import numpy
from time import localtime, strftime
from numpy import NaN, Inf, arange, isscalar, asarray, array
import sys
from scipy import stats
import re


# PROGRAMMABLE VALUES, IG specific.
# SET INITIAL VARIABLES
orderType_value = "MARKET"
size_value = "1"
expiry_value = "DFB"
guaranteedStop_value = True
currencyCode_value = "GBP"
forceOpen_value = True


LITECOINEPICID = "CS.D.LTCUSD.TODAY.IP"
ESMAMARGREQ = 33                            # (50% for Crypto)
MARGINPROTECT = 250                         # No stupidly high pip limit per trade
MAXTRADES = int(int(size_value) * 5)        # Max Trades (total per point) Per Epic
PERCENTACCUSED = 85                         # How much of account to use
GREEDINDICATOR = 30                         # Dont hang onto profitable trades too long
SUPER_LOW_NEG_MARGIN = 100                  # Dont trust IG to take care of ESMA margins
b_REAL = False
b_Contrarian = False  # DO NOT SET
hacks_enabled = False

#CREDS###################################################################
LIVE_API_KEY = ''
LIVE_USERNAME = ""
LIVE_PASSWORD = ""
LIVE_ACC_ID = ""
##########################################################################
DEMO_API_KEY = ''
DEMO_USERNAME = ""
DEMO_PASSWORD = ""
DEMO_ACC_ID = ""
###########################################################################


if b_REAL:
    REAL_OR_NO_REAL = 'https://api.ig.com/gateway/deal'
    API_ENDPOINT = "https://api.ig.com/gateway/deal/session"
    API_KEY = LIVE_API_KEY
    data = {"identifier": LIVE_USERNAME, "password": LIVE_PASSWORD}
else:
    REAL_OR_NO_REAL = 'https://demo-api.ig.com/gateway/deal'
    API_ENDPOINT = "https://demo-api.ig.com/gateway/deal/session"
    API_KEY = DEMO_API_KEY
    data = {"identifier": DEMO_USERNAME, "password": DEMO_PASSWORD}

headers = {'Content-Type': 'application/json; charset=utf-8',
           'Accept': 'application/json; charset=utf-8',
           'X-IG-API-KEY': API_KEY,
           'Version': '2'
           }

r = requests.post(API_ENDPOINT, data=json.dumps(data), headers=headers)

headers_json = dict(r.headers)
CST_token = headers_json["CST"]
print(R"CST : " + CST_token)
x_sec_token = headers_json["X-SECURITY-TOKEN"]
print(R"X-SECURITY-TOKEN : " + x_sec_token)

# GET ACCOUNTS
base_url = REAL_OR_NO_REAL + '/accounts'
authenticated_headers = {'Content-Type': 'application/json; charset=utf-8',
                         'Accept': 'application/json; charset=utf-8',
                         'X-IG-API-KEY': API_KEY,
                         'CST': CST_token,
                         'X-SECURITY-TOKEN': x_sec_token}

auth_r = requests.get(base_url, headers=authenticated_headers)
d = json.loads(auth_r.text)

base_url = REAL_OR_NO_REAL + '/session'

if b_REAL:
    data = {
        "accountId": LIVE_ACC_ID,
        "defaultAccount": "True"}  # Main Live acc
else:
    data = {
        "accountId": DEMO_ACC_ID,
        "defaultAccount": "True"}  # Main Demo acc

auth_r = requests.put(
    base_url,
    data=json.dumps(data),
    headers=authenticated_headers)

# print("-----------------DEBUG-----------------")
# print("#################DEBUG#################")
# print(auth_r.status_code)
# print(auth_r.reason)
# print(auth_r.text)
# print("-----------------DEBUG-----------------")
# print("#################DEBUG#################")


##########################################################################
##########################END OF LOGIN CODE###############################
##########################END OF LOGIN CODE###############################
##########################END OF LOGIN CODE###############################
##########################END OF LOGIN CODE###############################
##########################################################################

def supres(
        low,
        high,
        min_touches=2,
        stat_likeness_percent=1.5,
        bounce_percent=5):
    """Support and Resistance Testing

    Identifies support and resistance levels of provided price action data.

    Args:
        low(pandas.Series): A pandas Series of lows from price action data.
        high(pandas.Series): A pandas Series of highs from price action data.
        min_touches(int): Minimum # of touches for established S&R.
        stat_likeness_percent(int/float): Acceptable margin of error for level.
        bounce_percent(int/float): Percent of price action for established bounce.

    ** Note **
        If you want to calculate support and resistance without regard for
        candle shadows, pass close values for both low and high.

    Returns:
        sup(float): Established level of support or None (if no level)
        res(float): Established level of resistance or None (if no level)
    """
    # Setting default values for support and resistance to None
    sup = None
    res = None

    # Identifying local high and local low
    maxima = high.max()
    minima = low.min()

    # Calculating distance between max and min (total price movement)
    move_range = maxima - minima

    # Calculating bounce distance and allowable margin of error for likeness
    move_allowance = move_range * (stat_likeness_percent / 100)
    bounce_distance = move_range * (bounce_percent / 100)

    # Test resistance by iterating through data to check for touches delimited
    # by bounces
    touchdown = 0
    awaiting_bounce = False
    for x in range(0, len(high)):
        if abs(maxima - high[x]) < move_allowance and not awaiting_bounce:
            touchdown = touchdown + 1
            awaiting_bounce = True
        elif abs(maxima - high[x]) > bounce_distance:
            awaiting_bounce = False
    if touchdown >= min_touches:
        res = maxima

    # Test support by iterating through data to check for touches delimited by
    # bounces
    touchdown = 0
    awaiting_bounce = False
    for x in range(0, len(low)):
        if abs(low[x] - minima) < move_allowance and not awaiting_bounce:
            touchdown = touchdown + 1
            awaiting_bounce = True
        elif abs(low[x] - minima) > bounce_distance:
            awaiting_bounce = False
    if touchdown >= min_touches:
        sup = minima
    return sup, res


def debug_info(err_str):
    # Standard debugging function, pass it a string
    # print("-----------------DEBUG-----------------")
    print("#################DEBUG##################")
    print(str(time.strftime("%H:%M:%S")) + ":!!!DEBUG!!!:" + str(err_str))
    print("#################DEBUG##################")
    # print("-----------------DEBUG-----------------")


def percentage(part, whole):
    return 100 * float(part) / float(whole)


def percentage_of(percent, whole):
    # percent should always be 20 for stocks
    # ESMA regulations calculating min stop loss (20% for stocks)
    return (percent * whole) / 100.0


def humanize_time(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)


def idTooMuchPositions(key, positionMap):
    if((key in positionMap) and (int(positionMap[key]) >= int(MAXTRADES))):
        return True
    else:
        return False


def all_same(items):
    return all(x == items[0] for x in items)


def try_market_order(epic_id, trade_direction, limit, stop_pips, positionMap):

    if trade_direction == "NONE":
        return None

    key = epic_id + '-' + trade_direction
    # print(str(key) + " has position of " + str(positionMap[key]))
    if idTooMuchPositions(key, positionMap):
        print(str(key) +
              " has position of " +
              str(positionMap[key]) +
              ", hence should not trade")
        return None

    no_trade_window()  # last chance to bail to avoid neg balance

    limitDistance_value = str(limit)  # Limit
    stopDistance_value = str(stop_pips)  # Stop

    ##########################################################################
    print(
        "Order will be a " +
        str(trade_direction) +
        " Order, With a limit of: " +
        str(limitDistance_value))
    print(
        "stopDistance_value for " +
        str(epic_id) +
        " will bet set at " +
        str(stopDistance_value))
    ##########################################################################

    # MAKE AN ORDER
    base_url = REAL_OR_NO_REAL + '/positions/otc'
    data = {
        "direction": trade_direction,
        "epic": epic_id,
        "limitDistance": limitDistance_value,
        "orderType": orderType_value,
        "size": size_value,
        "expiry": expiry_value,
        "guaranteedStop": guaranteedStop_value,
        "currencyCode": currencyCode_value,
        "forceOpen": forceOpen_value,
        "stopDistance": stopDistance_value}
    r = requests.post(
        base_url,
        data=json.dumps(data),
        headers=authenticated_headers)

    print("-----------------DEBUG-----------------")
    print("#################DEBUG#################")
    print(r.status_code)
    print(r.reason)
    print(r.text)
    print("-----------------DEBUG-----------------")
    print("#################DEBUG#################")

    d = json.loads(r.text)
    deal_ref = d['dealReference']
    time.sleep(1)
    # CONFIRM MARKET ORDER
    base_url = REAL_OR_NO_REAL + '/confirms/' + deal_ref
    auth_r = requests.get(base_url, headers=authenticated_headers)
    d = json.loads(auth_r.text)
    DEAL_ID = d['dealId']
    print("DEAL ID : " + str(d['dealId']))
    print(d['dealStatus'])
    print(d['reason'])

    if str(d['reason']) != "SUCCESS":
        print("some thing occurred ERROR!!")
        time.sleep(5)
        print("[+]!!!INFO!!!...Order failed, Check IG Status, Resuming...")
    else:
        print("[+]!!INFO!!...Yay, ORDER OPEN")
        time.sleep(3)


def main_trade_function(epic_id):

    position_base_url = REAL_OR_NO_REAL + "/positions"
    position_auth_r = requests.get(
        position_base_url, headers=authenticated_headers)
    position_json = json.loads(position_auth_r.text)

    positionMap = {}

    # print("-------------Position Info-------------")
    # print("#################DEBUG#################")
    # print(position_auth_r.status_code)
    # print(position_auth_r.reason)
    # print(position_auth_r.text)
    # print("-----------------DEBUG-----------------")
    # print("#################DEBUG#################")

    for item in position_json['positions']:
        direction = item['position']['direction']
        dealSize = item['position']['dealSize']
        ccypair = item['market']['epic']
        key = ccypair + '-' + direction
        if(key in positionMap):
            positionMap[key] = dealSize + positionMap[key]
        else:
            positionMap[key] = dealSize
    # print('current position summary:')
    # print(positionMap)

    try:
        # obligatory sleep, gets round IG 60 per min limit
        time.sleep(2)

        base_url = REAL_OR_NO_REAL + '/markets/' + epic_id
        auth_r = requests.get(
            base_url, headers=authenticated_headers)
        d = json.loads(auth_r.text)

        # print("-----------------DEBUG-----------------")
        # print("#################DEBUG#################")
        # print(auth_r.status_code)
        # print(auth_r.reason)
        # print(auth_r.text)
        # print("-----------------DEBUG-----------------")
        # print("#################DEBUG#################")

        current_bid = d['snapshot']['bid']
        current_offer = d['snapshot']['offer']
        ######################################
        instrument_name = str(d['instrument']['name'])
        debug_info(instrument_name)

        base_url = REAL_OR_NO_REAL + "/prices/" + epic_id + "/MINUTE_15/96"
        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5,
        # MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3,
        # HOUR_4, DAY, WEEK, MONTH)
        auth_r = requests.get(base_url, headers=authenticated_headers)
        d = json.loads(auth_r.text)

        # print("-----------------DEBUG-----------------")
        # print("#################DEBUG#################")
        # print(auth_r.status_code)
        # print(auth_r.reason)
        # print(auth_r.text)
        # print("-----------------DEBUG-----------------")
        # print("#################DEBUG#################")

        remaining_allowance = d['allowance']['remainingAllowance']
        reset_time = humanize_time(
            int(d['allowance']['allowanceExpiry']))
        debug_info("[-]Remaining API Calls left: " + str(remaining_allowance))
        debug_info("[-]Time to API Key reset: " + str(reset_time))

        high_prices = []
        low_prices = []

        for i in d['prices']:

            if i['highPrice']['bid'] is not None:
                highPrice = i['highPrice']['bid']
                high_prices.append(highPrice)
            ########################################
            if i['lowPrice']['bid'] is not None:
                lowPrice = i['lowPrice']['bid']
                low_prices.append(lowPrice)
            ########################################

        array_len_check = []
        array_len_check.append(len(high_prices))
        array_len_check.append(len(low_prices))

        if all_same(array_len_check) == False:
            print("[-]Incomplete dataset from IG, quitting")
            return None

        sup, res = supres(pandas.Series(low_prices),
                          pandas.Series(high_prices))

        trade_direction = "NONE"
        pip_limit = 9999999  # Junk Data
        stop_pips = "999999"  # Junk Data

        if res is not None:
            if float(current_bid) > float(res):  # broken through resistance
                debug_info("!!BUY SIGNAL...." + str(instrument_name))
                trade_direction = "BUY"

        if sup is not None:
            if float(current_bid) < float(sup):  # broken through support
                debug_info("!!SELL SIGNAL...." + str(instrument_name))
                trade_direction = "SELL"
            if float(current_bid) > float(sup):
                if float(abs(float(current_bid) - float(sup))) < 1:
                    debug_info("!!BUY SIGNAL....(bounce off support)" + str(instrument_name))
                    trade_direction = "BUY"

        ###############################################################
        ###############################################################
        ###############################################################

        if trade_direction == "BUY":
            pip_limit = int(abs(numpy.amin(low_prices) - numpy.amax(high_prices)))
            stop_pips = str(int(percentage_of(ESMAMARGREQ, current_bid)))
            print("!!INFO!!...BUY!!")
            print(str(epic_id))
            print(
                "!!INFO!!...Take Profit@...." +
                str(pip_limit) +
                " pips")
        elif trade_direction == "SELL":
            pip_limit = int(abs(numpy.amin(low_prices) - numpy.amax(high_prices)))
            stop_pips = str(int(percentage_of(ESMAMARGREQ, current_bid)))
            print("!!INFO!!...SELL!!")
            print(str(epic_id))
            print(
                "!!INFO!!...Take Profit@...." +
                str(pip_limit) +
                " pips")

        ###############################################################
        ###############################################################
        ########################SANITY CHECKS##########################
        ###############################################################
        ###############################################################

        if trade_direction != "NONE":

            ESMAMARGREQ_req = int(
                percentage_of(
                    ESMAMARGREQ,
                    current_bid))

            if int(ESMAMARGREQ_req) > int(stop_pips):
                debug_info("ESMA Readjustment....")
                stop_pips = int(ESMAMARGREQ_req)
            if int(stop_pips) > int(ESMAMARGREQ_req):
                debug_info("ESMA Readjustment....")
                stop_pips = int(ESMAMARGREQ_req)
            if int(pip_limit) == 0:
                debug_info("Pip limit 0!!")  # not worth the trade
                trade_direction = "NONE"
            if int(pip_limit) == 1:
                debug_info("Pip limit 1!!")  # not worth the trade
                trade_direction = "NONE"
            if int(pip_limit) >= int(GREEDINDICATOR):
                pip_limit = int(GREEDINDICATOR - 1)
            if int(stop_pips) > int(MARGINPROTECT):
                # Remember this "confusing" error
                # message, It's not always too high
                # margin
                debug_info(
                    "Got to be junk data OR MARGINPROTECT limit hit!!")
                trade_direction = "NONE"

            #################################################################
            #################################################################
            try_market_order(
                epic_id, trade_direction, pip_limit, stop_pips, positionMap)
            #################################################################
            #################################################################
        else:
            debug_info("[-]NO CLEAR TRADE DIRECTION")

    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print(sys.exc_info()[0])
        debug_info(
            "[-]Some error occured!")
        time.sleep(2)
        pass

def no_trade_window():

    while True:

        try:

            base_url = REAL_OR_NO_REAL + "/accounts"
            auth_r = requests.get(base_url, headers=authenticated_headers)
            d = json.loads(auth_r.text)

            # print("--------------Account Info-------------")
            # print("#################DEBUG#################")
            # print(auth_r.status_code)
            # print(auth_r.reason)
            # print(auth_r.text)
            # print("-----------------DEBUG-----------------")
            # print("#################DEBUG#################")

            for i in d['accounts']:
                if str(i['accountType']) == "SPREADBET":
                    balance = i['balance']['balance']
                    deposit = i['balance']['deposit']

            percent_used = percentage(deposit, balance)
            neg_bal_protect = i['balance']['available']

            debug_info(
                "!!INFO!!...Percent of account used ..." +
                str(percent_used))

            neg_balance_checks = [
                float(percent_used) > float(PERCENTACCUSED),
                float(neg_bal_protect) < SUPER_LOW_NEG_MARGIN]

            if any(neg_balance_checks):
                print("!!INFO!!...Don't trade, Too much margin used up already")
                time.sleep(60)
                continue
            else:
                debug_info("!!INFO!!...OK to trade...")
                # dont check too often, IG Index API limit 60/min
                time.sleep(3)
                return

        except Exception as e:
            # print(e)
            # print(traceback.format_exc())
            # print(sys.exc_info()[0])
            debug_info("!!ERROR!!...No trade window error!!")
            pass


if __name__ == '__main__':

    while True:
        main_trade_function(LITECOINEPICID)

