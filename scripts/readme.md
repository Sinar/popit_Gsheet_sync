To import, run python gSheet_sync.py in the console with the chosen parameters.


usage: gSheet_sync.py [-h]
                      updateBase updateType spreadsheetId
                      spreadsheetId_control sheetName

Update Popit DB with changes from spreadsheet

positional arguments:
  updateBase            mm for OpenHluttaw, my for Sinar
  updateType            person or membership
  spreadsheetId         ID of Google spreadsheet
  spreadsheetId_control	ID of control Google spreadsheet to generate list of changes from last update (lastUpdated directory on Drive)
  sheetName             Name of sheet in Google spreadsheet to update

