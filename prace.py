#!/usr/bin/env python3
import glob
import re
import os
import json

def trimLine(line):
    return re.sub('[ ]+', ' ', re.sub(r"[\u3000]", "", line)).split(' ')

def parsePlayer(line):
    (number, id, name, age, area, weight, rank, win_all, sec_all, win_cur, sec_cur) = (
        int(line[:1]),
        line[2:6],
        line[6:10],
        int(line[10:12]),
        line[12:14],
        int(line[14:16]),
        line[16:18],
        float(line[18:24]),
        float(line[24:30]),
        float(line[30:35]),
        float(line[35:41]),
    )

    obj = {}
    obj["number"] = number
    obj["name"] = name
    obj["age"] = age
    obj["area"] = area
    obj["weight"] = weight
    obj["rank"] = rank
    obj["win_all"] = win_all
    obj["sec_all"] = sec_all
    obj["win_cur"] = win_cur
    obj["sec_cur"] = sec_cur

    # print(obj)

    return obj


def parseRacelistFile(filename):
    # print(filename)

    date = filename[filename.rfind('/') + 1: filename.find('.')]

    (year, month, day) = (
        int(date[1:3]) + 2000,
        int(date[3:5]),
        int(date[5:]),
    )
    # print(year, month, day)

    lines = 0
    prevLine = ''
    nt = True
    lb = 0  # Line Break Flag '---'
    place = ''
    pline = False
    pcount = 0
    races = []
    race = {}
    racers = []
    with open(filename, 'r') as f:
        while True:
            line = f.readline()
            if line:
                if nt:
                    # タイトル取得(全角スペースを除去した後に連続する空白をまとめてから分割する)
                    titleline = trimLine(line)
                    place = titleline[0].replace('ボートレース', '')
                    # print(place)
                    nt = False
                elif pline:
                    racer = parsePlayer(line)
                    pcount += 1
                    racers.append(racer)
                    if pcount == 6:
                        race["racers"] = racers
                        races.append(race)
                        pline = False
                else:
                    if 'BGN' in line:
                        nt = True
                    elif 'END' in line:
                        nt = False
                    elif '---' in line:
                        lb += 1
                        if lb == 1:
                            raceinfo = trimLine(prevLine)
                            racenumber = int(raceinfo[0].translate(raceinfo[0].maketrans(
                                {chr(0xFF01 + i): chr(0x21 + i) for i in range(94)})).replace('R', ''))
                            # print(racenumber)

                            race = {}
                            race["place"] = place
                            race["racenumber"] = racenumber
                        else:
                            # 次の行から選手が出てくる
                            lb = 0
                            pline = True
                            pcount = 0
                            racers = []
    
                prevLine = line
                lines += 1
            else:
                break

    return races

def parseResult(line):
    if not 'R' in line:
        return (0, 0, 0)    # 同着の場合。とりあえず無視する

    racenumber = int(line[:line.find('R')])
    # print('race', racenumber)

    if '中　止' in line:
        # print('中止')
        return (-1, -1, -1)
    if '不成立' in line:
        return (-1, -1, -1)

    first = int(line[15:16])
    second = int(line[17:18])
    third = int(line[19:20])
    return (first, second, third)
    
def parseResultFile(filename):
    # print(filename)

    date = filename[filename.rfind('/') + 1: filename.find('.')]

    (year, month, day) = (
        int(date[1:3]) + 2000,
        int(date[3:5]),
        int(date[5:]),
    )
    # print(year, month, day)

    nt = False
    rt = False
    rn = 0
    results = []
    result = {}
    with open(filename, 'r') as f:
        while True:
            line = f.readline()
            if nt:
                place = trimLine(line)[0]
                place = place[: place.rfind('［')]
                # print(place)
                nt = False
            elif rt:
                fst = parseResult(line)
                if not fst == (0, 0, 0):
                    rn += 1
                    result = {}
                    result["place"] = place
                    result["racenumber"] = rn
                    result["results"] = list(fst)
                    results.append(result)
                    if rn == 12:
                        rt = False
                else:
                    print("同着スキップ")
            elif line:
                if 'BGN' in line:
                    nt = True
                # elif 'END' in line:
                    # print('END')
                elif '払戻金' in line:
                    rt = True
                    rn = 0
            else:
                break

    return results


def parseRacelistFiles(files):
    for file in files:
        parseRacelistFile(file)


def parseResultFiles(files):
    for file in files:
        parseResultFile(file)


def mergeRaceAndResult(races, results):
    emptyraces = []
    for race in races:
        # find result
        for result in results:
            if result["place"] == race["place"] and race["racenumber"] == result["racenumber"]:
                race["result"] = result
                break
        
        if not "result" in race:
            print("not result", race["place"], race["racenumber"])
            emptyraces.append(race)
            # return False
    
    for race in emptyraces:
        races.remove(race)

    return True


def parseFiles(kfiles):
    races = []
    results = []

    for kfile in kfiles:
        bfile = f"racelist/b{kfile[kfile.rfind('k') + 1:]}"
        if os.path.exists(bfile):
            print(kfile)
            la = True
            races = parseRacelistFile(bfile)
            results = parseResultFile(kfile)

            if mergeRaceAndResult(races, results):
                jsonfile = f"model/m{kfile[kfile.rfind('k') + 1: kfile.rfind('.txt')]}.json"
                # print(jsonfile)
                with open(jsonfile, 'wt', encoding='utf-8') as jf:
                    json.dump(races, jf, ensure_ascii = False, indent = 4)
        else:
            print(f"result file {bfile} is not exists")


if __name__ == '__main__':
    resultfiles = glob.glob('result/k*.txt')
    # resultfiles = ['result/k210524.txt']
    parseFiles(resultfiles)

