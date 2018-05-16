#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import searchCLI
import gSheet_utils
import utils



def genPayload(base_url, headers, row, orgID, gSheet_details, sub_langs):
    '''
    Generates membership payload based on row and updates to Popit database
    Inputs:
        base_url: base_url of Popit DB
        headers: request headers for Popit DB
        row: pandas series object
        orgID: organization of ID for membership
        gSheet_details: dic containing details of gSheet synced from
        sub_langs: List of sub languages to update eg. ['my'], or ['ms', 'cn', 'id']
        
    '''
    gSheet_idx = row['gSheet_index']
    
    
    #UPDATE ON_BEHALF_OF
    on_behalf_ofP = row.filter(regex=r'^on_behalf_of_')
    on_behalf_ofP.index = [colName.split('on_behalf_of_')[1] for colName in on_behalf_ofP.index]
    on_behalf_ofP['classification'] = "Party"
    on_behalf_ofP['name_en'] = utils.clean(on_behalf_ofP['name_en'])
    on_behalf_of_id = on_behalf_ofP.pop('id')    
     
    if not on_behalf_of_id and on_behalf_ofP['name_en']:
        on_behalf_of_id = searchCLI.searchCLI(base_url, on_behalf_ofP['name_en'], 'organizations', 'name', 'othernames', headers,  [])
    
    on_behalf_of_id = update_allLangs('organizations', on_behalf_of_id, base_url, headers, on_behalf_ofP, sub_langs)


    #UPDATE AREA
    areaP = row.filter(regex=r'^area_')
    areaP.index = [colName.split('area_')[1] for colName in areaP.index]
    areaP["classification"] = 'Parliamentary Constituency'
    areaP['name_en'] = utils.clean(areaP['name_en'])
    area_id = areaP.pop('id')
    
    if not area_id:   #Get ID from area_name or area identifier:
        area_id = searchCLI.searchCLI_naive(base_url, areaP['name_en'], 'areas', 'name')
        
    area_id = update_allLangs('areas', area_id, base_url, headers, areaP, sub_langs)
      
    #UPDATE POST
    postP = row.filter(regex=r'^post_')
    postP.index = [colName.split('post_')[1] for colName in postP.index]
    postP['label_en'] = utils.clean(postP['label_en'])
    post_id = postP.pop('id')
    
    if not post_id and postP['label_en']:
        post_id = searchCLI.searchCLI(base_url, postP['label_en'], 'posts', 'label', 'other_labels', headers, [])
    
    #postP['organization_id'] = orgID
    postP['area_id'] = area_id
    post_id = update_allLangs('posts', post_id, base_url, headers, postP, sub_langs)
        
    #UPDATE PERSON
    personP = row.filter(regex=r'^person_')
    personP.index = [colName.split('person_')[1] for colName in personP.index]
    person_id = personP['id']
    
    if not person_id:
        person_id = searchCLI.searchCLI(base_url, personP['name_en'], 'persons', 'name', 'othernames', headers, ['birth_date', 'national_identity'])
    
    person_id = update_allLangs('persons', person_id, base_url, headers, personP, sub_langs)
         
    #UPDATE MEMBERSHIP
    memP = {
    'on_behalf_of_id': on_behalf_of_id,
    'post_id': post_id,
    'person_id': person_id,   
    'organization_id': orgID,
    'start_date': utils.datetimeParser(row['start_date']),
    'end_date': utils.datetimeParser(row['end_date']),
     }
    url = base_url+ "/en/memberships/"
    memP = dict((k,v) for k,v in memP.items() if v) #remove keys with null vals
    membership_id = row['membership_id']    
    if membership_id:    #Update
        url = url+ membership_id    
        r = requests.put(url, headers=headers, json= memP)
    else:
        r = requests.post(url, headers=headers, json=memP)
        try:
            membership_id = r.json()['result']['id']
        except KeyError:
            print(r.json())
            

    
    
    #update GSheet with newly updated/obtained IDs
    try:
        memP.pop('organization_id')
    except KeyError: #org_id was null
        pass

    col_AI_map = gSheet_details['col_AI_map']
    sheetID = gSheet_details['sheetID']
    sheetName = gSheet_details['sheetName']
    
    gSheet_utils.updateGSheetCell(membership_id, sheetID, sheetName, col_AI_map['membership_id'], gSheet_idx)
    gSheet_utils.updateGSheetCell(area_id, sheetID, sheetName, col_AI_map['area_id'], gSheet_idx)

    for k,v in memP.items():
        gSheet_utils.updateGSheetCell(v, sheetID, sheetName, col_AI_map[k], gSheet_idx)
        
    print("{} Done".format(gSheet_idx))
    
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
