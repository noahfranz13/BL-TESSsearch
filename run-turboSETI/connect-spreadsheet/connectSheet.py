# Imports
import pandas as pd
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def getSheet():
    '''
    gains access to the necessary google spreadsheet

    returns google spreadsheet client
    '''

    # Gain access to the google sheets and read in table with pandas
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    jsonfile = os.path.join(os.getcwd(), 'client_info.json')
    credentials = ServiceAccountCredentials.from_json_keyfile_name(jsonfile, scope)
    client = gspread.authorize(credentials)

    # Real path to spreadsheet
    ss = client.open('franz-turboSETI-input-file-info').sheet1
    # Uncomment below to test
    #ss = client.open('backup-franz-turboSETI-input-file-info').sheet1

    return ss


def readSheet():
    '''
    Reads in information from google sheets file-info table
    Necessary headers and example table here:
    https://docs.google.com/spreadsheets/d/1Jny2OhsXjr23HhlN_e5bJ-WITwP2HSFZJIBWg3Dpr_Y/edit?usp=sharing

    returns : pandas table for input into turboSETI wrapper
    '''

    # Read in info from spreadsheet
    ss = getSheet()
    ssdata = ss.get_all_records()
    fileinfo = pd.DataFrame.from_dict(ssdata)

    return fileinfo

def writeSheet(row, column=9, msg='TRUE'):
    '''
    Updates google spreadsheet according to new changes

    row [int]    : row index that needs to be updated, count starts at 1
    column [int] : column index that needs to be updated, defaulted to 9,
                   count starts at 1
    msg [string] : Message to put in cell, defaulted to TRUE

    returns      : nothing, just updates the google sheet
    '''

    ss = getSheet()
    ss.update_cell(row, column, msg)
