#!/usr/bin/env python3
import os
import sys
import utils
import json
from datetime import datetime as dt
import show_deviation

def show_timelimit(date, limit=10):
    racefile = f'json/m{date}.json'
    if not os.path.exists(racefile):
        print(f"{racefile} is not exists.")
        return
    
    with open(racefile, 'r', encoding='utf-8') as rf:
        rjson = json.load(rf)

        now = dt.now().strftime('%H:%M')

        sorted_race = sorted(rjson, key=lambda x: x['timelimit'])
        filterd_race = filter(lambda x:x['timelimit'] > now, sorted_race)
        for i, race in enumerate(filterd_race):
            place = (race['place'] + "　　　")[:3]
            print("")
            print(f"{race['timelimit']} {place} {race['racenumber']:>2}R")
            print("")
            show_deviation.show_deviation(date, 'lm', race['place'], race['racenumber'])
            if i + 1 == limit:
                break



if __name__ == '__main__':
    date = ""
    limit = 10
    if len(sys.argv) < 3:
        date = utils.getStringToday()

    if len(sys.argv) == 2:
        limit = int(sys.argv[1])
    
    if len(sys.argv) == 3:
        date = sys.argv[2]
        if date == 'today':
            date = utils.getStringToday()
        elif date == 'yesterday':
            date = utils.getStringYesterday()

    
    show_timelimit(date, limit)
