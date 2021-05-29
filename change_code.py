#!/usr/bin/env python3
import subprocess
import glob

def changeCode(dir):
    files = glob.glob(f'{dir}/*.txt')
    for file in files:
        print(file)
        cmd = f"nkf -w --overwrite {file}"
        subprocess.call(cmd, shell=True)


if __name__ == '__main__':
    changeCode('result')
    changeCode('racelist')
