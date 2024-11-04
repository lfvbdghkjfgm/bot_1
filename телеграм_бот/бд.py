import sqlite3 as sq

com_time = 610
day = 'wednesday'
con = sq.connect(f'157610Г.db')
cur = con.cursor()
now_less_id = cur.execute('SELECT id FROM time WHERE start < ? and finish > ?', (com_time, com_time))
now_less_id = cur.execute(f'SELECT {day}.id, {day}.lesson, {day}.teacher, {day}.class FROM {day},time WHERE time.start < ? and finish > ? and {day}.id = time.id',[com_time,com_time])
now_less_id = now_less_id.fetchall()
if not len(now_less_id):
    now_less = 0
else:
    now_less = now_less_id[0]
print(now_less)

next_less_id = cur.execute('SELECT id FROM time WHERE start > ?', (com_time,))
next_less_id = next_less_id.fetchall()
if len(next_less_id):
    next_less = cur.execute(f'SELECT * FROM {day} WHERE id = ?', (next_less_id[0][0],))
    next_less = next_less.fetchall()[0]
else:
    next_less = 0

con.close()




# @bot.message_handler(commands=['group_1'])
# def group_1(message):
#     con = sq.connect('users.db')
#     cur = con.cursor()
#     class_1 = cur.execute('SELECT class FROM users_1 WHERE id = ?', [message.chat.id, ])
#     class_1 = class_1.fetchall()
#     if class_1[0][0] == '157610Г':
#         cur.execute('UPDATE users_1 SET gr = ? WHERE id = ?', [1, message.chat.id])
#         con.commit()
#         bot.send_message(message.chat.id, 'Вы успешно выбрали группу')
#         start_1(message)
#     con.close()
#
#
# @bot.message_handler(commands=['group_2'])
# def group_2(message):
#     con = sq.connect('users.db')
#     cur = con.cursor()
#     class_1 = cur.execute('SELECT class FROM users_1 WHERE id = ?', [message.chat.id, ])
#     class_1 = class_1.fetchall()
#     if class_1[0][0] == '157610Г':
#         cur.execute('UPDATE users_1 SET gr = ? WHERE id = ?', [2, message.chat.id])
#         con.commit()
#         bot.send_message(message.chat.id, 'Вы успешно выбрали группу')
#         start_1(message)
#     con.close()