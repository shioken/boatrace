#!/usr/bin/env python3
import sys
import utils
import os
import re
import json
import numpy as np

def show_deviation(date, type):
    if not re.match("nn|lm", type):
        print("type not found. nn   or lm")
        return
    
    prefix = 'n' if type == 'nn' else 'l'
    pfile = f'predicted/{prefix}{date}.json'
    if not os.path.exists(pfile):
        print(f"{pfile} is not exists.")
        return

    with open(pfile, 'r', encoding='utf-8') as pf:
        pjson = json.load(pf)
        for place in pjson['places']:
            print(place['name'])
            for race in place['races']:
                print(f"{race['number']:2}R")
                scores = np.array(list(map(lambda x: x['score'], race['racers'])))
                std = np.std(scores)
                avg = np.average(scores)

                print(f"std: {std:2.8f} avg: {avg:2.8f}")
                for i, racer in enumerate(race['racers']):
                    print(f" {racer['course']} {racer['name']} {racer['score']: 2.8f} {(scores[i] - avg) / std * 10 + 50: 2.8f}")
                    
        
    

if __name__ == '__main__':
    date = ""
    if len(sys.argv) > 1:
        date = sys.argv[1]
        if date == 'today':
            date = utils.getStringToday()
        elif date == 'yesterday':
            date = utils.getStringYesterday()

    if len(sys.argv) == 3:
        show_deviation(date, sys.argv[2])
    elif len(sys.argv) == 2:
        show_deviation(date, 'nn')
        show_deviation(date, 'lm')
    else:
        print("show_deviation.py date type(nn/lm)")
