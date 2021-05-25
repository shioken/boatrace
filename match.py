#!/usr/bin/env python3
import glob

def trimfiles(files):
    tfiles = []
    for file in files:
        index = file.rfind('/')
        tfiles.append(file[index + 2 :])

    return tfiles



r_files = glob.glob('result/k*.txt')
b_files = glob.glob('racelist/b*.txt')

rt = trimfiles(r_files)
bt = trimfiles(b_files)

print(set(rt) ^ set(bt))
