#!/usr/bin/env python3
import sys
import utils
import os
import re
import json
import matplotlib as mlp
import matplotlib.pyplot as plt

def draw_scatter(date, type):
    if not re.match("nn|lm", type):
        print("type not found. nn   or lm")
        return
    
    prefix = 'n' if type == 'nn' else 'l'
    pfile = f"predicted/{prefix}{date}.json"
    rfile = f"json/m{date}.json"

    if not os.path.exists(pfile):
        print(f"{pfile} is not exists.")
        return

    if not os.path.exists(rfile):
        print(f"{rfile} is not exists.")
        return

    with open(pfile, 'r', encoding='utf-8') as pf, open(rfile, 'r', encoding='utf-8') as rf:
        pjson = json.load(pf)
        rjson = json.load(rf)
        
if __name__ == '__main__':
    date = ""
    if len(sys.argv) > 1:
        date = sys.argv[1]
        if date == 'today':
            date = utils.getStringToday()
        elif date == 'yesterday':
            date = utils.getStringYesterday()

    if len(sys.argv) == 3:
        draw_scatter(date, sys.argv[2])
    elif len(sys.argv) == 2:
        draw_scatter(date, 'nn')
        draw_scatter(date, 'lm')
    else:
        print("draw_scatter.py date type(nn/lm)")
