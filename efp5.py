import json
import os
import re
import sys
import time
import urllib
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError


"""
This simple script looks to extract the amount of capital raised by
Brewdog in the Equity Punk V round, and writes the data to .json
and csv.

The stats are then uploaded to dropbox.
"""

if not os.path.exists('.dropbox-api'):
   raise ValueError('No dropbox-api file')


URL = 'https://www.brewdog.com/equityforpunks'


def extract_data(body):
    sys.stderr.write('Extracting stats...')
    rx_raised = re.compile('^<h3>\\xc2\\xa3([0-9,\.]+)<\/h3>$')
    rx_investors = re.compile('<h3>([0-9,]+)<\/h3>')
    efp5_raised = rx_raised.sub('\g<1>',body[body.index('<span>Raised</span>')+1])
    efp5_investors = rx_investors.sub('\g<1>', body[body.index('<span>Investors</span>')+1])
    
    sys.stderr.write('%s from %s investors\n' % (efp5_raised, efp5_investors))

    return (efp5_raised, efp5_investors)


def download_data(url):
    sys.stderr.write('Fetching stats from %s\n' % (url))
    req=urllib.urlopen(url)
    body=req.read().split()
    return body


def write_local_data(raised, investors):
    sys.stderr.write('Saving data to disk\n')
    if os.path.exists('brewdog-efp5.json'):
	efp5_file = open('brewdog-efp5.json')
	efp5_json = json.loads(efp5_file.read())
	efp5_file.close()
    else:
	efp5_json = []

    efp5_json.append([time.time(), time.ctime(), raised, investors])

    efp5_file = open('brewdog-efp5.json', 'w')
    efp5_file.write(json.dumps(efp5_json))
    efp5_file.close()

    return efp5_json

def convert_json_to_csv(efp5_json):
    sys.stderr.write('Converting to CSV\n')
    if not os.path.exists('brewdog-efp5.csv'):
	efp5_csv = open('brewdog-efp5.csv', 'w')
	for entry in efp5_json:
	    efp5_csv.write('%s,%s,%s,%s\r\n' % (entry[0], entry[1],
						entry[2].replace(',', ''),
						entry[3].replace(',', '')))
	efp5_csv.close()
    else:
	efp5_csv = open('brewdog-efp5.csv', 'a')
	entry = efp5_json[-1]
	efp5_csv.write('%s,%s,%s,%s\r\n' % (entry[0], entry[1],
					    entry[2].replace(',', ''),
					    entry[3].replace(',', '')))

def connect_to_dropbox():
    dropbox_api_file = open('.dropbox-api')
    dropbox_token = dropbox_api_file.readline().rstrip()
    dropbox_api_file.close()

    dbx=dropbox.Dropbox(dropbox_token)
    dbx.users_get_current_account()

    return dbx

def upload_file_to_dropbox(dbx, file_to_upload,
                           dropbox_folder = '/Apps/myapps2',
			   dropbox_subfolder = 'brewdog-efp5'):
    sys.stderr.write('Uploading file to dropbox %s -> %s/%s/%s\n' % (file_to_upload,
								   dropbox_folder,
								   dropbox_subfolder,
								   file_to_upload))
    with open(file_to_upload, 'r') as file_obj:
	dbx.files_upload(file_obj.read(),
			 dropbox_folder + '/' + dropbox_subfolder + '/'  + file_to_upload,
			 mode=WriteMode('overwrite'))

data = download_data(URL)
(efp5_raised, efp5_investors) = extract_data(data)
efp5_json = write_local_data(efp5_raised, efp5_investors)
convert_json_to_csv(efp5_json)
dbx = connect_to_dropbox()
upload_file_to_dropbox(dbx, 'brewdog-efp5.json')
upload_file_to_dropbox(dbx, 'brewdog-efp5.csv')





