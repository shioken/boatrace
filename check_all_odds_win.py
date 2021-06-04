#!/usr/bin/env python3
import glob
import os
import sys
import check_odds_win as cow

def check_all_odds(date):
    files = glob.glob(f'odds/w{date}*.json')
    print(len(files))
    for file in files:
        cow.check_odds(file)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        check_all_odds(sys.argv[1])
    else:
        print("check_all_odds date")
