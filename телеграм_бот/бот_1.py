import telebot
from telebot import types
from datetime import datetime
import time
import threading
import sqlite3

# Инициализация бота
bot = telebot.TeleBot('YOUR_BOT_TOKEN_HERE')

# Подключение к базе данных SQLite
conn = sqlite3.connect('school_bot.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблиц, если они не существуют
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS timetable (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_of_week INTEGER,
    lesson_name TEXT,
    classroom TEXT,
    teacher_name TEXT
)
''')

conn.commit()

# Праздники и время уроков
holidays = [[], [28, 29, 30, 31], [1, 4], [30, 31], [1, 2, 3, 6, 7, 8], [17, 18, 19, 20, 21, 24], [], [7, 8, 9, 10, 11]]
time_less = [510, 550, 570, 610, 630, 670, 690, 730, 750, 790, 810, 850, 870, 910]
all_ids = []


def send_all_messages():
    global all_ids
    while True:
        time_1 = time_now()
        comf_time = time_1[3] * 60 + time_1[4]
        a = 15
        if time_1[2] != 6 and time_1[2] != 7:  # Проверка на выходные
            lessons = get_lessons()
            g = less(comf_time)[1]
            if time_1[3] == 8 and time_1[4] == 0:
                for i in all_ids:
                    bot.send_message(i, 'Уроки начинаются через 30 минут')
                    mess_1 = f'Первый урок - {lessons[0][1]}\nВ кабинете номер {lessons[0][2]}\nУчителя зовут {lessons[0][3]}'
                    bot.send_message(i, mess_1)
                a = 65
            elif g - comf_time == 5:
                for i in all_ids:
                    bot.send_message(i, 'Урок через 5 минут')
                    mess_1 = f'Следующий урок - {lessons[0][1]}\nВ кабинете номер {lessons[0][2]}\nУчителя зовут {lessons[0][3]}'
                    bot.send_message(i, mess_1)
                a = 65
            else:
                a = 15
        time.sleep(a)


def time_now():
    time_1 = datetime.fromtimestamp(time.time())
    month = time_1.month
    day = time_1.day
    week = time_1.weekday() + 1
    hour = time_1.hour
    minute = time_1.minute
    return [month, day, week, hour, minute]


def get_lessons():
    day_of_week = time_now()[2]
    cursor.execute('SELECT * FROM timetable WHERE day_of_week = ?', (day_of_week,))
    return cursor.fetchall()


def messages_1(chat_id):
    global all_ids
    if chat_id in all_ids:
        bot.send_message(chat_id, 'Вы выключили уведомления об уроках')
        all_ids.remove(chat_id)
    else:
        bot.send_message(chat_id, 'Вы включили уведомления об уроках')
        all_ids.append(chat_id)


def less(time_now):
    time_to_lesson = 0
    global time_less
    g = 0
    if time_now < time_less[0]:
        g = 1
        time_to_lesson = time_less[0]
    elif time_now > time_less[-1]:
        g = 15
    else:
        start = 0
        end = 1
        k = 2
        for i in range(13):
            if time_now >= time_less[start] and time_now <= time_less[end]:
                g = k
            start += 1
            end += 1
            k += 1
        if g % 2 == 1:
            time_to_lesson = time_less[g - 1]
    g = [g, time_to_lesson]
    return (g)


@bot.message_handler(commands=['start'])
def start_1(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    fun_1 = types.KeyboardButton('/start')
    fun_2 = types.KeyboardButton('/help')
    fun_3 = types.KeyboardButton('/timetable')
    fun_4 = types.KeyboardButton('/lesson_data')
    fun_5 = types.KeyboardButton('/messages')
    mess_1 = f'Привет, {message.from_user.first_name}'
    markup.add(fun_1, fun_2, fun_3, fun_4, fun_5)
    bot.send_message(message.chat.id, mess_1, reply_markup=markup)

    # Добавление пользователя в базу данных
    cursor.execute('INSERT OR IGNORE INTO users (chat_id) VALUES (?)', (message.chat.id,))
    conn.commit()

    bot.send_message(message.chat.id, 'Выбери нужную команду или нажми \n/help для открытия инструкции',
                     reply_markup=markup)
    threading.Thread(target=send_all_messages, daemon=True).start()


@bot.message_handler(commands=['help'])
def help_1(message):
    mess_1 = '''
Приветствую вас в моем боте\n
Этот бот позволяет быстро узнать следующий урок, а также кабинет и ФИО учителя\n
'''
    bot.send_message(message.chat.id, mess_1, parse_mode='html')
    mess_2 = '''
<b>Руководство по командам бота</b>\n
<b>/lesson_data</b> - команда, чтобы узнать следующий урок\n
<b>/timetable</b> - команда, чтобы узнать все расписание на сегодня \n
<b>/messages</b> - команда, чтобы включить или выключить уведомления\n
<i>Уведомления приходят за 30 минут до начала первого урока и за 5 минут до начала каждого урока</i>'''
    bot.send_message(message.chat.id, mess_2, parse_mode='html')
    mess_3 = '''
Тех поддержка бота <b>@topych_lfvb</b>'''
    bot.send_message(message.chat.id, mess_3, parse_mode='html')


@bot.message_handler(commands=['lesson_data'])
def lesson_1(message):
    if time_now()[2] == 6 or time_now()[2] == 7 or (time_now()[1] in holidays[time_now()[0] - 9]):
        bot.send_message(message.chat.id, 'Сегодня выходной')
    else:
        lessons = get_lessons()
        current_lesson_info = less(time_now()[3] * 60 + time_now()[4])
        if current_lesson_info[0] == 15:
            bot.send_message(message.chat.id, 'Уроки закончились')
        else:
            if current_lesson_info[0] % 2 == 1:
                now_less = lessons[current_lesson_info[0] // 2 - 1]
            else:
                now_less = None
            next_less = lessons[current_lesson_info[0] // 2]
            if now_less:
                mess = f'Сейчас - {now_less[1]}\nВ кабинете номер {now_less[2]}\nУчителя зовут {now_less[3]}'
                bot.send_message(message.chat.id, mess)
            mess_3 = f'Следующий урок - {next_less[1]}\nВ кабинете номер {next_less[2]}\nУчителя зовут {next_less[3]}'
            bot.send_message(message.chat.id, mess_3)


@bot.message_handler(commands=['messages'])
def messages(message):
    messages_1(message.chat.id)


@bot.message_handler(commands=['timetable'])
def timetable_1(message):
    if time_now()[2] == 6 or time_now()[2] == 7 or (time_now()[1] in holidays[time_now()[0] - 9]):
        bot.send_message(message.chat.id, 'Сегодня выходной')
    else:
        lessons = get_lessons()
        l = 1
        for less_1 in lessons:
            if l == 8:
                break
            mess = f'<b>{l} урок</b>\nУрок - {less_1[1]}\nВ кабинете номер {less_1[2]}\nУчителя зовут - {less_1[3]}'
            bot.send_message(message.chat.id, mess, parse_mode='html')
            l += 1


bot.polling(non_stop=True)
