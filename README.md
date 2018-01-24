# Popit-Gsheet Sync
Popit-Gsheet syncs data from Google sheets to the Popit database.


## Installation
1. Google Sheets API setup
2. Git clone


## Configuration
Config file.



## Templates
The columns in the data template correspond to fields belonging to entities in Popit (refer to the [Popit API docs](https://api.popit.sinarproject.org/docs)), which Popit-Gsheet Sync updates/posts to the database. Data templates for Popit entities are stored in the templates folder.

The column names should remain unchanged, unless otherwise specified. The order of the columns does not matter, and can be reordered or hidden from view if convenient.

### Modifying the templates
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

Additionally, ensure that these language codes are specified in the config file.


You can remove the sublang columns if you have no use for alternate languages.


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
|spreadsheetId|         ID of Google spreadsheet|
|spreadsheetId_control| ID of control Google spreadsheet to generate list of changes from last update (lastUpdated directory on Drive)|
|sheetName |            Name of sheet in Google spreadsheet to update|
### First sync

First sync.

This will:
1. Update the Popit DB with the new data.
2. 

Option: lastupdate diff
1. First sync: Pass in an empty sheetID created in your desired directory for the last_update parameter.
This will do the same as a regular update, but also create a sheet sheetID which is a duplicate of your current sheet, representing the state of the most recent update.

As opposed to a regular update, which runs through every row in the sheet to sync the data, passing in a lastUpdate sheetID will compare the current sheet to the previous sheet for any changes or additions, and updates only those modifications. This is handy for saving time and bandwidth.


# Usage
Provide a short code snippet (if applicable), or short usage instructions


