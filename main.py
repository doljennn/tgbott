import telebot
from telebot import TeleBot
import sqlite3
import config
import time
from telebot import types
from time import sleep
import logging
import datetime

#"5137964405:AAGeAhMEd_hDYjf7JbEE1Olo_G2vmmPGN8M"
bot: TeleBot = telebot.TeleBot(config.token)

keyboard = telebot.types.ReplyKeyboardMarkup(True)
keyboard.row('Покупка услуг','Обратная связь')
keyboard.row('Проверить подписку', 'Заявка')

connection = sqlite3.connect('Data.db', check_same_thread=False)
cursor = connection.cursor()
Sqlquery = 'create table if not exists users(id int primary key, name text, surname text, lastname text)'
cursor.execute(Sqlquery)
connection.commit()


def send (id, text):
    bot.send_message(id, text, reply_markup= keyboard)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    send(message.chat.id, "asdasd")
    bot.reply_to(message, "Добро пожаловать, что вас интересует? Используйте /info, для того, чтобы ознакомиться с краткой спракой для моего функционирования")
    
    userid = message.from_user.id
    userfirstname = message.from_user.first_name
    userlastname = message.from_user.last_name
    username = message.from_user.username

    Sqlquery = "select * from users where id = {0}".format(userid)
    cursor.execute(Sqlquery)
    asd = cursor.fetchall()
    if asd[0][0] != userid:
        assert isinstance(userid, object)
        sqlquery = 'insert into users(name, surname, id, lastname) values("{0}","{1}","{2}", "{3}")'.format(
            userfirstname, username, userid, userlastname)
        cursor.execute(sqlquery)
        connection.commit()

@bot.message_handler(commands=['feedback'])
def feedback(message):
    msg = message.text
    msg = msg.replace("/feedback ", "")
    keyboard1 = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
    keyboard1.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard1.add(key_no)
    question = "Это ваше обращение? \n {0}".format(msg)
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard1)



@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
        Sqlquery = 'create table if not exists feedback(id integer primary key autoincrement not null, message text, userid int)'
        cursor.execute(Sqlquery)
        connection.commit()
        msg = call.message.text
        msg = msg.replace("Это ваше обращение? \n ","")
        Sqlquery = 'insert into feedback(message, userid) values("{0}", "{1}")'.format(msg, call.message.from_user.id)
        cursor.execute(Sqlquery)
        connection.commit()
        bot.send_message(call.message.chat.id, 'Сейчас передам сотрудникам');
    elif call.data == "no":
            bot.send_message(call.message.chat.id, "Отправьте обращение заново")  # переспрашиваем

def obr(question):
    answer = yield question
    return answer

@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id, 'Приветствую, я бот-ассистент под покровительством компании "Адей". Тут вы можете обратиться за обратной связью к нашим работникам, приобрести необходимые продукты, для разработки на 1С, а также оставить заявку на вызов специалиста с почасовой оплатой труда.')

@bot.message_handler(content_types=['text'])
def main(message):
    id = message.chat.id
    msg = message.text
    if message.text.lower() == 'обратная связь':
        send(id, "Используйте команду /feedback, для того, чтобы оставить сообщение разработчику")
    elif msg == 'Покупка услуг':
        send(id, 'Для покупки продуктов и вызова специалиста воспользуйтесь нашим сайтом https://adey.ru/magazin , чтобы избежать неприятностей с оплатой и дальнейшим получением купленного продукта')
    else:
        send(id, 'Не понимаю вас, я не искусственый интеллект, пожалуйста, воспользуйся командами /start; /info;')


bot.infinity_polling()