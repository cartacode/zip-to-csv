from __future__ import print_function

from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools

import io
import os
import csv
from zipfile import ZipFile
import pandas as pd
from google_drive_downloader import GoogleDriveDownloader as gdd
import gdown

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    zipfile_path = "{}/zip-folders".format(BASE_DIR)
    output_path = "{}/temp-folders".format(BASE_DIR)
    combined_path = "{}/combined-folders".format(BASE_DIR)

    run_type = 1 # 1: unzip the zipfiles, 2: get output.csv file from input.txt file
    if run_type == 1:
        SCOPES = 'https://www.googleapis.com/auth/drive'
        store = file.Storage('storage.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)
        service = discovery.build('drive', 'v3', http=creds.authorize(Http()))

        res = service.files().list(q="'%s' in parents" % folder_id).execute()
        items = [{'id': f['id'], 'name': f['name']} for f in res['files']]

        for item in items:
            gdd.download_file_from_google_drive(file_id=item['id'],
                                        dest_path='{}/{}'.format(zipfile_path, item['name']),
                                        unzip=False)

        