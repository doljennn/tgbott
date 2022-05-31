#coding: utf8
import sqlite3
import time
import telebot
from telebot import types
from time import sleep
import config
import logging
import datetime

from config1 import error_log

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) 
bot = telebot.AsyncTeleBot(token = '5140675739:AAHbT4nreLVCxCWVss7phwbu7HI96gTOp6A',  skip_pending=False, threaded=False, num_threads=100)
markup = types.ReplyKeyboardMarkup()
itembtna = types.KeyboardButton('/paste_text')
itembtnb = types.KeyboardButton('/stats')
itembtnc = types.KeyboardButton('/help')
itembtnd = types.KeyboardButton('/start')
markup.row(itembtna, itembtnb)
markup.row(itembtnc, itembtnd)
bot.send_message(468437664, "Бот был запущен! Используй одну из команд ниже", reply_markup=markup)
conn = sqlite3.connect("mydatabase.db") # или :memory: чтобы сохранить в RAM
cursor = conn.cursor()
class DataConn:
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name, isolation_level=None)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        if exc_val:
            raise
runtime = time.time()
bot.send_message(468437664, 'Бот был запущен. Сообщений в очереди: <b>{}</b>'.format(bot.get_webhook_info().pending_update_count), parse_mode='HTML')

@bot.message_handler(commands=['paste_text'])
def dis(message):
	if message.chat.id == config.owner:
		bot.send_message(config.owner, 'Введи текст для рассылки')
		bot.register_next_step_handler(message, next_step)
	else:
		bot.send_message(message.chat.id, 'Эта команда была создана не для вас!')

@bot.message_handler(commands=['stats'])
def stats(message):
	try:
		if message.chat.id == int(468437664):
			key = types.InlineKeyboardMarkup()
			but_1 = types.InlineKeyboardButton(text="Пользователей в личке", callback_data="NumberOne")
			but_2 = types.InlineKeyboardButton(text="Сообщений в базе", callback_data="NumberTwo")
			but_3 = types.InlineKeyboardButton(text="Отправить базу", callback_data="NumberThree")
			but_4 = types.InlineKeyboardButton(text="Рассылка", callback_data="Number4")
			key.add(but_1)
			key.add(but_2)
			key.add(but_3)
			key.add(but_4)

			bot.send_message(message.chat.id, "Привет. Выбери один из пунктов меню", reply_markup=key)
		else:
			bot.send_message(message.chat.id, 'Похоже, вы не имеете доступа к этой команде :(')
	except Exception as e:
		bot.send_message(config.error_log, e)


@bot.callback_query_handler(func=lambda c:True)
def inline(c):
	if c.data == 'NumberOne':
		cursor.execute('SELECT * FROM distr')
		num_users = cursor.fetchall()
		bot.send_message(468437664, 'Зарегистрировано пользователей в базе: <b>{}</b>'.format(len(num_users)), parse_mode='HTML')

	if c.data == 'NumberTwo':
		cursor.execute('SELECT * FROM bot')
		num_messages = cursor.fetchall()
		bot.send_message(468437664, 'Зарегистрировано сообщений в базе: <b>{}</b>'.format(len(num_messages)), parse_mode='HTML')

	if c.data == 'NumberThree':
		data = open('mydatabase.db', 'rb')
		bot.send_document(468437664, data)
	if c.data == 'Number4':
		with conn:
			cursor.execute('SELECT * FROM distr')
			rows = cursor.fetchall()
			arr=[i[0] for i in rows]
			num_users = cursor.fetchall()
			bot.send_message(468437664, 'Рассылка была запущена! Сообщение получат: <b>{}</b>'.format(len(rows)), parse_mode='HTML')
			cursor.execute('SELECT text FROM text_of_dis WHERE id = 1 ')
			t = cursor.fetchall()
			#arr_text=[i[0] for i in t]
			for i in arr:
				print(rows)
				bot.send_message(i, t)

def next_step(message):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM text_of_dis WHERE id = 1")

	cursor.execute("INSERT INTO text_of_dis  VALUES (?,?)", (1, message.text))
	conn.commit()

	bot.send_message(message.chat.id, 'Текст был вставлен')
	
@bot.message_handler(commands=['start'])
def start(message): 
		if int(message.chat.id) == config.owner:
			try:
				markup = types.ReplyKeyboardMarkup()
				itembtnv = types.KeyboardButton('/send_db')
				itembtnc = types.KeyboardButton('/help')
				itembtnd = types.KeyboardButton('/ping')
				itembtnb = types.KeyboardButton('/stats')
				markup.row(itembtnv, itembtnb)
				markup.row(itembtnc, itembtnd)
				bot.send_message(config.owner, 'Привет', reply_markup=markup)
			except Exception as e:
				bot.send_message(config.error_log, e)
		else:
			try:
				cursor = conn.cursor()
				message_id = int(message.chat.id)
				status = cursor.execute("SELECT user_id FROM distr WHERE user_id == (?)", (message_id,))
				if message_id == status:
					bot.send_message(message.chat.id, 'Упс, кажется вы уже регистрировались. Просто напишите что-нибудь')
				else:
					bot.send_message(message.chat.id,  'Привет, ' + str(message.from_user.first_name) +'!\n' 'Данный бот создан для общения с @AmirAdminTG\n\nДоступные команды:\n/id — посмотреть cвой ID\n/ping — узнать, жив ли бот')
					cursor.execute("INSERT INTO distr (user_id) VALUES (?)", (message_id,))
					conn.commit()
			except Exception as e:
				bot.send_message(config.error_log, e)

#@bot.message_handler(commands=["ping"]) 
#def ping(message):
#	if message.chat.id == 484846555:
#		pass
#	else:
#		bot.send_message(message.chat.id, "<b>PONG!</b>" , parse_mode="HTML") 
@bot.message_handler(commands=['ping'])
def ping(message):

    nowtime = time.time()
    uptime = round(nowtime - runtime)
    uptimestr = str(time.strftime("%H:%M:%S", time.gmtime(int(uptime))))
    answertime = nowtime - message.date
    nowtimestr = time.ctime(nowtime)
    status = bot.get_webhook_info().pending_update_count - 1
    msgg = bot.reply_to(message,'Текущее время: '+ str(nowtimestr) + '\nБот ответил за: ' + str(answertime) + '\n Бот активен уже: ' + str(uptimestr)  + '\nСообщений в очереди: ' + str(status),  parse_mode='html')






@bot.message_handler(commands=['id'])
def process_start(message):
	if int(message.chat.id) == 484846555: 
		pass
	else:
		bot.send_message(message.chat.id, "Твой ID: " + str(message.from_user.id), parse_mode = 'HTML')
		bot.forward_message(config.owner, message.chat.id, message.message_id)

@bot.message_handler(content_types=["text"])
def messages(message):
	cursor = conn.cursor()
	message_id = message.chat.id
	name = message.chat.first_name
	username = message.chat.username
	message_text = message.text
	message_date = message.date 
	cursor.execute("INSERT INTO bot VALUES (?,?,?,?,?)", (message_id, name, username, message_text, message_date))
	conn.commit()   
	if int(message.chat.id) == config.group or int(message.chat.id) == 468437664:
		try:
			bot.send_message(message.reply_to_message.forward_from.id, message.text)
		except Exception as e:
			bot.send_message(config.error_log, e)
	else:
		try:
			bot.forward_message(config.group, message.chat.id, message.message_id)
		except Exception as e:
			bot.send_message(468437664, e)
			bot.send_message(error_log, e)

if __name__ == '__main__':
        bot.polling(none_stop = True)	
        
