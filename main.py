import time
import requests
import json
import telebot
from telebot import types
from keys import api_key, api_secret, token
from binance.client import Client
from newsapi import NewsApiClient
from googletrans import Translator
from threading import Thread
import datetime
import pyshorteners
import schedule
import random

client = Client(api_key, api_secret)
bot = telebot.TeleBot(token)


headers = {
    'X-API-KEY': '9ea3a5fa-bb7d-4f8d-8dc0-5ca352b4931a',
    'Content-Type': 'application/json',
}

def get_film():
    id = random.randint(297, 5000000)
    url = f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{id}"
    req = requests.get(url, headers=headers)
    return json.loads(req.text)

def weather_get():
    api_weather = "http://api.openweathermap.org/data/2.5/find?q=Lviv&type=like&appid=8622086cf3b22b20f915416a1fe01145&units=metric"

    req = requests.get(api_weather)
    data = req.json()

    translator = Translator()

    temp = str(data["list"][0]["main"]["temp"]) + "℃"
    wind = str(data["list"][0]["wind"]["speed"]) + " М/С"
    text = str(data["list"][0]["weather"][0]["description"])
    weather = translator.translate(text, src='en', dest="uk").text
    wind_dir = int(data["list"][0]["wind"]["deg"])
    wind_direction = ""
    if wind_dir >= 337 and wind_dir <= 360 or wind_dir >= 0 and wind_dir <= 22:
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
    string = f"Місто: Львів\nТемпература: {temp}\nПогода: {weather}\nНапрямок вітру: {wind_direction}\nШвилкість вітру: {wind}"
    return string

def price_get():
    req = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=5").text
    json_string = json.loads(req)

    price_uah = str(round(float(json_string[0]["buy"]), 2))
    avg_btc_price = str(round(float(client.get_avg_price(symbol='BTCUSDT')["price"]))) + "$"

    string = f"Курс доллара: {price_uah}\nКурс Біткоіна: {avg_btc_price}"
    return string

def main():
    price_get()
    lines = "--------------------------------------"
    @bot.message_handler(commands=["start"])
    def start(message, res=False):
        time.sleep(1)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_phone = types.KeyboardButton(text="Інформація")
        button_translate = types.KeyboardButton(text="Перекласти текст")
        button_reminder = types.KeyboardButton(text="Нагадування")
        button_short_url = types.KeyboardButton(text="Скоротити посилання")
        button_code = types.KeyboardButton(text="Зашифрувати")
        button_decode = types.KeyboardButton(text="Розшифрувати")
        keyboard.add(button_phone, button_translate, button_reminder, button_short_url, button_code, button_decode)
        bot.send_message(message.chat.id,
                         "Натисніть на кнопку",
                         reply_markup=keyboard)

    @bot.message_handler(content_types=["text"])
    def text(m):
        if m.text == "Інформація":
            message = f"{lines}\n{weather_get()}\n{lines}\n{price_get()}\n{lines}"
            bot.send_message(m.chat.id, message)
        elif m.text == "Перекласти текст":
            keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboard.add("uk>en", "en>uk", "Назад")
            msg = bot.send_message(m.chat.id, 'Виберіть мову', reply_markup=keyboard)
            bot.register_next_step_handler(msg, process_translation)
        elif m.text == "Нагадування":
            msg = bot.send_message(m.chat.id, 'Введіть текст, який ви хочете нагадати собі')
            bot.register_next_step_handler(msg, next_step_reminder)
        elif m.text == "Зашифрувати":
            msg = bot.send_message(m.chat.id, 'Введіть текст, який ви хочете зашифрувати')
            bot.register_next_step_handler(msg, func)
        elif m.text == "Розшифрувати":
            msg = bot.send_message(m.chat.id, 'Введіть текст, який ви хочете розшифрувати')
            bot.register_next_step_handler(msg, re_func)
        elif m.text == "Скоротити посилання":
            msg = bot.send_message(m.chat.id, 'Введіть посилання, яке ви хочете скоротити')
            bot.register_next_step_handler(msg, short_url)
        else:
            try:
                crypto_ticker = str(m.text).upper().strip() + "USDT"
                price = str(round(float(client.get_avg_price(symbol=crypto_ticker)["price"]), 2)) + "$"
                bot.send_message(m.chat.id, f"{crypto_ticker}:\n{price}")
            except Exception as ex:
                pass

    def short_url(message):
        try:
            bot.send_message(message.chat.id, pyshorteners.Shortener().tinyurl.short(message.text))
        except Exception as ex:
            bot.send_message(message.chat.id, "Посилання неправильного формату")

    def completed_key(text, keyword):
        new_key = ''
        text = text.lower()
        for i in range(len(text)):
            if text[i] != " ":
                for j in range(len(keyword)):
                    if len(new_key) < len(text):
                        new_key += keyword[j]
            else:
                new_key += " "
        return new_key

    def func(message):
        message.text = message.text.lower()
        alphabet = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя "
        text_num, key_num, sum = [], [], []
        result = ""

        for i in range(len(message.text)):
            try:
                text_num.append(alphabet.index(message.text[i]))
                key_num.append(alphabet.index(completed_key(message.text, "мінор")[i]))
            except Exception as ex:
                return


        for i in range(len(message.text)):
            if text_num[i] == 33:
                sum.append(33)
                continue
            elif text_num[i] + key_num[i] > 32:
                sum.append((text_num[i] + key_num[i]) - 33)
            else:
                sum.append(text_num[i] + key_num[i])

        for i in sum:
            result += alphabet[i]

        bot.send_message(message.chat.id, result)

    def re_func(message):
        message.text = message.text.lower()
        alphabet = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя "
        text_num, key_num, sum = [], [], []
        result = ""

        for i in range(len(message.text)):
            text_num.append(alphabet.index(message.text[i]))
            key_num.append(alphabet.index(completed_key(message.text, "мінор")[i]))

        for i in range(len(message.text)):
            if text_num[i] == 33:
                sum.append(33)
                continue
            elif text_num[i] < key_num[i]:
                sum.append((text_num[i] + 33 - key_num[i]))
            else:
                sum.append(text_num[i] - key_num[i])

        for i in sum:
            result += alphabet[i]

        bot.send_message(message.chat.id, result)

    def next_step_reminder(message):
        try:
            msg = bot.send_message(message.chat.id, 'Введіть годину, о якій ви хочете отримати нагадування (формату 14:53)')
            text_for_reminder = message.text
            bot.register_next_step_handler(msg, next_second_step_reminder, text_for_reminder)
        except Exception as ex:
            return

    def next_second_step_reminder(message, text_for_reminder):
        try:
            bot.send_message(message.chat.id, "Нагадування створене!")
            def reminder():
                bot.send_message(message.chat.id, text_for_reminder)
                return schedule.CancelJob

            def scheduler():
                splited = str(message.text).split(":")
                if int(splited[0]) < 0:
                    if len(str(abs(int(splited[0]) - 24))) == 1:
                        timezone = f"{'0' + str(abs(int(splited[0]) - 24))}:{splited[1]}"
                    else:
                        timezone = f"{str(abs(int(splited[0]) - 24))}:{splited[1]}"
                else:
                    if len(str(int(splited[0]))) == 1:
                        timezone = f"{'0' + str(int(splited[0]))}:{splited[1]}"
                    else:
                        timezone = f"{str(int(splited[0]))}:{splited[1]}"

                schedule.every().day.at(timezone).do(reminder)

                while True:
                    schedule.run_pending()
                    time.sleep(1)

            t = Thread(target=scheduler)
            t.start()
        except Exception as ex:
            bot.send_message(message.chat.id, ex)

    def process_translation(message):
        try:
            if message.text == "uk>en":
                msg = bot.send_message(message.chat.id, 'Виберіть текст, який бажаєте перекласти')
                bot.register_next_step_handler(msg, translate_to_en)
                bot.register_next_step_handler(msg, start)
            elif message.text == "en>uk":
                msg = bot.send_message(message.chat.id, 'Виберіть текст, який бажаєте перекласти')
                bot.register_next_step_handler(msg, translate_to_uk)
                bot.register_next_step_handler(msg, start)
            elif message.text == "Назад":
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                button_phone = types.KeyboardButton(text="Інформація")
                button_translate = types.KeyboardButton(text="Перекласти текст")
                button_reminder = types.KeyboardButton(text="Нагадування")
                button_short_url = types.KeyboardButton(text="Скоротити посилання")
                button_code = types.KeyboardButton(text="Зашифрувати")
                button_decode = types.KeyboardButton(text="Розшифрувати")
                keyboard.add(button_phone, button_translate, button_reminder, button_short_url, button_code,
                             button_decode)
                bot.send_message(message.chat.id,
                                 "Натисніть на кнопку",
                                 reply_markup=keyboard)
        except Exception as ex:
            print(ex)
            bot.send_message(message.chat.id, 'Помилка!')

    def translate_to_en(message):
        try:
            translator = Translator()
            translation = translator.translate(message.text, dest='en')
            bot.reply_to(message, translation.text)
        except Exception as ex:
            print(ex)
    def translate_to_uk(message):
        try:
            translator = Translator()
            translation = translator.translate(message.text, dest='uk')
            bot.reply_to(message, translation.text)
        except Exception as ex:
            print(ex)
    bot.polling(none_stop=True, interval=0)

if __name__ == '__main__':
    main()
