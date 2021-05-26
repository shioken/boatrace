#!/usr/bin/env python3
import glob
import re

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

    print(obj)

    return obj


def parseRacelistFile(filename):
    print(filename)

    date = filename[filename.rfind('/') + 1: filename.find('.')]

    (year, month, day) = (
        int(date[1:3]) + 2000,
        int(date[3:5]),
        int(date[5:]),
    )
    print(year, month, day)

    lines = 0
    prevLine = ''
    nt = True
    lb = 0  # Line Break Flag '---'
    place = ''
    pline = False
    pcount = 0
    with open(filename, 'r') as f:
        while True:
            line = f.readline()
            # line = line.strip()
            if line:
                if nt:
                    # タイトル取得(全角スペースを除去した後に連続する空白をまとめてから分割する)
                    titleline = trimLine(line)
                    place = titleline[0].replace('ボートレース', '')
                    print(place)
                    nt = False
                elif pline:
                    parsePlayer(line)
                    pcount += 1
                    if pcount == 6:
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
                            racenumber = raceinfo[0].translate(raceinfo[0].maketrans(
                                {chr(0xFF01 + i): chr(0x21 + i) for i in range(94)})).replace('R', '')
                            print(racenumber)
                        else:
                            # 次の行から選手が出てくる
                            lb = 0
                            pline = True
                            pcount = 0
    
                prevLine = line
                lines += 1
            else:
                break
    print(lines)


def parseResult(line):
    racenumber = int(line[:line.find('R')])
    print('race', racenumber)

    if '中　止' in line:
        print('中止')
        return

    first = int(line[15:16])
    second = int(line[17:18])
    third = int(line[19:20])
    print(first, second, third)
    
def parseResultFile(filename):
    print(filename)

    date = filename[filename.rfind('/') + 1: filename.find('.')]

    (year, month, day) = (
        int(date[1:3]) + 2000,
        int(date[3:5]),
        int(date[5:]),
    )
    print(year, month, day)

    nt = False
    rt = False
    rn = 0
    with open(filename, 'r') as f:
        while True:
            line = f.readline()
            if nt:
                place = trimLine(line)[0][:2].rstrip('［')
                print(place)
                nt = False
            elif rt:
                parseResult(line)
                rn += 1
                if rn == 12:
                    rt = False
            elif line:
                if 'BGN' in line:
                    nt = True
                elif 'END' in line:
                    print('END')
                elif '払戻金' in line:
                    rt = True
                    rn = 0
            else:
                break


def parseRacelistFiles(files):
    for file in files:
        parseRacelistFile(file)


def parseResultFiles(files):
    for file in files:
        parseResultFile(file)

if __name__ == '__main__':
    # files = glob.glob('racelist/b*.txt')
    racelistfiles = ['racelist/b210525.txt']
    resultfiles = ['result/k210525.txt']
    parseRacelistFiles(racelistfiles)
    parseResultFiles(resultfiles)
