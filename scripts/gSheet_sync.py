#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys, argparse, requests

parser = argparse.ArgumentParser(description='Update Popit DB with changes from spreadsheet')
   
parser.add_argument('updateBase', help= 'my for OpenHluttaw, ms for Sinar')
parser.add_argument('updateType', help= 'person or membership')
parser.add_argument('spreadsheetId', help='ID of Google spreadsheet')
parser.add_argument('spreadsheetId_control', help='ID of control Google spreadhseet. Required if updateType=change')
parser.add_argument('sheetName', help= 'Name of sheet in Google spreadsheet to update')

    
args, rest = parser.parse_known_args()
#=============================================
#VALIDATE ARGS
#=============================================
if args.updateBase=='ms':
    base_url = "http://api.popit.sinarproject.org"
    token = open('../oAuth/token_ms.txt').read()
    headers = {'Authorization': token.rstrip()}
    sub_langs = ['ms']
elif args.updateBase=='my':
    base_url = "http://api.openhluttaw.org"
    token = open('../oAuth/token_my.txt').read()
    headers = {'Authorization': token.rstrip()}
    sub_langs = ['my']
else:
    print("Invalid Popit base")
        
if args.updateType == 'person':
    classType = 'person'
elif args.updateType=='membership':
   classType = 'membership'
else:
    print("Invalid update type")


if __name__ == '__main__':
    #IMPORT SHEET CHANGES
    sys.argv = ['gSheet_utils']
    import gSheet_utils
    
    #df, col_AI_map = gSheet_utils.sheetChanges(args.spreadsheetId, args.spreadsheetId_control, args.sheetName, args.sheetName, args.updateType+'_id')
    df, col_AI_map = gSheet_utils.importGSheetAsDF(args.spreadsheetId, args.sheetName)
    gSheet_details = {'sheetID':args.spreadsheetId, 'sheetName': args.sheetName, 'col_AI_map': col_AI_map, 'sub_langs':sub_langs}
         
   
    if  classType=='membership':
        sys.argv = ['searchCLI.py']
        import searchCLI
        orgName = ' '.join(args.sheetName.split('memberships_')[1].split('_'))
        orgID = searchCLI.searchCLI(base_url, orgName, 'organizations', 'name', 'othernames')
        
        if not orgID:
            orgP = {'name': orgName}
            url = base_url+ "/en/organizations/"
            r_en = requests.post(url, headers=headers, json=orgP)
            
            if r_en.ok:
                try:
                    orgID = r_en.json()['result']['id']
                except KeyError:
                    orgID = r_en.json()['id']
            else:
                print(orgP)
                print(r_en.content)
        
        sys.argv = ['membershipsUpdate_langs.py']
        import membershipsUpdate_langs  
        df.apply(lambda row: membershipsUpdate_langs.genPayload(base_url, headers, row, orgID, gSheet_details, sub_langs), axis=1)
        
          
    elif classType == 'person':
        sys.argv = ['personsUpdate_langs.py']
        import personsUpdate_langs
        personsUpdate_langs.personsUpdate(df, base_url, headers, gSheet_details)            
        
    else:
        print("Invalid class")

'''
#SYNC ALL SHEETS
sheetNames = getSheetNames(sheetID)
for sheetName in sheetNames:
    orgName = ' '.join(sheetName.split('memberships_')[1].split('_'))
    orgID = searchCLI.searchCLI(base_url, orgName, 'organizations', 'name', 'othernames', [])
    print("Importing for {}".format('orgName'))
    
    if not orgID:
            print("Adding org for {}".format(orgName))
            orgP = {'name': orgName}
            url = base_url+ "/en/organizations/"
            r_en = requests.post(url, headers=headers, json=orgP)
            
            if r_en.ok:
                try:
                    orgID = r_en.json()['result']['id']
                except KeyError:
                    orgID = r_en.json()['id']
            else:
                print(orgP)
                print(r_en.content)
                
    df, col_AI_map = gSheet_utils.importGSheetAsDF(sheetID, sheetName)
    gSheet_details = {'sheetID':sheetID, 'sheetName': sheetName, 'col_AI_map': col_AI_map, 'sub_langs':sub_langs}
    df.apply(lambda row: genPayload(base_url, headers, row, orgID, gSheet_details, sub_langs), axis=1)
    
'''