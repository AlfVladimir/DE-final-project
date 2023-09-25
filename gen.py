# Генерация "правдоподобного" дата-сета, список звонков

import numpy as np
import random
import csv
import datetime
from faker import Faker
from scipy.stats import skewnorm

def daterange(start_date, end_date):
    ''' Функция range для диапазона дат
    '''
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

# Функции для рандомизации
ra = lambda x: int(x * random.uniform(0.9,1.1))
rap = lambda x: int(x * random.uniform(1.01,1.2))

# Номерной диапазон
nums_st = 10000
nums_en = 65999

kod = 55588
kod_pref = kod * 10**5

fnum_st = kod_pref+nums_st
fnum_en = kod_pref+nums_en

# Молчуны (не разговаривают)
silents_count = rap(10000)
silents = {random.randint(fnum_st,fnum_en) for _ in range(silents_count)}

# Трепачи (активно звонят)
talkers_count = rap(500)
talkers_prob = 0.05
talkers = [random.randint(fnum_st,fnum_en) for _ in range(talkers_count)]


def get_teid(na,nb):
    ''' Определение АТС которой принадлежит номер
    '''
    if na < fnum_st or na > fnum_en:
        return 8
    na = na - kod_pref
    ret = 0
    if 10000 <= na <=19999:
        ret = 1
    elif 20000 <= na <=39999:
        ret = 3
    elif 40000 <= na <=49999:
        ret = 2
    elif 50000 <= na <=59999:
        ret = 4
    elif 60000 <= na <=65999:
        ret = 5
    return ret

# Вероятности для направления
dir_prob = [0.4,0.3,0.3]

# Диапазон для продолжительности вызовов со "скошенным" распределением
dur_rand_count = 1000
dur_rand = skewnorm.rvs(a = 10 ,loc = 2, scale = 25,size = dur_rand_count).astype(int)

# Тенденции (вероятности) для разных периодов
# месяцы
months_r = [1.1, 0.8, 0.9, 0.8, 1, 0.8, 0.7, 0.9, 1.2, 1.1, 1, 1.2]
# дни недели
wds_r = [1, 1.1, 1.2, 1.3, 1.2, 0.7, 0.6]
# часы
hrs_r = [0.1, 0.05, 0.04, 0.03, 0.04, 0.1, 0.2, 0.5, 1 , 1.2,
         1.4,  1.5,  1.8,  1.4,  1.3, 1.5, 1.6, 1.2, 1 , 1.1,
           1,  0.8,  0.6,  0.3
         ]

# В среднем вызовов за день 
day_count = 22222
day_count = rap(day_count)

# Период формирования
dt_start = datetime.date(2022,1,1)
dt_end = datetime.date(2022,12,31)

# "Особые" дни (обычно всплеск вызовов)
vip_days = [
    datetime.date(2022,1,1),
    datetime.date(2022,12,31),
    datetime.date(2022,2,23),
    datetime.date(2022,3,8),
    datetime.date(2022,9,1),
    ]

# Аномалии
insight = {
    datetime.date(2022,7,20):['+',[2,3,4,5]],
    datetime.date(2022,3,23):['-',[8,9,10,11,12,13,14]],
}

with open('calls.csv','a',newline='') as file:

    writer = csv.writer(file,delimiter=';')

    for cur_dt in daterange(dt_start,dt_end):
        cur_day_count = day_count
        cur_day_count *= months_r[cur_dt.month-1]
        cur_day_count *= wds_r[cur_dt.weekday()]
        cur_day_count = ra(cur_day_count)

        if cur_dt in vip_days:
            for _ in range(5):
                cur_day_count = rap(cur_day_count)

        for cur_call in range(cur_day_count):
            cur_hour = random.choices(range(24),weights=hrs_r)[0]
            cur_datetime = datetime.datetime.combine(
                cur_dt,
                datetime.time(cur_hour,random.randint(0,59),random.randint(0,59))
            )

            cur_dur = abs(random.choices(dur_rand)[0] * random.randint(1,3))+1

            dir = random.choices([0,1,2],weights= dir_prob)[0]

            if random.choices([0,1],weights=[1-talkers_prob,talkers_prob])[0]:
                a = random.choices(talkers)[0]
            else:
                a = random.randint(fnum_st,fnum_en)
                while a not in silents:
                    a = random.randint(fnum_st,fnum_en)

            b = random.randint(fnum_st,fnum_en)

            if dir == 1:
                a = random.randint(10**10,10**11-1)
            elif dir == 2:
                b = random.randint(10**10,10**11-1)

            teid = get_teid(a,0)

            if cur_dt in insight:
                if cur_hour in insight[cur_dt][1]:
                    if insight[cur_dt][0] == '+':
                        for _ in range(10):
                            writer.writerow([cur_datetime, a, b, cur_dur, dir, teid])
                else:
                    writer.writerow([cur_datetime, a, b, cur_dur, dir, teid])
            else:
                writer.writerow([cur_datetime, a, b, cur_dur, dir, teid])

