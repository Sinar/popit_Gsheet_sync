#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 15 17:20:46 2017

@author: metamatical
"""

#Import orgs

import utils
import requests

sheetID = '15VyBvMzO3dK7_5azS-0Rn5V4ASFhOKug4lv34GFUK0Q'
sheetName = 'Organizations'

base_url = "http://api.openhluttaw.org"
token = open('../oAuth/token_my.txt').read()
headers = {'Authorization': token.rstrip()}
sub_langs = ['my']

df, col_AI_map = gSheet_utils.importGSheetAsDF(sheetID, sheetName)

df.pop('geographic_area')
df.pop('parent_org_en')
df.pop('parent_org_mm')

df.apply(lambda row: syncOrgs(row, base_url, headerssub_langs), axis=1)
        
def syncOrgs(row, base_url, headers, sub_langs)
    popit_id = row['popit_id']
    if popit_id:
        r_org = requests.get(url+popit_id)
        if r_org.status_code != 201:
            popit_id = ""
    
    org_id = update_allLangs('organizations', popit_id, base_url, headers, orgP, sub_langs)
    


def update_allLangs(popit_className, classID, base_url, headers, payload, sub_langs):
    '''
    Update/post to Popit class with entries for en and all sub_langs
    sub_langs = list of sub_langs, eg. ['ms', 'my']
    '''
    #DF of all non_lang and EN entries
    pl = payload.filter(regex=r'(?<!{})$'.format("|".join(sub_langs)), axis=0)
    pl.index= [colName.split('_'+'en')[0] for colName in pl.index]   #remove lang suffix
    
    url_en = "{}/en/{}/{}".format(base_url, popit_className, classID)  
    pl_en = utils.seriesToDic(pl)
             
    if classID: #Already existing, update
        r_en = requests.put(url_en, headers=headers, json=pl_en)
    else:   #Post new entry
        r_en = requests.post(url_en, headers=headers, json=pl_en)   
        if r_en.ok:
            try:
                classID = r_en.json()['result']['id']
            except KeyError:
                classID = r_en.json()['id']
                
        else:
            print(pl_en)
            print(r_en.content)
            
        
    for sl in sub_langs:
        #df of only sublang entries
        pl_sl= payload.filter(regex=r'(?<={})$'.format(sl), axis=0) 
        pl_sl.index= [colName.split('_'+sl)[0] for colName in pl_sl.index]   #remove lang suffix
        pl_sl['id'] = classID
        url_sl = "{}/{}/{}/{}".format(base_url, sl, popit_className, classID)
        pl_sublang = utils.seriesToDic(pl_sl) 
        r = requests.put(url_sl, headers=headers, json=pl_sublang)


    return classID