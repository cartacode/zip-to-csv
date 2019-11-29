from __future__ import print_function
# import pickle
# import os.path
# from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request

from googleapiclient import discovery
from googleapiclient.http import MediaIoBaseDownload
from httplib2 import Http
from oauth2client import file, client, tools

import io
import os
import csv
from zipfile import ZipFile
import pandas as pd
from google_drive_downloader import GoogleDriveDownloader as gdd

import pdb

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Declare the function to return all file paths of the particular directory
def retrieve_file_paths(dirName):
 
    # setup file paths variable
    filePaths = []

    # Read all directory, subdirectories and file lists
    for root, directories, files in os.walk(dirName):
        for filename in files:
            # Create the full filepath by using os module.
            filePath = os.path.join(root, filename)
            filePaths.append(filePath)
         
    # return all paths
    return filePaths

def zip_directory(dir_name , zipfile_name):  
    # Call the function to retrieve all files and folders of the assigned directory
    filePaths = retrieve_file_paths(dir_name)

    # printing the list of all files to be zipped
    print("The following list of files will be zipped:")
    for fileName in filePaths:
        print(fileName)
         
    # writing files to a zipfile
    zip_file = ZipFile(zipfile_name+".zip", "w", zipfile.ZIP_DEFLATED)
    with zip_file:
        # writing each file one by one
        for file in filePaths:
            file_path = os.path.relpath(file, os.path.join(dir_name, ".."))
            zip_file.write(file_path)


def unzip(zipfile_path, output_path, members=None, pwd=None):
    with ZipFile(zipfile_path, "r") as zip_obj:
        # Extract all the contents of zip file in different directory
        zip_obj.extractall(output_path)
        zip_obj.close()

def extract_all_zipfiles(zipfile_path, output_path):
    files = retrieve_file_paths(zipfile_path)
    for file in files:
        if file[-4:] == ".zip":
            file_path = file
            unzip(file_path, output_path);


def listFiles(service):

    listOfFiles = []
    page_token = None
    q = "mimeType='image/jpeg'"

    #Get list of jpg files in Drive of authenticated user
    while True:
        response = service.files().list(spaces = "drive", fields = "nextPageToken, files(id, name)", pageToken = page_token, driveId='0B4niqV00F3msQWg4MXZpSnl3Z28', corpora='drive', includeItemsFromAllDrives=True, supportsAllDrives=True).execute()
        for file in response.get('files', []):
            listOfFiles.append(file)

        print(listOfFiles)
        page_token = response.get('nextPageToken', None)

        if page_token is None:
            break

if __name__ == "__main__":
    zipfile_path = "{}/zip-folders".format(BASE_DIR)
    output_path = "{}/temp-folders".format(BASE_DIR)
    combined_path = "{}/combined-folders".format(BASE_DIR)

    run_type = 1 # 1: unzip the zipfiles, 2: get output.csv file from input.txt file
    if run_type == 1:
        # file_id = '0B4niqV00F3msQWg4MXZpSnl3Z28'
        # # file_id = '0B4niqV00F3msdzFlZHZESnhSb2c'
        # destination = zipfile_path
        # gdd.download_file_from_google_drive(file_id=file_id,
        #                             dest_path=zipfile_path + '/mnist.zip',
        #                             unzip=True)

        SCOPES = 'https://www.googleapis.com/auth/drive'
        store = file.Storage('storage.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)
        service = discovery.build('drive', 'v3', http=creds.authorize(Http()))

        # folder_id = '1UQmAkOtmsdKHyqwvw0VXvrFZByJDisI8'
        folder_id = '0B4niqV00F3msQWg4MXZpSnl3Z28'
        # results = service.files().list(q="name = '"+folder_id+"' and trashed = false",fields="nextPageToken, files(name, shared)").execute()
        
        results = service.files().list(
                    q="mimeType='application/vnd.google-apps.folder'",
                    pageSize=1000,
                    fields="nextPageToken, files(name, shared)").execute()
        token = results.get('nextPageToken', None)
        items = results.get('files', [])

        for item in items:
            print(item)
        #     response = DRIVE.files().get_media(fileId=item['id'])
        #     fh = io.FileIO(item['name'], 'wb')
        #     downloader = MediaIoBaseDownload(fh, response)
        # done = False
        # while done is False:
        #     status, done = downloader.next_chunk()
        #     print("Downloading..." + str(fileID['name']))