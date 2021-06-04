#!/usr/bin/env python3
import sys
import scrap_odds_win as sow

def scrap_all_odds(date):
    for place in range(24):
        for race in range(12):
            outfile = sow.scrap_odds(date, str(place + 1), race + 1)
            if outfile is None:
                break

if __name__ == '__main__':
    if len(sys.argv) == 2:
        scrap_all_odds(sys.argv[1])
    else:
        print("scrap_all_odds_win.py date")
