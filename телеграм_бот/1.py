import sqlite3 as sq
days = ['monday.txt','tuesday.txt','wednesday.txt','thursday.txt','friday.txt']
with sq.connect('157610Г.db') as con:
    cur = con.cursor()
    for i in days:
        teach = []
        teach_2 = []
        file = open(i,encoding='utf-8')
        timetable = [i.split() for i in file.readlines()]

        for ind_2 in timetable:
            ind = timetable.index(ind_2)
            for b in ind_2:
                if '-' in b:
                    c = ind_2.index(b)
                    b = b.replace('-', ' ')
                    timetable[ind][c] = b
        for l in timetable:
            teach.append(l[-1])
        for p in teach:
            if not '/' in p:
                p = p.split()
                teach_2.append(f'{p[2]} {p[0]} {p[1]}')
            else:
                k = p.split('/')
                u = k[0].split()
                j = k[1].split()
                teach_2.append(f'{u[2]} {u[0]} {u[1]}/{j[2]} {j[0]} {j[1]}')
        ind = 1
        for t in teach_2:
            cur.execute(f'UPDATE {i[:-4]} SET teacher = ? WHERE id = ?',[t,ind])
            con.commit()
            ind+=1