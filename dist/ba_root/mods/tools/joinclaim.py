#ba meta requires api 7
#JoinClaim by SARA 
import ba, _ba
import random
from datetime import datetime, timedelta
from chatHandle.ChatCommands.commands import CoinCmds as cc
from chatHandle.ChatCommands.commands.Handlers import sendchatclid
from playersData import pdata
import setting
settings = setting.get_settings_data()
tic = settings["CurrencyType"]["Currency"]

def join_claim(name, clid, accountid):
    set_time_hours = 24
    set_time_seconds = set_time_hours * 3600  # Convert hours to seconds
    customers = pdata.get_custom()['coin_claim']

    previous = customers.get(accountid)
    now = datetime.now()
    if previous is None or now >= datetime.strptime(
            previous['expiry'], '%d-%m-%Y %H:%M:%S'):
        streak = int(previous.get('streak', 0)) + 1 if previous else 1
        coin_claim = min(200, 50 + (streak - 1) * 10)

        expiry = now + timedelta(seconds=set_time_seconds)
        customers[accountid] = {
            'name': name,
            'expiry': expiry.strftime('%d-%m-%Y %H:%M:%S'),
            'streak': streak,
        }

        if coin_claim == 50:
            message = f"Congratulations,{name} You've claimed..! {coin_claim}{tic}.\n"
        elif coin_claim == 60:
            message = f"Wow, {name} You've claimed {coin_claim}{tic}.Nice..! \n"
        elif coin_claim == 70:
            message = f"Incredible,{name}! You've claimed {coin_claim}{tic}.\n"
        elif coin_claim == 80:
            message = f"{name}, you're on fire..! You've claimed {coin_claim}{tic}.\n"

        cc.addcoins(accountid, coin_claim)
        pdata.CacheData.custom = pdata.get_custom()
        sendchatclid(message, clid)

        # Add countdown message only once
        countdown_message = f"To check next join claim time: type /cjt or /checkjointime"
        sendchatclid(countdown_message, clid)
