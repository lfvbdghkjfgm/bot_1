import telebot
from telebot import types
from datetime import datetime
import time
import threading
import sqlite3 as sq


bot = telebot.TeleBot('7528462585:AAFH6DKZdBZk3bNgEOpeI1yGZkwAwxudq8s')

def db_connect(db_name):
    return sq.connect(f'{db_name}.db')

def is_holiday(con, month, day):
    cur = con.cursor()
    days = cur.execute('SELECT days FROM holidays WHERE month = ?', (month,)).fetchone()[0].split()
    return str(day) in days

def get_db_user_class(con, user_id):
    cur = con.cursor()
    return cur.execute('SELECT class FROM users_1 WHERE id = ?', (user_id,)).fetchone()[0]

def send_message_to_users(users, message):
    for user in users:
        bot.send_message(int(user), message)

def time_now():
    now = datetime.now()
    return now.month, now.day, now.strftime("%A").lower(), now.hour * 60 + now.minute

def lesson(con, db_name):
    com_time = time_now()[-1]
    day = time_now()[-2]
    cur = con.cursor()

    now_less = cur.execute('SELECT * FROM {} WHERE start < ? AND finish > ?'.format(day), (com_time, com_time)).fetchone()
    next_less = cur.execute('SELECT * FROM {} WHERE start > ?'.format(day), (com_time,)).fetchone()

    return now_less, next_less

def users_in_class(con, class_name):
    cur = con.cursor()
    return [user[0] for user in cur.execute('SELECT id FROM users_1 WHERE class = ? AND messages = 1', (class_name,)).fetchall()]

def send_all_messages(next_time, first_time, con):
    already_sent = 0
    while True:
        com_time = time_now()[-1]
        if time_now()[2] not in ['saturday', 'sunday']:
            for time_data in next_time:
                if not is_holiday(con, time_data[1][:-3], time_now()[1]):
                    if time_data[0] - com_time == 5 and already_sent != com_time:
                        ind = time_data[1][:-3]
                        h = lesson(con, ind)[1]
                        send_message_to_users(users_in_class(con, ind), f'Урок через 5 минут\nСейчас будет урок {h[1]}\nУчителя зовут {h[2]}\nУрок будет в кабинете {h[3]}')
                        already_sent = com_time
            for time_data in first_time:
                if not is_holiday(con, time_data[1][:-3], time_now()[1]):
                    if com_time - time_data[0] == -30 and already_sent != com_time:
                        ind = time_data[1][:-3]
                        h = lesson(con, ind)[1]
                        send_message_to_users(users_in_class(con, ind), f'Урок через 30 минут\nСейчас будет урок {h[1]}\nУчителя зовут {h[2]}\nУрок будет в кабинете {h[3]}')
                        already_sent = com_time
        time.sleep(15)

@bot.message_handler(commands=['start'])
def start_1(message):
    with db_connect('users') as con:
        cur = con.cursor()
        if cur.execute('SELECT COUNT(*) FROM users_1 WHERE id = ?', (message.chat.id,)).fetchone()[0] == 0:
            cur.execute('INSERT INTO users_1 (id, class, messages) VALUES (?, ?, ?)', (message.chat.id, '157610Г', 0))
            con.commit()

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = ['/start', '/help', '/timetable', '/lesson_data', '/messages']
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}', reply_markup=markup)
    bot.send_message(message.chat.id, 'Выбери нужную команду или нажми \n/help для открытия инструкции', reply_markup=markup)

    threading.Thread(target=send_all_messages, daemon=True, args=(next_time, first_time, con)).start()

@bot.message_handler(commands=['help'])
def help_1(message):
    help_text = '''
Приветствую вас в моем боте\n
Этот бот позволяет быстро узнать следующий урок, а также кабинет и ФИО учителя\n
<b>Руководство по командам бота</b>\n
<b>/lesson_data</b> - команда, чтобы узнать следующий урок\n
<b>/timetable</b> - команда, чтобы узнать все расписание на сегодня \n
<b>/messages</b> - команда, чтобы включить или выключить уведомления\n
<i>Уведомления приходят за 30 минут до начала первого урока и за 5 минут до начала каждого урока</i>
Тех поддержка бота <b>@topych_lfvb</b>
'''
    bot.send_message(message.chat.id, help_text, parse_mode='html')

@bot.message_handler(commands=['lesson_data'])
def lesson_1(message):
    with db_connect('users') as con:
        db = get_db_user_class(con, message.chat.id)
        if time_now()[2] not in ['saturday', 'sunday'] and not is_holiday(con, db, time_now()[1]):
            lessons = lesson(con, db)
            if lessons[0]:
                mess = f'Сейчас - {lessons[0][1]}\nВ кабинете номер {lessons[0][3]}\nУчителя зовут {lessons[0][2]}'
                bot.send_message(message.chat.id, mess)
                mess_3 = f'Следующий урок - {lessons[1][1]}\nВ кабинете номер {lessons[1][3]}\nУчителя зовут {lessons[1][2]}'
                bot.send_message(message.chat.id, mess_3)
            elif lessons[1]:
                mess_3 = f'Сечас - {lessons[1][1]}\nВ кабинете номер {lessons[1][3]}\nУчителя зовут {lessons[1][2]}'
                bot.send_message(message.chat.id, mess_3)
                bot.send_message(message.chat.id, 'Это последний урок')
            else:
                bot.send_message(message.chat.id, 'Уроки закончились')
        else:
            bot.send_message(message.chat.id, 'Сегодня нет уроков')

@bot.message_handler(commands=['messages'])
def messages(message):
    with db_connect('users') as con:
        cur = con.cursor()
        current_status = cur.execute('SELECT messages FROM users_1 WHERE id = ?', (message.chat.id,)).fetchone()[0]
        new_status = 1 - current_status
        cur.execute('UPDATE users_1 SET messages = ? WHERE id = ?', (new_status, message.chat.id))
        con.commit()
        bot.send_message(message.chat.id, 'Вы включили уведомления об уроках' if new_status else 'Вы выключили уведомления об уроках')

@bot.message_handler(commands=['timetable'])
def timetable_1(message):
    with db_connect('users') as con:
        db = get_db_user_class(con, message.chat.id)
        day = time_now()[2]
        if day not in ['saturday', 'sunday'] and not is_holiday(con, db, time_now()[1]):
            cur = con.cursor()
            lessons = cur.execute(f'SELECT * FROM {day}').fetchall()
            for lesson in lessons:
                mess = f'<b>{lesson[0]} урок</b>\nУрок - {lesson[1]}\nВ кабинете номер {lesson[3]}\nУчителя зовут - {lesson[2]}'
                bot.send_message(message.chat.id, mess, parse_mode='html')
        else:
            bot.send_message(message.chat.id, 'Сегодня нет уроков')

# Инициализация
with db_connect('157610Г') as con:
    next_time = [[con.execute('SELECT start FROM time WHERE start > ?', (time_now()[-1],)).fetchone()[0], '157610Г.db']]
    first_time = [[con.execute('SELECT start FROM time WHERE id = 1').fetchone()[0], '157610Г.db']]

bot.polling(non_stop=True)
