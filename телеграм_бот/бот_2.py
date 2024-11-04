import telebot
from telebot import types
from datetime import datetime
import time
import threading
import sqlite3 as sq

bot = telebot.TeleBot('7528462585:AAFH6DKZdBZk3bNgEOpeI1yGZkwAwxudq8s')
next_time = []
first_time = []
already_sent = 0
dbs = ['157610Г.db']


def send(time1, db):
    user = users(db)
    h = lesson(db[:-3])[1]
    if h:
        for i in user:
            h = what_group(h, int(i))
            bot.send_message(int(i), f'Урок через {time1} минут')
            bot.send_message(int(i), f'Сейчас будет урок - {h[1]}\nУчителя зовут {h[2]}\nУрок будет в кабинете {h[3]}')


def what_group(les, ID):
    with sq.connect('users.db') as con:
        cur = con.cursor()
        group = cur.execute('SELECT gr FROM users_1 WHERE id = ?', [ID])
    group = group.fetchall()[0][0]
    res_lesson = []
    for i in les:
        i = str(i)
        if '/' in i:
            ind = i.index('/')
            if group == 1:
                h = i[:ind]
            elif group == 2:
                h = i[ind + 1:]
            else:
                h = i
        else:
            h = i
        res_lesson.append(h)
    return res_lesson


def first():
    global first_time, dbs
    first_time = []
    for i in dbs:
        with sq.connect(i) as con:
            cur = con.cursor()
            h = cur.execute('''SELECT start FROM time WHERE id = 1''')
        h = h.fetchall()
        first_time.append([h[0][0], '157610Г.db'])


def next_les():
    global next_time, dbs
    next_time = []
    for i in dbs:
        with sq.connect(i) as con:
            cur = con.cursor()
            h = cur.execute('''SELECT start FROM time WHERE start>?''', (time_now()[-1],))
            h = h.fetchall()
            if len(h):
                next_time.append([h[0][0], '157610Г.db'])
            else:
                next_time.append([0, '157610Г.db'])


def is_id(ID):
    with sq.connect('users.db') as con:
        cur = con.cursor()
        ids = cur.execute('SELECT id FROM users_1')
    ids = ids.fetchall()
    ids = [i[0] for i in ids]
    if ID in ids:
        return True
    else:
        return False


def is_holiday(DB):
    t = time_now()
    month = t[0]
    day = t[1]
    week = t[2]
    with sq.connect(f'{DB}.db') as con:
        cur = con.cursor()
        days = cur.execute('SELECT days FROM holidays WHERE month = ?', (month,))
    days = days.fetchall()[0][0]
    days = days.split()
    if str(day) in days or week in ['saturday', 'sunday']:
        return False
    else:
        return True


def get_db(ID):
    with sq.connect('users.db') as con:
        cur = con.cursor()
        user_db = cur.execute('SELECT class FROM users_1 WHERE id = ?', (ID,))
    user_db = user_db.fetchall()[0][0]
    return user_db


def send_all_messages():
    global next_time, first_time, already_sent
    while True:
        com_time = time_now()[-1]
        if already_sent != com_time:
            for i in range(len(next_time)):
                if is_holiday(next_time[i][1][:-3]):
                    if next_time[i][0] - com_time == 5:
                        send(5, next_time[i][1])
                        already_sent = com_time
                    if first_time[i][0] - com_time == 30:
                        send(30, first_time[i][1])
                        already_sent = com_time
        for i in next_time:
            if com_time >= i[0]:
                next_les()
        time.sleep(15)


def users(DB):
    with sq.connect('users.db') as con:
        cur = con.cursor()
        g = cur.execute('SELECT id FROM users_1 WHERE class = ? and messages = 1', (DB[:-3],))
    g = g.fetchall()
    g = [i[0] for i in g]
    return g


def time_now():
    time_1 = datetime.fromtimestamp(time.time())
    month = time_1.month
    day = time_1.day
    week = time_1.strftime('%A').lower()
    com_time = time_1.hour * 60 + time_1.minute
    return [month, day, week, com_time]


def lesson(DB):
    t = time_now()
    com_time = t[-1]
    day = t[-2]
    with sq.connect(f'{DB}.db') as con:
        cur = con.cursor()
        now_less = cur.execute(f'SELECT * FROM {day},time WHERE {day}.id = time.id and time.start <= ? and ? <= '
                               f'time.finish', [com_time, com_time])
        now_less = now_less.fetchall()
        if now_less:
            now_less = now_less[0]
        next_less = cur.execute(f'SELECT * FROM {day},time WHERE {day}.id = time.id and time.start > ?', [com_time])
        next_less = next_less.fetchall()
        if next_less:
            next_less = next_less[0]
    return [now_less, next_less]


@bot.message_handler(commands=['start'])
def start_1(message):
    g = is_id(message.chat.id)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if g:
        fun_2 = types.KeyboardButton('/help')
        fun_3 = types.KeyboardButton('/timetable')
        fun_4 = types.KeyboardButton('/lesson_data')
        fun_5 = types.KeyboardButton('/messages')
        change = types.KeyboardButton('/change_db')
        mess_1 = f'Привет, {message.from_user.first_name}'
        if message.from_user.username == 'topych_lfvb':
            fun_6 = types.KeyboardButton('/start')
            markup.add(fun_2, fun_3, fun_4, fun_5, change, fun_6)
        else:
            markup.add(fun_2, fun_3, fun_4, fun_5, change)
        bot.send_message(message.chat.id, mess_1)
        bot.send_message(message.chat.id, 'Выбери нужную команду или нажми \n/help для открытия инструкции',
                         reply_markup=markup)

    else:
        change = types.KeyboardButton('/change_db')
        markup.add(change)
        bot.send_message(message.chat.id,
                         'Вы еще не пользовались этим ботом\nНажмите команду /change_db чтобы выбрать класс',
                         reply_markup=markup)


@bot.message_handler(commands=['help'])
def help_1(message):
    g = is_id(message.chat.id)
    if g:
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
    <i>Уведомления приходят за 30 минут до начала первого урока и за 5 минут до начала каждого урока</i>\n\n
    <b>/change_db</b> - команда, чтобы поменять класс'''
        bot.send_message(message.chat.id, mess_2, parse_mode='html')
        mess_3 = '''
    Тех поддержка бота <b>@topych_lfvb</b>'''
        bot.send_message(message.chat.id, mess_3, parse_mode='html')
    else:
        bot.send_message(message.chat.id,
                         'Вы не ввели идентификатор вашего класса\nВам недоступны все функции этого бота')


@bot.message_handler(commands=['lesson_data'])
def lesson_1(message):
    g = is_id(message.chat.id)
    if g:
        db = get_db(message.chat.id)
        booling = is_holiday(db)
        if booling:
            lessons = lesson(db)
            if lessons[0] and lessons[1]:
                h1 = lessons[0]
                h2 = lessons[1]
                h1 = what_group(h1, message.chat.id)
                h2 = what_group(h2, message.chat.id)
                mess = f'Сейчас - {h1[1]}\nВ кабинете номер {h1[3]}\nУчителя зовут {h1[2]}'
                bot.send_message(message.chat.id, mess)
                mess_3 = f'Следующий урок - {h2[1]}\nВ кабинете номер {h2[3]}\nУчителя зовут {h2[2]}'
                bot.send_message(message.chat.id, mess_3)
            elif lessons[0]:
                h1 = lessons[0]
                h1 = what_group(h1, message.chat.id)
                mess_3 = f'Сейчас - {h1[1]}\nВ кабинете номер {h1[3]}\nУчителя зовут {h1[2]}'
                bot.send_message(message.chat.id, mess_3)
                bot.send_message(message.chat.id, 'Это последний урок')
            elif lessons[1]:
                h2 = lessons[1]
                h2 = what_group(h2, message.chat.id)
                mess_3 = f'Следующий урок - {h2[1]}\nВ кабинете номер {h2[3]}\nУчителя зовут {h2[2]}'
                bot.send_message(message.chat.id, mess_3)

            else:
                bot.send_message(message.chat.id, 'Уроки закончились')
        else:
            bot.send_message(message.chat.id, 'Сегодня нет уроков')
    else:
        bot.send_message(message.chat.id,
                         'Вы не ввели идентификатор вашего класса\nВам недоступны все функции этого бота')


@bot.message_handler(commands=['messages'])
def messages(message):
    g = is_id(message.chat.id)
    if g:
        con = sq.connect('users.db')
        cur = con.cursor()
        h = cur.execute('''SELECT messages FROM users_1 WHERE id = ?''', (message.chat.id,))
        h = h.fetchall()
        h = h[0][0]
        if h == 0:
            mess = 'Вы включили уведомления об уроках'
            h = 1
        else:
            mess = 'Вы выключили уведомления об уроках'
            h = 0
        cur.execute('''UPDATE users_1 SET messages = ? WHERE id = ?''', (h, message.chat.id))
        con.commit()
        bot.send_message(message.chat.id, mess)
        con.close()
    else:
        bot.send_message(message.chat.id,
                         'Вы не ввели идентификатор вашего класса\nВам недоступны все функции этого бота')


@bot.message_handler(commands=['timetable'])
def timetable_1(message):
    g = is_id(message.chat.id)
    if g:
        DB = get_db(message.chat.id)
        day = time_now()[2]
        booling = is_holiday(DB)
        if booling:
            lessons = lesson(DB)
            if lessons[0]:
                lessons = lessons[0]
            elif lessons[1]:
                lessons = lessons[1]
            else:
                lessons = 0
            con = sq.connect(f'{DB}.db')
            cur = con.cursor()
            g = cur.execute(f'SELECT * FROM {day}')
            g = g.fetchall()
            for i in g:
                i = what_group(i, message.chat.id)
                if lessons == 0:
                    mess = f'<strike><b>{i[0]} урок</b>\nУрок - {i[1]}\nВ кабинете номер {i[3]}\nУчителя зовут - {i[2]}</strike>'
                elif lessons == 1 or lessons[0] > int(i[0]):
                    mess = f'<strike><b>{i[0]} урок</b>\nУрок - {i[1]}\nВ кабинете номер {i[3]}\nУчителя зовут - {i[2]}</strike>'
                elif lessons[0] == int(i[0]):
                    mess = f'<b>{i[0]} урок\nУрок - {i[1]}\nВ кабинете номер {i[3]}\nУчителя зовут - {i[2]}</b>'
                else:
                    mess = f'<i><b>{i[0]} урок</b>\nУрок - {i[1]}\nВ кабинете номер {i[3]}\nУчителя зовут - {i[2]}</i>'
                bot.send_message(message.chat.id, mess, parse_mode='html')
            con.close()
        else:
            bot.send_message(message.chat.id, 'Сегодня нет уроков')
    else:
        bot.send_message(message.chat.id,
                         'Вы не ввели идентификатор вашего класса\nВам недоступны все функции этого бота')


@bot.message_handler(commands=['change_db'])
def change_db(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    class_1 = types.KeyboardButton('157610Г')
    markup.add(class_1)
    bot.send_message(message.chat.id, 'Выберите ваш класс', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def new_user(message):
    with sq.connect('users.db') as con:
        cur = con.cursor()
        if message.text == '157610Г':
            is_in = is_id(message.chat.id)
            if is_in:
                cur.execute('''UPDATE users_1 SET class = ?, gr = ? WHERE id = ?''', ('157610Г', 0, message.chat.id))
                con.commit()
                bot.send_message(message.chat.id, 'Вы успешно изменили свой класс на 10"Г" класс школы №1576')
            else:
                cur.execute('INSERT INTO users_1(id,class,gr,messages) VALUES (?,?,?,?)',
                            (message.chat.id, '157610Г', 0, 0))
                con.commit()
                bot.send_message(message.chat.id,
                                 'Вы успешно зарегистрировались в боте\nВаш класс - 10"Г"  школы №1576')
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            group_1 = types.KeyboardButton('группа 1')
            group_2 = types.KeyboardButton('группа 2')
            markup.add(group_1, group_2)
            bot.send_message(message.chat.id,
                             'Теперь вы обязательно должны выбрать вашу группу\n\nГруппа №1 - учителя: '
                             'Сарычева С.В, Талачев З.Р и Чистякова Е.В\n\nГруппа №2 - учителя: '
                             'Алексеенко М.В и Оганнесян Л.Р', reply_markup=markup)

        elif message.text == 'группа 1' or message.text == 'группа 2':
            class_1 = cur.execute('SELECT class FROM users_1 WHERE id = ?', [message.chat.id, ])
            class_1 = class_1.fetchall()
            if class_1[0][0] == '157610Г':
                cur.execute('UPDATE users_1 SET gr = ? WHERE id = ?', [int(message.text[-1]), message.chat.id])
                con.commit()
                bot.send_message(message.chat.id, 'Вы успешно выбрали группу')
                start_1(message)


first()
next_les()
threading.Thread(target=send_all_messages, daemon=True).start()


def main():
    while True:
        try:
            bot.polling(none_stop=True)
        except:
            time.sleep(5)


if __name__ == '__main__':
    main()
