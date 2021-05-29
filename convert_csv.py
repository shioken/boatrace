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

        scores = (8, 3, 1)

        rows = []
        for race in data:
            result = race["result"]
            results = result["results"]
            print(results)
            # row.extend(results)

            racers = race["racers"]
            for i, racer in enumerate(racers):
                row = []

                score = 0
                if (i + 1) in results:
                    r = results.index(i + 1)
                    score = scores[r]

                row += [score]

                row += [race["place"], race["placeid"], race["racenumber"]]
                row += [
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
                ]

                if results[0] > -1:
                    rows.append(row)
                else:
                    print("skip race(中止)")

        with open(csvfilename, 'wt', encoding='utf-8') as w:
            writer = csv.writer(w)

            header = []
            # header += ["1st", "2nd", "3rd"]
            header += ["winscore"]
            header += ["place", "placeid", "racenumber", ]
            header += ["number", "name", "age", "area", "weight", "rank", "win_all", "sec_all", "win_cur", "sec_cur"]
            # for i in range(1, 7):
            #     header += [f"number{i}", f"name{i}", f"age{i}", f"area{i}", f"weight{i}", f"rank{i}", f"win_all{i}", f"sec_all{i}", f"win_cur{i}", f"sec_cur{i}"]

            writer.writerow(header)            
            writer.writerows(rows)



def convertFiles(files):
    for file in files:
        convertFile(file)

if __name__ == '__main__':
    # files = glob.glob('model/*.json')
    files = ['model/m210525.json']
    convertFiles(files)
