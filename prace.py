#!/usr/bin/env python3
import glob
import re

def trimLine(line):
    return re.sub('[ ]+', ' ', re.sub(r"[\u3000]", "", line)).split(' ')

def parsePlayer(line):
    number = int(line[:1])
    id = line[2:6]
    name = line[6:10]
    age = int(line[10:12])
    area = line[12:14]
    weight = int(line[14:16])
    rank = line[16:18]
    data = line[19:]
    parts = re.sub('[ ]+', ' ', data).split(' ')
    print('len', len(parts))
    win_all = float(parts[0])
    sec_all = float(parts[1])
    win_cur = float(parts[2])
    sec_cur = float(parts[3])

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


def parseFile(filename):
    print(filename)

    date = filename[filename.rfind('/') + 1: filename.find('.')]

    year = int(date[1:3]) + 2000
    month = int(date[3:5])
    day = int(date[5:])
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
                        print("START")
                        nt = True
                    elif 'END' in line:
                        print("END")
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

def parseFiles(files):
    for file in files:
        parseFile(file)
    
    print(len(files))


if __name__ == '__main__':
    # files = glob.glob('racelist/b*.txt')
    files = ['racelist/b210525.txt']
    parseFiles(files)
