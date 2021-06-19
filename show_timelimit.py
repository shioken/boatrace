#!/usr/bin/env python3
import os
import sys
import utils
import json

def show_timelimit(date):
    racefile = f'json/m{date}.json'
    if not os.path.exists(racefile):
        print(f"{racefile} is not exists.")
        return
    
    with open(racefile, 'r', encoding='utf-8') as rf:
        rjson = json.load(rf)

        sorted_race = sorted(rjson, key=lambda x: x['timelimit'])
        for race in sorted_race:
            place = (race['place'] + "　　　")[:3]
            print(f"{race['timelimit']} {place} {race['racenumber']:>2}R")

if __name__ == '__main__':
    date = ""
    if len(sys.argv) == 1:
        date = utils.getStringToday()
    elif len(sys.argv) > 1:
        date = sys.argv[1]
        if date == 'today':
            date = utils.getStringToday()
        elif date == 'yesterday':
            date = utils.getStringYesterday()
    
    show_timelimit(date)
