#!/usr/bin/env python3
import glob
import re
import os
import json
import sys
import utils
import datetime

def parsePlayer(line):
    (number, id, name, age, area, weight, rank, win_all, sec_all, win_cur, sec_cur, motor_no, motor_ratio, boat_no, boat_ratio, season_result) = (
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
        int(line[41:44]),
        float(line[44:50]),
        int(line[50:53]),
        float(line[53:59]),
        line[60:66],
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
    obj["motor_no"] = motor_no
    obj["motor_ratio"] = motor_ratio
    obj["boat_no"] = boat_no
    obj["boat_ratio"] = boat_ratio

    season_result = re.sub(r"[ FLSK]", "0", season_result)

    for i in range(6):
        obj[f"r{i + 1}"] = season_result[i:i + 1]

    # print(obj)

    return obj


def parseRacelistFile(filename):
    # print(filename)

    places = {'桐生':1, '戸田':2, '江戸川':3, '平和島':4, '多摩川':5, '浜名湖':6, '蒲郡':7,
              '常滑':8, '津':9, '三国':10, 'びわこ':11, '琵琶湖':11, '住之江':12, '尼崎':13, '鳴門':14, '丸亀':15, '児島':16, '宮島':17, '徳山':18, '下関':19, '若松':20, '芦屋':21, '福岡':22, '唐津':23, '大村':24, }
    
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
                    titleline = utils.trimLine(line)
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
                            raceinfo = utils.trimLine(prevLine)
                            racenumber = int(raceinfo[0].translate(raceinfo[0].maketrans(
                                {chr(0xFF01 + i): chr(0x21 + i) for i in range(94)})).replace('R', ''))
                            # print(racenumber)

                            race = {}
                            race["place"] = place
                            race["placeid"] = places[place]
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
        return None    # 同着の場合。とりあえず無視する

    racenumber = int(line[:line.find('R')])
    # print('race', racenumber)

    res = {}

    if '中　止' in line:
        # print('中止')
        res["1st"] = -1
        res["2nd"] = -1
        res["3rd"] = -1
        return res
    if '不成立' in line:
        res["1st"] = -1
        res["2nd"] = -1
        res["3rd"] = -1
        return res

    tr = utils.trimLine(line.strip())
    # print(tr)

    res["1st"] = int(tr[1][0:1])
    res["2nd"] = int(tr[1][2:3])
    res["3rd"] = int(tr[1][4:5])

    res["tierce"] = int(tr[2])  # 3連単
    if re.findall('特払い|不成立', tr[3]):
        res["show"] = 70
        tr.insert(3, "70")
    else:
        res["trio"] = int(tr[4])        # 3連複
    res["quinella"] = int(tr[6])  # 2連単
    if '特払い' in tr[7]:
        res["show"] = 70
    else:
        res["show"] = int(tr[8])        # 2連複

    return res
    
def parserOrder(line, order):
    tr = utils.trimLine(line)
    return {f'c{tr[2]}': tr[1]}

def parseWin(line, place, racenumber, results):
    tr = utils.trimLine(line)
    # print(place, racenumber, tr)
    result = list(filter(lambda x: x['place'] == place and x['racenumber'] == racenumber, results))
    if len(result) > 0:
        if len(tr) >3:
            result[0]["win"] = int(tr[3])
        else:
            result[0]["win"] = 100  # k160521 下関 3Rに単勝の払戻金が無い


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
    racenumber = 0
    inOrder = False
    orders = {}
    order = 0
    inr = False # レースごとの結果の中の"不成立"を判定しない
    with open(filename, 'r') as f:
        while True:
            line = f.readline()
            # print(line)
            if nt:
                place = utils.trimLine(line)[0]
                place = place[: place.rfind('［')]
                # print(place)
                racenumber = 1
                nt = False
            elif rt:
                fst = parseResult(line)
                if not fst is None:
                    rn += 1
                    result = {}
                    result["place"] = place
                    result["racenumber"] = rn
                    # result["results"] = list(fst)
                    result.update(fst)
                    results.append(result)
                    if rn == 12:
                        rt = False
                        ir = False
                        inr = False
                else:
                    print("同着スキップ")
            elif inOrder:
                orderResult = parserOrder(line, order)
                # print(orderResult)
                orders.update(orderResult)
                order += 1
                inOrder = order < 7
                if not inOrder:
                    result = list(filter(lambda x: x['place'] == place and x['racenumber'] == racenumber, results))
                    if len(result) > 0:
                        result[0].update(orders)
            elif line:
                if 'BGN' in line:
                    nt = True
                    inr = True
                elif '払戻金' in line:
                    rt = True
                    rn = 0
                elif '不成立' in line:
                    if not inr:
                        racenumber = 1 if racenumber + 1 == 13 else racenumber + 1
                    elif 'レース不成立' in line:
                        racenumber = 1 if racenumber + 1 == 13 else racenumber + 1
                    inr = True

                elif '単勝' in line:
                    parseWin(line, place, racenumber, results)
                    racenumber = 1 if racenumber + 1 == 13 else racenumber + 1
                    inr = True
                elif '---' in line:
                    inOrder = True
                    orders = {}
                    order = 1
                    
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


def parseFiles(kfiles, force=False):
    races = []
    results = []

    for kfile in kfiles:
        bfile = f"racelist/b{kfile[kfile.rfind('k') + 1:]}"
        if os.path.exists(bfile):
            print(kfile)
            la = True
            races = parseRacelistFile(bfile)
            results = parseResultFile(kfile)

            jsonfile = f"json/m{kfile[kfile.rfind('k') + 1: kfile.rfind('.txt')]}.json"
            if not force and os.path.exists(jsonfile):
                print(f"{jsonfile} is exists")
                continue

            if mergeRaceAndResult(races, results):
                print("output", jsonfile)
                with open(jsonfile, 'wt', encoding='utf-8') as jf:
                    json.dump(races, jf, ensure_ascii = False, indent = 4)
        else:
            print(f"result file {bfile} is not exists")


def parseFile(date):
    parseFiles([f"result/k{date}.txt"], True)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        date = sys.argv[1]
        if sys.argv[1] == 'today':
            date = utils.getStringToday()
        elif sys.argv[1] == 'yesterday':
            date = utils.getStringYesterday()

        parseFile(date)
    else:
        resultfiles = sorted(glob.glob('result/k*.txt'))
        # resultfiles = ['result/k210525.txt']
        parseFiles(resultfiles)
