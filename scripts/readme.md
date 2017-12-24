To import from Google Sheet to Popit DB, run python gSheet_sync.py in the console with the chosen parameters.

### Update Popit DB with changes from spreadsheet
usage: gSheet_sync.py [-h]
                      updateBase updateType spreadsheetId
                      spreadsheetId_control sheetName



positional arguments:

	updateBase            my for OpenHluttaw, ms for Sinar
	updateType            person or membership
	spreadsheetId         ID of Google spreadsheet
	spreadsheetId_control ID of control Google spreadsheet to generate list of changes from last update (lastUpdated directory on Drive)
	sheetName             Name of sheet in Google spreadsheet to update

