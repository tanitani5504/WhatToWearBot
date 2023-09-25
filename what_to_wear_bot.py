import telebot
from telebot import types
import requests
import json
import logging

from hidden import TOKEN
from hidden import API

bot = telebot.TeleBot(TOKEN)

# добавим логгирование, чтобы получать сообщения в консоль
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)


@bot.message_handler(commands=['start'])
def main(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(
        'Woman', callback_data='female')
    btn2 = types.InlineKeyboardButton(
        'Man', callback_data='male')
    markup.row(btn1, btn2)
    bot.send_message(
        message.chat.id, f'Hello, {message.from_user.first_name}! Tell us your gender:', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global gender
    if callback.data == 'female':
        gender = 'female'
        bot.send_message(
            callback.message.chat.id, f'Woman. Tell us your location (city):')
    elif callback.data == 'male':
        gender = 'male'
        bot.send_message(
            callback.message.chat.id, f'Man. Tell us your location (city):')
    elif callback.data == 'photo':
        file = open(f'./{gender}_{temp_indicator}.jpg', 'rb')
        bot.send_photo(callback.message.chat.id, file)


@bot.message_handler(content_types=['text'])
def get_weather(message):
    global temp_indicator
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(
        'I want photo-example!', callback_data='photo')
    markup.row(btn1)
    city = message.text.strip().lower()
    res = requests.get(
        f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    if res.status_code == 200:
        data = json.loads(res.text)
        temp = round(data["main"]["temp"])
        conditions = data['weather'][0]['main']
        if temp > 24.0:
            if gender == "male":
                description = "shorts, t-shirt, sandals or flip flops"
            else:
                description = "summer dress, shorts/skirt, t-short/top, sandals/flip flops"
            text = f'Quite hot. Better to put something light: {description}'
            temp_indicator = 24
        elif temp > 18.0:
            if gender == "male":
                description = "jeans with t-shirt or shirt, light jacket, shoes or sneackers"
            else:
                description = "dress with denim jacket, jeans with t-shirt or shirt, light jacket, flats, shoes or sneackers"
            text = f"It's warm. Better to wear today: {description}"
            temp_indicator = 18
        elif temp > 12.0:
            description = "jeans or trousers, shirt, sweater or hoodie, leather jacket or light coat, shoes or sneackers"
            text = f"It's chilly outside. Better to wear today: {description}"
            temp_indicator = 12
        elif temp > 5.0:
            description = "jeans or trousers, sweater or hoodie, warm jacket or coat, boots."
            text = f"It's cold. Better to wear today: {description} Don't forget a scarf!"
            temp_indicator = 5
        else:
            description = "jeans or trousers, sweater or hoodie, winter jacket or fur coat, winter boots or uggs."
            text = f"It's cold. We recommend to put on thermal underwear or warm socks. Better to wear today: {description} Don't forget hat, scarf and gloves!"
            temp_indicator = 0
        bot.reply_to(
            message, f'Outside temperature is {temp}. {conditions}. {text}', reply_markup=markup)

        if conditions == "Rain":
            bot.reply_to(
                message, f"Raining outside! Don\'t forget to grab an umbrella ")
        elif temp > 18 and conditions == "Clear":
            bot.reply_to(
                message, f'Strong sun today. Don\'t forget to use SPF-cream')
    else:
        bot.reply_to(message, 'Error : City not found. Try again')


bot.polling(none_stop=True)
