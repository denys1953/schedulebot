import time
import requests
import json
import telebot
from telebot import types
from keys import api_key, api_secret, token
from binance.client import Client
from translate import Translator

client = Client(api_key, api_secret)
bot = telebot.TeleBot(token)

def weather_get():
    api_weather = "http://api.openweathermap.org/data/2.5/find?q=Sambir&type=like&appid=8622086cf3b22b20f915416a1fe01145&units=metric"

    req = requests.get(api_weather)
    data = req.json()

    translator = Translator(to_lang="Ukrainian")

    temp = str(data["list"][0]["main"]["temp"]) + "℃"
    wind = str(data["list"][0]["wind"]["speed"]) + " М/С"
    weather = translator.translate(str(str(data["list"][0]["weather"][0]["description"])))
    wind_dir = int(data["list"][0]["wind"]["deg"])
    wind_direction = ""
    if wind_dir >= 337 and wind_dir <= 22:
        wind_direction = "ПН"
    elif wind_dir > 22 and wind_dir <= 67:
        wind_direction = "ПН/СХ"
    elif wind_dir > 67 and wind_dir <= 112:
        wind_direction = "СХ"
    elif wind_dir > 112 and wind_dir <= 157:
        wind_direction = "ПД/СХ"
    elif wind_dir > 157 and wind_dir <= 202:
        wind_direction = "ПД"
    elif wind_dir > 202 and wind_dir <= 247:
        wind_direction = "ПД/ЗХ"
    elif wind_dir > 247 and wind_dir <= 292:
        wind_direction = "ЗХ"
    elif wind_dir > 292 and wind_dir < 337:
        wind_direction = "ПН/ЗХ"
    string = f"Місто: Самбір\nТемпература: {temp}\nПогода: {weather}\nНапрямок вітру: {wind_direction}\nШвилкість вітру: {wind}"
    print(data)
    return string

def price_get():
    url_fiat_course = "https://freecurrencyapi.net/api/v2/latest?apikey=2417fbe0-94e5-11ec-8326-d95b106c0d87"
    req = requests.get(url_fiat_course).text
    json_string = json.loads(req)

    price_uah = str(round(float(json_string["data"]["UAH"]), 2))
    avg_btc_price = str(round(float(client.get_avg_price(symbol='BTCUSDT')["price"]))) + "$"

    string = f"Курс Доллара: {price_uah}\nКурс Біткоіна: {avg_btc_price}"
    return string


def main():
    price_get()
    lines = "--------------------------------------"
    @bot.message_handler(commands=["start"])
    def start(m, res=False):
        bot.send_message(m.chat.id, 'Привіт! Тут буде публікуватися актуальна інформація про погоду і курси валют')
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = types.KeyboardButton(text="Інформація")
        keyboard.add(button_phone)
        bot.send_message(m.chat.id,
                         "Натисніть на кнопку!",
                         reply_markup=keyboard)

    @bot.message_handler(content_types=["text"])
    def text(m):
        if m.text == "Інформація":
            message = f"{lines}\n{weather_get()}\n{lines}\n{price_get()}\n{lines}"
            bot.send_message(m.chat.id, message)
        else:
            try:
                crypto_ticker = str(m.text).upper().strip() + "USDT"
                price = str(round(float(client.get_avg_price(symbol=crypto_ticker)["price"]), 2)) + "$"
                bot.send_message(m.chat.id, f"{crypto_ticker}:\n{price}")
            except Exception as ex:
                pass


    bot.polling(none_stop=True, interval=0)

if __name__ == '__main__':
    main()

