#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests, re
import searchCLI, gSheet_utils, utils
import numpy as np

def personsUpdate(df, base_url, headers, gSheet_details):
    '''
    Updates data from df to Popit database
    Inputs:
        df: df to import from
        base_url: base_url of Popit DB
        headers: request headers for Popit DB
        gSheet_details: dic containing details of gSheet synced from
        
    '''
    df.is_copy = False
    #Remove entries with no names
    #df = df[df['name_en']!= ""]
    named= df['name_en'].replace('', np.nan).dropna().index.values
    df = df.iloc[named]
    
    #ADD NEW PERSONS
    newPersons = df[df['person_id']== ""]
    for i in newPersons.index:
        person=  newPersons.loc[i]
        personName = person['name_en']
        person_id = searchCLI.searchCLI(base_url, personName, 'persons', 'name', 'other_names', headers, ['birth_date'])
        if person_id:
            #set id of person as id found
            df.loc[i, 'person_id'] = person_id
            
        
    #ADD/UPDATE PERSONS
    df.apply(lambda row: updatePopitPersons(row, gSheet_details, base_url, headers), axis=1)

def updatePopitPersons(row, gSheet_details, base_url, headers):
    '''
    Posts data from row to Popit, and updates corresponding Gsheet
    '''
    gSheet_idx = row.pop('gSheet_index')
    personID = row['person_id']
    sub_langs = gSheet_details['sub_langs']
    try:
        row['birth_date']= utils.datetimeParser(row['birth_date'])
        row['death_date']= utils.datetimeParser(row['death_date'])
    except ValueError:
        print("Date parsing error at {}: Birthdate: {}, Deathdate: {}".format(gSheet_idx, row['birth_date'], row['death_date']))
    r_json = update_allLangs('persons', personID, base_url, headers, row, sub_langs)
    if r_json:
        updatePersonGsheetIDs(r_json, gSheet_details, gSheet_idx)
        print("{} Success".format(gSheet_idx))

    
def update_allLangs(popit_className, classID, base_url, headers, payload, sub_langs):
    '''
    Update/post to Popit class with entries for en and all sub_langs
    sub_langs = list of sub_langs, eg. ['mm', 'my']
    '''
    #DF of all non_lang and EN entries
    pl = payload.filter(regex=r'(?<!{})$'.format("|".join(sub_langs)), axis=0)
    pl.index= [colName.split('_'+'en')[0] for colName in pl.index]   #remove lang suffix
    pl_en = generatePayload_row(pl)
    url_en = "{}/{}/{}/".format(base_url, 'en', popit_className)
       
    class_exists = requests.get(url_en+classID)
    if class_exists.ok: #Already existing, update
        r_en = requests.put(url_en+classID, headers=headers, json=pl_en)
    else:   #Post new entry
        r_en = requests.post(url_en, headers=headers, json=pl_en)   
    
    #Post/update sublangs
    if r_en.ok:
        try:
            r_json = r_en.json()['result']
        except KeyError:
            r_json = r_en.json()
        
        classID = r_json['id']
        for sl in sub_langs:
            #df of only sublang entries
            pl_sl= payload.filter(regex=r'(?<={})$'.format(sl), axis=0) 
            pl_sl.index= [colName.split('_'+sl)[0] for colName in pl_sl.index]   #remove lang suffix
            if pl_sl['other_names']:
                try:
                    pl_sl['other_names'] = [{'name': otherName} for otherName in pl_sl['other_names'].split(',')]
                except KeyError:
                    pass
            pl_sl['id'] = classID
            url_sl = "{}/{}/{}/{}".format(base_url, sl, popit_className, classID)
            pl_sublang = utils.seriesToDic(pl_sl) 
            r = requests.put(url_sl, headers=headers, json=pl_sublang)

        return r_json

    else:
        print(r_en.content)
        
def updatePersonGsheetIDs(json, gSheet_details, gSheet_idx):
    '''
    Updates GSheet with newly generated IDs from successful Popit update
    '''
    col_AI_map = gSheet_details['col_AI_map']
    sheetID = gSheet_details['sheetID']
    sheetName = gSheet_details['sheetName']
    
    personID = json['id']
    
    gSheet_utils.updateGSheetCell(personID, sheetID, sheetName, col_AI_map['person_id'], gSheet_idx)
     
    #Update gSheet with contact detail ID
    cd_posted = json['contact_details']
    for i in range(len(cd_posted)):
        colName = 'contact_'+ cd_posted[i]['type'] + '_id'
        try: 
            AI_not = col_AI_map[colName]
            cd_id = cd_posted[i]['id']
            gSheet_utils.updateGSheetCell(cd_id, sheetID, sheetName, AI_not, gSheet_idx)
       
        except KeyError:
            pass
        
    #Update gSheet with link details IDs
    lk_posted = json['links']
    for i in range(len(lk_posted)):
        colName = 'link_'+ lk_posted[i]['note'] + '_id'
        try:
            AI_not = col_AI_map[colName]
            lk_id = lk_posted[i]['id']
            gSheet_utils.updateGSheetCell(lk_id, sheetID, sheetName, AI_not, gSheet_idx)

        except KeyError:
            pass

    #Update gSheet with feature values
    


    
def generatePayload_row(row):
    '''
    Generate complete payloads for a single row
    row: Pandas series
    '''
    
    contacts = row.filter(regex=r'^contact_')
    links = row.filter(regex=r'^link_')
    rest = row.filter(regex=r'^(?!link_|contact_)')
    payload = rest.to_dict()
    
    #Other_names payload
    if payload['other_names']:    
        payload['other_names'] = [{'name': otherName} for otherName in payload['other_names'].split(',')]
    
    #Get contacts and links payloads
    contactP = getContactPayload(contacts)
    linkP = getLinkPayload(links)
    
    #Merge all
    payload['contact_details'] = contactP
    payload['links'] = linkP
    
    payload = utils.seriesToDic(payload)
    return payload
           
        
def getContactPayload(contact):
    cd = {}
    #groupby type of contact
    for key, value in sorted(contact.iteritems()):
        cd.setdefault(extractType(key), []).append(contact[key])
    #create payload only if value is not null
    payload = [{'type': k, 'value': cd[k][0], 'id': cd[k][1]}  for k in cd.keys() if cd[k][0]]
    return payload

def getLinkPayload(link):
    lnk =  {}
    #groupby type of link
    for key, value in sorted(link.iteritems()):
        lnk.setdefault(extractType(key), []).append(link[key])
    
    #create payload only if url is not null
    payload = [{'note': k, 'url': lnk[k][0], 'id': lnk[k][1]}  for k in lnk.keys() if lnk[k][0]]
    return payload


def extractType(k):
    match =re.search(r'(?<=\_).*?(?=(?:\_|$))', k).group()  #match between '_' or till end of str
    return match


             
