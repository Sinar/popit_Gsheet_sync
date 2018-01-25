
# Popit-Gsheet Sync
Popit-Gsheet syncs data from Google sheets to the Popit database.


## Installation
Clone/download this project.

### Google Sheets API setup
To use the sync script, the user must setup the Google Sheets API. 
1. Follow Step 1 of this [guide](https://developers.google.com/sheets/api/quickstart/python) to enable the Google Sheets API.
2. Move the _client_secret.json_ file  into the oAuth directory in the Popit-Gsheet project directory.
3. Follow step 2 of the guide and install the Google client library
4. Move _sheets.googleapis.com-python-quickstart.json_ to the oAuth directory.
5. Replace the token txt file(s) in the oAuth directory with the relevant Popit API tokens from Sinar.


## Templates
The columns in the data template correspond to fields belonging to entities in Popit (refer to the [Popit API docs](https://api.popit.sinarproject.org/docs)), which Popit-Gsheet Sync updates/posts to the database. Data templates for Popit entities are stored in the templates folder.

The column names should remain unchanged, unless otherwise specified. The order of the columns does not matter, and can be reordered or hidden from view if convenient.

###  Language codes

The template allows for multiple languages to be specified for a field entry. For example:

| org_name_en  |org_name_sl |org_id |
|-------------- |-----------|----------|

Where sl is a placeholder for a corresponding Popit language code (refer to your Popit DB for supported languages). We can replace that with Malay, as below.

| org_name_en               |org_name_ms  |org_id                  |
|-------------------------- |-------------|------------------------|
| House of Representatives  |Dewan Rakyat |53633b5a19ee29270d8a9ecf|


If more sub-languages are necessary, you can add additional columns for each in the template.

| org_name_en               |org_name_ms  |org_name_cn |org_id                  |
|-------------------------- |-------------|-------------|------------------------|
| House of Representatives  |Dewan Rakyat |众议院       |53633b5a19ee29270d8a9ecf|

The sublang columns can be removed if there is no need for alternate languages.


### Unnecessary columns. 
If certain fields are found to be unnecessary for your data, eg. you find that you have no use for the area_identifier field, it is perfectly acceptable to leave the column blank. Do not delete the column from the template.

### Additional unsupported columns
Additional columns that are not supported fields in the Popit database can be added to the sheet for personal reference; they will not be posted to the database.

| person_id |birth_date  |death_date |gender       | source_url                                             |
|---------- |------------|-----------|-------------|----------------------------|
| 42        | 1/1/1970   |           | Female      | https://en.wikipedia.org/wiki/Wikipedia:Citation_needed|

source_url is not a supported field in Popit, thus will not be posted to the database, but can be kept in the sheet without affecting the sync script.

### Contacts and links.
If more contacts or links subtypes are necessary, additional columns can be made following a format.
For each subtype added, two new columns must be created:

| contact_subtype           | contact_subtype_id  |
|-------------------------- |---------------------|

Likewise for links:

| link_subtype             | link_subtype_id     |
|--------------------------|---------------------|

## Usage
### Running Popit-Gsheet sync 

To sync between Google Sheet and Popit DB, run gSheet_sync.py in the console with the chosen parameters.

### Update Popit DB with changes from spreadsheet
	 gSheet_sync.py [-h]  updateBase updateType spreadsheetId  spreadsheetId_control sheetName

positional arguments:

|updateBase|            mm for OpenHluttaw, my for Sinar|
|--------------|-------------------------------------------------|
|updateType|            person or membership|
|spreadsheetId|         ID of Google spreadsheet  (https://docs.google.com/spreadsheets/d/copy_the_ID_here)
|spreadsheetId_control| ID of control Google spreadsheet to generate list of changes from last update (lastUpdated directory on Drive)|
|sheetName |            Name of sheet in Google spreadsheet to update|

### First sync
Taking the example of syncing a spreadsheet using the persons template,

	gsheet_sync.py person 1CACj8dRV5AjyuQ2Fta M21ls7WgFXZULef5cOrpYF0K8 MP_persons

During the first sync, no lastUpdate sheet has been created yet, due to the lack of prior updates. 
Pass in the sheetID to a new empty sheet created in your desired directory for the spreadsheetID_control parameter. This will sync the data from the spreadsheetId sheet, and copy the contents of the fully synced sheet over to the lastUpdate sheet, as a record of the state of the most recent update.

### Subsequent syncs
When subsequent changes have been made to the original spreadsheet, which we'd like to sync to the Popit database, we run the same line of code:
		
	gsheet_sync.py person 1CACj8dRV5AjyuQ2Fta M21ls7WgFXZULef5cOrpYF0K8 MP_persons

As opposed to a regular update, which runs through every row in the sheet to sync the data, passing in a lastUpdate sheetID will compare the current sheet to our lastUpdate sheet for any changes or additions, and will update only those modifications to the Popit database. 

