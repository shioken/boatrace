#!/usr/bin/env python3

import re
import datetime

def trimLine(line):
    return re.sub('[ ]+', ' ', re.sub(r"[\u3000]", "", line)).split(' ')

def getOffsetToday(delta):
    target = datetime.datetime.today() + datetime.timedelta(days=delta)
    return target.strftime("%y%m%d")
    
def getStringToday():
    return getOffsetToday(0)

def getStringYesterday():
    return getOffsetToday(-1)

def getStringTommorow():
    return getOffsetToday(1)
