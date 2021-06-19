#!/usr/bin/env python3

import re
import datetime

RANKMAP = {
    'A1': [1.0, 0.0, 0.0, 0.0],
    'A2': [0.0, 1.0, 0.0, 0.0],
    'B1': [0.0, 0.0, 1.0, 0.0],
    'B2': [0.0, 0.0, 0.0, 1.0],
}

places = {'桐生': 1, '戸田': 2, '江戸川': 3, '平和島': 4, '多摩川': 5, '浜名湖': 6, '蒲郡': 7,
          '常滑': 8, '津': 9, '三国': 10, 'びわこ': 11, '琵琶湖': 11, '住之江': 12, '尼崎': 13, '鳴門': 14, '丸亀': 15, '児島': 16, '宮島': 17, '徳山': 18, '下関': 19, '若松': 20, '芦屋': 21, '福岡': 22, '唐津': 23, '大村': 24,}
          
def placeid(place):
    if place in places:
        return places[place]
    return 0

def rankmap(rank):
    if rank in RANKMAP:
        return RANKMAP[rank]
    return [0.0, 0.0, 0.0, 0.0]

def trimLine(line):
    return re.sub('[ ]+', ' ', re.sub(r"[\u3000]", "", line.strip())).split(' ')

def getOffsetToday(delta):
    target = datetime.datetime.today() + datetime.timedelta(days=delta)
    return target.strftime("%y%m%d")
    
def getStringToday():
    return getOffsetToday(0)

def getStringYesterday():
    return getOffsetToday(-1)

def getStringTommorow():
    return getOffsetToday(1)
