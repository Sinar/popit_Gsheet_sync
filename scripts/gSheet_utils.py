#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from __future__ import print_function
import httplib2
import pandas as pd 

from googleapiclient import discovery
import gSheet_credentials


#Gsheet credentials
credentials = gSheet_credentials.get_credentials()
http = credentials.authorize(httplib2.Http())
discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                'version=v4')
service = discovery.build('sheets', 'v4', http=http,
                          discoveryServiceUrl=discoveryUrl)


def importGSheetAsDF(spreadsheetId, sheetName):
    '''
    Imports Google Sheet as DF
    Inputs:
        spreadsheetId: ID of Google spreadsheet to import
        sheetName: Name of sheet to import
        
    Returns:
        df: dataframe of imported Gsheet
        col_AI_map: Dictionary mapping column names to GSheet AI notation
    '''
    #Get header row
    rangeName = sheetName+'!1:1'
    colNames = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName, majorDimension= "ROWS").execute()
    colNames = colNames.get('values', [])[0]
    col_AI_map = colNamesToAInot(colNames)
    #Append placeholder end row to mark end of table as SheetsV4 omits empty trailing rows/columns
    placeholderVals = [['-']*len(colNames)]
    valInput_body={"majorDimension": "ROWS",
     "values": placeholderVals}
    rangeName = sheetName
    writeResult = service.spreadsheets().values().append(spreadsheetId=spreadsheetId, range=rangeName, 
            valueInputOption='RAW', body = valInput_body).execute()   
    
    #Store range of placeholder row to be removed later
    updatedRange = writeResult['updates']['updatedRange']
    
    #Get col data
    tableRange = sheetName+'!A2:{}'.format(indexToAInot(len(colNames)))
    result = service.spreadsheets().values().get(
         spreadsheetId=spreadsheetId, range=tableRange, majorDimension= "COLUMNS").execute()
    colVals = result['values']

    #Remove placeholder end row
    emptyRow = [['']*len(colNames)]
    valInput_body['values'] = emptyRow
    writeResult = service.spreadsheets().values().update(spreadsheetId=spreadsheetId, range=updatedRange, 
            valueInputOption='RAW', body = valInput_body).execute() 
    
    #Create df out of colNames and colVals
    dic = dict((kvPair[0], kvPair[1]) for kvPair in zip(colNames, colVals))
    df = pd.DataFrame.from_dict(dic, orient = 'columns')
    df = df[:-1]
    
    #Gsheet index for ref
    df['gSheet_index'] = df.index+2
    
    return df, col_AI_map


def sheetChanges(spreadsheetId1, spreadsheetId2, sheet1, sheet2, classID):
    '''
    Get df of changed rows between two sheets.
    Inputs:
        spreadsheetId1: ID of Google sheet to update
        sheet1:: Name of sheet to update
        spreadsheetId2: ID of google sheet to compare spreadsheetId1 against
        sheet2: Name of sheet to compare against
        classID: Popit class of spreadsheet for sorting new entries. 'person_id' or 'membership_id'
    Returns:
        df: dataframe of changed rows between both spreadsheets
        col_AI_map: Dictionary mapping column names to GSheet AI notation
    '''
    df_latest, col_AI_map = importGSheetAsDF(spreadsheetId1, sheet1)
    df_control = importGSheetAsDF(spreadsheetId2, sheet2)[0]
    
    #Sort by memID so all new entries are at the top
    df_latest = df_latest.sort_values(by=classID, axis=0)
    df_control = df_control.sort_values(by=classID, axis=0)
    df_control.reset_index(drop=True, inplace=True)
    #Get new entries
    nDiff = len(df_latest)- len(df_control)
    df_added = df_latest[:nDiff]
    #Get updated entries
    df_latest = df_latest[nDiff:]
    df_latest.reset_index(drop=True, inplace=True)
    df_updated=  df_latest[(df_control.drop('gSheet_index', axis=1) != df_latest.drop('gSheet_index', axis=1)).sum(axis = 1) >0]
    
    df_changes = df_updated.append(df_added, ignore_index= True)
    return df_changes, col_AI_map


def updateGSheetCell(cell_updateValue, sheetID, sheetName, col_ind, row_ind):
    '''
    update cell of Google sheet with sheetID and sheetName
    '''
    cell_update = "{}!{}{}".format(sheetName, col_ind, row_ind)
    service.spreadsheets().values().update(spreadsheetId= sheetID, 
                    range= cell_update, 
                    body= {'values':[[cell_updateValue]]}, 
                    valueInputOption='RAW').execute()    
    

def colNamesToAInot(colName_list):
    '''
    return corresponding AI notation for col name from GSheet
    '''
    colName_AI_map = {}
    for i in range(len(colName_list)):
        colName_AI_map[colName_list[i]] = indexToAInot(i+1)
        
    return colName_AI_map

def indexToAInot(col_ind):
    '''
    return corresponding AI notation for col index
    '''
    temp = ""
    letter = ""
    while col_ind > 0:
        temp = (col_ind -1) % 26;
        letter = chr(temp+65) + letter
        col_ind = (col_ind - temp-1) // 26
                          
    return letter