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
    api_weather = "http://api.openweathermap.org/data/2.5/find?q=Sambir&type=like&appid=8622086cf3b22b20f915416a1fe01145&units=metric"

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
    string = f"Місто: Самбір\nТемпература: {temp}\nПогода: {weather}\nНапрямок вітру: {wind_direction}\nШвилкість вітру: {wind}"
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
        button_news = types.KeyboardButton(text="Новини")
        button_film = types.KeyboardButton(text="Фільм")
        button_translate = types.KeyboardButton(text="Перекласти текст")
        button_reminder = types.KeyboardButton(text="Нагадування")
        keyboard.add(button_phone, button_news, button_film, button_translate, button_reminder)
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
        elif m.text == "Новини":
            msg = bot.send_message(m.chat.id, 'Введіть тему для новини')
            bot.register_next_step_handler(msg, process_news)
        elif m.text == "Фільм":
            msg = bot.send_message(m.chat.id, 'Введіть кількість фільмів')
            bot.register_next_step_handler(msg, next_step_film)
        elif m.text == "Нагадування":
            msg = bot.send_message(m.chat.id, 'Введіть текст, який ви хочете нагадати собі')
            bot.register_next_step_handler(msg, next_step_reminder)
        else:
            try:
                crypto_ticker = str(m.text).upper().strip() + "USDT"
                price = str(round(float(client.get_avg_price(symbol=crypto_ticker)["price"]), 2)) + "$"
                bot.send_message(m.chat.id, f"{crypto_ticker}:\n{price}")
            except Exception as ex:
                pass

    def next_step_reminder(message):
        try:
            msg = bot.send_message(message.chat.id, 'Введіть годину, о якій ви хочете отримати нагадування (формату 14:53)')
            text_for_reminder = message.text
            bot.register_next_step_handler(msg, next_second_step_reminder, text_for_reminder)
        except Exception as ex:
            pass

    def next_second_step_reminder(message, text_for_reminder):
        try:
            bot.send_message(message.chat.id, "Нагадування створене!")
            def reminder():
                bot.send_message(message.chat.id, text_for_reminder)
                return schedule.CancelJob

            def scheduler():
                splited = str(message.text).split(":")
                if int(splited[0]) - 2 < 0:
                    if len(str(abs(int(splited[0]) - 2 - 24))) == 1:
                        timezone = f"{'0' + str(abs(int(splited[0]) - 24))}:{splited[1]}"
                    else:
                        timezone = f"{str(abs(int(splited[0]) - 24))}:{splited[1]}"
                else:
                    if len(str(int(splited[0]) - 2)) == 1:
                        timezone = f"{'0' + str(int(splited[0]) - 2)}:{splited[1]}"
                    else:
                        timezone = f"{str(int(splited[0]) - 2)}:{splited[1]}"

                schedule.every().day.at(timezone).do(reminder)

                while True:
                    schedule.run_pending()
                    time.sleep(1)

            t = Thread(target=scheduler)
            t.start()
        except Exception as ex:
            pass
    def next_step_film(message):
        try:
            i = 0
            while i < int(message.text):
                bot.send_message(message.chat.id, get_film_final())
                i += 1
        except Exception as ex:
            print(ex)

    def process_news(message):
        try:
            api_news = NewsApiClient(api_key='5e7365280b4c447c987243e890f80410')
            bbc = api_news.get_everything(q=message.text,
                                          language="ru",
                                          sort_by='relevancy')
            for k in range(0, 4):
                url = bbc["articles"][k]["url"]
                bot.send_message(message.chat.id, f"{url}")
        except Exception as ex:
            print(ex)
            bot.send_message(message.chat.id, 'Результатів не знайдено')
    def get_film_final():
        try:
            film_info = get_film()

            if film_info["ratingKinopoisk"] != None and film_info["ratingKinopoisk"] > 6.5:
                if film_info["ratingImdb"] != None and film_info["ratingImdb"] > 6.5:
                    if film_info["year"] > 1990:
                        if film_info["serial"] == False and film_info["shortFilm"] == False and film_info["has3D"] == False:
                            genres = []

                            for l in range(0, len(film_info["genres"])):
                                genres.append(film_info["genres"][l]["genre"])
                            if "документальный" in genres or "короткометражка" in genres:
                                get_film_final()
                            else:
                                image_film = film_info["posterUrl"]
                                nameRu = film_info["nameRu"]
                                rating_kinopoisk = film_info["ratingKinopoisk"]
                                rating_imdb = film_info["ratingImdb"]
                                year = film_info["year"]
                                genre = ",  ".join(genres)
                                film_length = str(film_info["filmLength"]) + " хвилин"
                                country = film_info["countries"][0]["country"]
                                description = film_info["description"]
                                main_message_film = f"Фільм: {nameRu}\n\nРік: {year}\nРейтинг: КП - {rating_kinopoisk} | IMDB - {rating_imdb}\nКраїна: {country}\nЖанр: {genre}\nЧас: {film_length}\nОпис: {description}\n{image_film}"
                                return main_message_film
        except Exception as ex:
            print(ex)
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
                button_news = types.KeyboardButton(text="Новини")
                button_film = types.KeyboardButton(text="Фільм")
                button_translate = types.KeyboardButton(text="Перекласти текст")
                keyboard.add(button_phone, button_news, button_film, button_translate)
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
