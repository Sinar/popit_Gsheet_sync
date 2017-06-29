#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from dateutil import parser


def clean(label):
    return re.sub(r'[^\w\s]', '', label.lower())


def datetimeParser(date):
    '''
    Returns date of varying formats as ISO for Popit
    '''
    if date:
        datetime =parser.parse(date)
        datetime = datetime.isoformat().split('T')[0]
    else:
        datetime= ""
    
    return datetime

def seriesToDic(s):
    d = {}  
    for k,v in s.items():
        if v:
            d[k] = v
    return d
