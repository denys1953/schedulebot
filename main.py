import time
import requests
import json
import schedule
import telebot
from telebot import types

token = "5118372579:AAG8mnrwgfWnYItTRiQuJUi7HOXYAtZ29e0"
bot = telebot.TeleBot(token)
bot_name = "@shedule5274_bot"

def weather_get():
    api_weather = "http://api.openweathermap.org/data/2.5/find?q=Sambir&type=like&appid=8622086cf3b22b20f915416a1fe01145&units=metric"

    req = requests.get(api_weather)
    data = req.json()

    temp = str(data["list"][0]["main"]["temp"]) + "℃"
    wind = str(data["list"][0]["wind"]["speed"]) + " М/С"
    weather = str(data["list"][0]["weather"][0]["main"])

    string = f"Місто: Самбір\nТемпература: {temp}\nПогода: {weather}\nВітер: {wind}"
    return string

def price_get():
    api_crypto_btc = "https://rest.coinapi.io/v1/assets/BTC"
    api_crypto_uah = "https://rest.coinapi.io/v1/assets/UAH"

    headers = {"X-CoinAPI-Key": "05F80901-9E5D-4814-B402-99E4595539EC"}

    req_btc = requests.get(api_crypto_btc, headers=headers)
    data_crypto = req_btc.json()

    req_usd = requests.get(api_crypto_uah, headers=headers)
    data_usd = req_usd.json()

    price_uah = str(round(float(1/data_usd[0]['price_usd']), 2)) + "₴"
    price_btc = str(round(float(data_crypto[0]['price_usd']))) + "$"

    string = f"Курс Доллара: {price_uah}\nКурс Біткоіна: {price_btc}"
    return string

def main():
    lines = "--------------------------------------"
    @bot.message_handler(commands=["start"])
    def start(m, res=False):
        bot.send_message(m.chat.id, 'Привіт! Тут буде публікуватися актуальна інформація про погоду і курси валют')
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = types.KeyboardButton(text="Почати цикл")
        keyboard.add(button_phone)
        bot.send_message(m.chat.id,
                         "Натисніть на кнопку!",
                         reply_markup=keyboard)

    @bot.message_handler(content_types=["text"])
    def text(m):
        if m.text == "Почати цикл":
            def get_info():
                message = f"{lines}\n{weather_get()}\n{lines}\n{price_get()}\n{lines}"
                bot.send_message(m.chat.id, message)

            get_info()

            schedule.every().day.at("10:00").do(get_info)

            while True:
                schedule.run_pending()

    bot.polling(none_stop=True, interval=0)

if __name__ == '__main__':
    main()

