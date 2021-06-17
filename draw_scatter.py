#!/usr/bin/env python3
import sys
import utils
import os
import re
import matplotlib as mlp
import matplotlib.pyplot as plt

def draw_scatter(date, type):
    if not re.match("nn|lm", type):
        print("type not found. nn   or lm")
        return
    

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
