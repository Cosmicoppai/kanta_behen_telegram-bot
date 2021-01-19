import random
import requests
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, bot
from telegram import Update
from telegram.ext import *
import telegram_send
from settings import TELEGRAM_API_TOKEN, CUSTOM_REPLY  # imported from settings.py

bot = telegram.Bot(TELEGRAM_API_TOKEN)


def start(update, context):
    update.message.reply_text("こんにちは, You can track your daily task's and check the weather. send '/help' for more"
                              "info")


def todo(update, context):
    task = update.effective_message.text
    task_id = update.effective_message.message_id
    todo_title = task.replace("/new", "")
    context.user_data[task_id] = {"title": todo_title, "completed": False}
    update.message.reply_text("Task Added")


def button_click(update, context):  # The task will be deleted on the clicking the button
    query = update.callback_query  # To get the task_id so we can delete the data using it
    task_id = int(query.data)
    del context.user_data[task_id]
    text = "Task's:\n"
    keyboard = []
    count = -1
    # print(context.user_data)
    for key, value in context.user_data.items():
        count += 1
        keyboard.append(
            [InlineKeyboardButton(text=value['title'], callback_data=key)]
        )
        # update.message.reply_text("{}{}{}".format(count, ":-", value['title']))
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text, reply_markup=reply_markup)


def del_all(update, context):
    context.user_data.clear()
    update.message.reply_text("All Task's Deleted")


def show_todo(update, context):
    text = "Task's:\n"
    keyboard = []
    count = -1
    # print(context.user_data)
    for key, value in context.user_data.items():
        count += 1
        keyboard.append(
            [InlineKeyboardButton(text=value['title'], callback_data=key)]
        )
        # update.message.reply_text("{}{}{}".format(count, ":-", value['title']))
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=reply_markup)


def help_(update, context):
    update.message.reply_text(
        text="Available Commands:\n"
             "/new:  Add new Task\n"
             "/delete:  To delete task\n"
             "/list:  To see the list of pending Task's\n"
             "/weather:  To check Weather\n"
    )


aisatsu = ['Hi', 'How are you', 'Hello', 'Yo', 'Namaskar']


def custom_reply(update: Update, context: CallbackContext):
    message_text = update.effective_message.text
    try:
        if message_text in aisatsu:
            reply_text = random.choice(CUSTOM_REPLY[message_text])  # Condition for message's which replies are in
            # the list
        else:
            reply_text = CUSTOM_REPLY[message_text]  # Msg which are in single string format
        if reply_text:
            update.message.reply_text(text=reply_text)
    except KeyError:
        update.message.reply_text("I'm not yet programmed for this situation")


def weather(update, context):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={' \
          '}&units=metric&appid=37ad0e70f360a5a1a7f2c51a7c598d47'
    city = update.effective_message.text
    city = city.replace("/weather", "")
    # print(request.POST)
    try:
        r = requests.get(url.format(city)).json()
        # print(r)
        city_weather = {
            'icon': r['weather'][0]['icon'],
            'temperature': r['main']['temp'],
            'description': r['weather'][0]['description'],
            'feels_like': r['main']['feels_like'],
            'humidity': r['main']['humidity'],
        }
        Icon = "http://openweathermap.org/img/w/{}.png".format(city_weather['icon'])


        chat_id = update.message.chat.id
        bot.send_photo(chat_id, Icon)
        weather_result = "Temperature:-   " + str(city_weather['temperature']) + "°C"
        weather_result1 = "Description:-  " + str(city_weather['description'])
        weather_result2 = "Feels Like:-   " + str(city_weather['feels_like']) + "°C"
        weather_result3 = "Humidity:-   " + str(city_weather['humidity']) + "%"

        update.message.reply_text(weather_result)
        update.message.reply_text(weather_result1)
        update.message.reply_text(weather_result2)
        update.message.reply_text(weather_result3)

    except KeyError:
        update.message.reply_text("No city found")


my_persistence = PicklePersistence(filename='my_file')
updater = Updater(TELEGRAM_API_TOKEN, use_context=True, persistence=my_persistence)

# updater.dispatcher.add_handler(CommandHandler(CUSTOM_REPLY['hi'], custom_reply))
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('new', todo))
dispatcher.add_handler(CommandHandler('help', help_))
dispatcher.add_handler(CommandHandler('list', show_todo))
dispatcher.add_handler(CommandHandler('delete', del_all))
dispatcher.add_handler(CommandHandler('weather', weather))
updater.dispatcher.add_handler(CallbackQueryHandler(button_click))
dispatcher.add_handler(MessageHandler(Filters.chat_type.private, custom_reply))

updater.start_polling()
updater.idle()
