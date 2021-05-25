#!/usr/bin/env python3
import glob
import re

players = set()

def parseLine(line):
    number = line[:4]
    offset = 4
    name = line[offset: offset + 8]

    # Shift-JIS -> UTF-8変換時に半角カナの濁点が一文字に変換されているので文字数が合わない
    newline = line[offset:]

    p = re.compile('[\u30A1-\u30FF]+ ')
    while True:
        result = p.search(newline)
        if result:
            newline = newline[result.end():]
        else:
            break

    newline = newline.lstrip(' ')

    offset = 0
    shibu = newline[offset: offset + 2]
    offset += 2
    rank = newline[offset: offset + 2]
    offset += 2

    offset = 19
    blood = newline[offset: offset + 2]
    offset += 2
    winrate = newline[offset: offset + 4]
    offset += 4
    multirate = newline[offset: offset + 4]
    offset += 4
    wincount = int(newline[offset: offset + 3])
    offset += 3
    secondcount = int(newline[offset: offset + 3])
    offset += 3
    racecount = int(newline[offset: offset + 3])
    offset += 3
    champrace = int(newline[offset: offset + 2])
    offset += 2
    champcount = int(newline[offset: offset + 2])
    offset += 2
    avgstart = newline[offset: offset + 3]
    
    offset = 142
    preiod_from = int(newline[offset: offset + 8])
    offset += 8
    preiod_to = int(newline[offset: offset + 8])

    # 文字列 → 数値
    winrate_val = float(f'{winrate[:2]}.{winrate[2:]}')
    multirate_val = float(f'{multirate[:2]}.{multirate[2:]}')
    avgstart_val = float(f'{avgstart[:2]}.{avgstart[2:]}')

    print(number, name, shibu, rank, blood, winrate_val, multirate_val, avgstart_val, preiod_from, preiod_to)



    # if number in players:
    #     print(f"{number}: 存在")
    
    players.add(number)

def parseFile():
    # fanfiles = glob.glob('fan/fan*.txt')
    fanfiles = ['fan/fan2010.txt']
    lines = 0

    for fanfile in fanfiles:
        print(fanfile)
        with open(fanfile, 'r') as file:
            while True:
                line = file.readline()
                line = line.strip()
                if line:
                    parseLine(line)
                    lines += 1
                else:
                    break

    print(lines, len(players))

if __name__ == '__main__':
    parseFile()
