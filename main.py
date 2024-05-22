import os
from pybit.unified_trading import HTTP
from util import calculate_pump_percent
import logging
import telebot
import time
import threading
from queue import Queue

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
session = HTTP(
    testnet=False,
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
)
users = []
users_queue = Queue()
tickers_unfiltered = session.get_tickers(category="linear")["result"]["list"]
tickers = [item for item in tickers_unfiltered if "USDT" in item["symbol"]]
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))
def compare_tickers(users_q):
    global tickers
    users = []
    while True:
        try:
            new_users = users_q.get(timeout=1)
            users = new_users
        except Exception:
            pass

        new_tickers_unfiltered = session.get_tickers(category="linear")["result"]["list"]
        new_tickers = [item for item in new_tickers_unfiltered if "USDT" in item["symbol"]]

        if (len(tickers) == 0):
            tickers = new_tickers
            time.sleep(900)
        message = ""
        for ticker in tickers:
            for new_ticker in new_tickers:
                if ticker["symbol"] == new_ticker["symbol"]:
                    pump_percent = calculate_pump_percent(ticker, new_ticker)
                    if abs(pump_percent) >= 5:
                        message += f"<a href='https://www.bybit.com/trade/usdt/{new_ticker['symbol']}'>{new_ticker['symbol']}</a> {'pumped' if pump_percent > 0 else 'dumped'} {pump_percent:.2f}%\n\n"
        if len(message) > 0:
            for user in users:
                try:
                    bot.send_message(user, message,parse_mode="HTML", disable_web_page_preview= True)
                except Exception as e:
                    logger.error("Error sending message", e)
        tickers = new_tickers
        time.sleep(900)

thread = threading.Thread(target=compare_tickers, args=(users_queue,))
thread.daemon = True  # Allows the program to exit even if this thread is still running
thread.start()

@bot.message_handler(commands=['start', 'hello'])
def register(message):
    if (users.count(message.from_user.id) == 0):
        users.append(message.from_user.id)
        bot.send_message(message.chat.id, "<b>Welcome to OICryptoScan! \n\n🌟</b> OICryptoScan is your go-to assistant for timely updates on the open interest of various cryptocurrencies.\n\nEvery 15 minutes, we provide signals on rising or falling open interest, helping you make informed trading decisions in real-time.\n\nOICryptoScan is completely <b>free</b> and exists and thrives solely because of the generous donations from users like you\n\n<b>TRC-USDT:</b> <code>TWkdkf8Pbz4jDgUikmrjBmVudRVBCAq1mA</code> (tap to copy)\n\n<b>BSC:</b> <code>0x7a4525ef6a59f9877b2f371e7861168227c40743</code> (tap to copy)\n\n🚀 From now on you will recieve open interest updates!\n\nYou will recieve your first update in less than <b>15 minutes</b>", parse_mode="HTML")
        users_queue.put(users)

def start_polling():
    bot.polling()
try:
    start_polling()
except Exception as e:
    logger.error("Error polling telegram")
    start_polling()

