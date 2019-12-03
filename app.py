import io
import os
import csv
from zipfile import ZipFile
from datetime import datetime, timedelta
from dateutil import parser
import pandas as pd

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

if __name__ == "__main__":
    zipfile_path = "{}/zip-folders".format(BASE_DIR)
    output_path = "{}/temp-folders".format(BASE_DIR)
    combined_path = "{}/combined-folders".format(BASE_DIR)
    input_files_path = "{}/input-files".format(BASE_DIR)

    # Create folders if they don't exist
    folder_path_list = [zipfile_path, output_path, combined_path, input_files_path]
    for folder_path in folder_path_list:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


    method = input("Type method: 1: unzip the zipfiles, 2: get output.csv file from input.txt file, 3: search specific data:\n")

    # 1: unzip the zipfiles, 2: get output.csv file from input.txt file
    # 3: search specific data
    run_type = int(method)
    if run_type == 1:
        # Get zipfiles
        extract_all_zipfiles(zipfile_path, output_path)
    elif run_type == 2:
        # Get top directories for year
        top_directories = [ name for name in os.listdir(output_path) if os.path.isdir(os.path.join(output_path, name)) ]

        for top_directory in top_directories:
            top_directory_path = output_path + "/" + top_directory
            combined_file = combined_path + "/" + top_directory + ".csv"

            first_csv = None
            merged = None
            has_initial_csv = False
            is_merged = False
            try:
                # Get all csv_files on one of top directories
                all_filenames = retrieve_file_paths(top_directory_path)
                #combine all files in the list
                combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
                #export to csv
                combined_csv.to_csv( combined_file, index=False, encoding='utf-8-sig')

            except Exception as e:
                print("Error when merging files into one file #{}.".format(top_directory))

    else:
        output = None # output dataframe

        # Get top directories for year
        top_directories = [ name for name in os.listdir(output_path) if os.path.isdir(os.path.join(output_path, name)) ]

        file_path = input_files_path + '/input.csv'
        df = pd.read_csv(file_path)

        for index, row in df.iterrows():
            ev_dt_obj = parser.parse(str(row['EV_DT']))
            ev_date = ev_dt_obj.date
            start_obj = ev_dt_obj - timedelta(days=30)
            end_obj = ev_dt_obj + timedelta(days=30)

            start_time = start_obj.strftime("%Y%m%d")
            end_time = end_obj.strftime("%Y%m%d")
            current_time = ev_dt_obj.strftime("%Y%m%d")

            # year
            year = ev_dt_obj.year

            target_file_path = "{}/{}.csv".format(combined_path, str(year))
            if str(year) in top_directories:
                target = pd.read_csv(target_file_path)

                target['date'] = target['date'].astype(str)
                result = target[(target['cik'] == row['CIK']) & (target['date'] > start_time) & (target['date'] < end_time)]
                output = pd.concat([output, result])

        output.to_csv(input_files_path+'/output.csv',
                        index=False,
                        encoding='utf-8-sig')


                