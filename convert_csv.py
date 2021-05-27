#!/usr/bin/env python3
import json
import glob
import os
import csv

def convertFile(file):
    csvfilename = f'csv/{os.path.splitext(os.path.basename(file))[0]}.csv'
    print(file, csvfilename)

    with open(file, 'rt', encoding='utf-8') as f:
        data = json.load(f)

        rows = []
        for race in data:
            row = []
            row += [race["place"], race["placeid"], race["racenumber"]]
            racers = race["racers"]
            for racer in racers:
                row.extend([
                    racer["number"],
                    racer["name"],
                    racer["age"],
                    racer["area"],
                    racer["weight"],
                    racer["rank"],
                    racer["win_all"],
                    racer["sec_all"],
                    racer["win_cur"],
                    racer["sec_cur"],
                ])

            result = race["result"]
            results = result["results"]
            row.extend(results)

            rows.append(row)

        with open(csvfilename, 'wt', encoding='utf-8') as w:
            writer = csv.writer(w)

            header = ["place", "placeid", "racenumber", ]
            for i in range(1, 7):
                header += [f"number{i}", f"name{i}", f"age{i}", f"area{i}", f"weight{i}", f"rank{i}", f"win_all{i}", f"sec_all{i}", f"win_cur{i}", f"sec_cur{i}"]
            header += ["1st", "2nd", "3rd"]

            writer.writerow(header)            
            writer.writerows(rows)



def convertFiles(files):
    for file in files:
        convertFile(file)

if __name__ == '__main__':
    files = glob.glob('model/*.json')
    # files = ['model/m210525.json']
    convertFiles(files)
