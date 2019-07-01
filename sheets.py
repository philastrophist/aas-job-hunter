from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import pandas as pd
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os

HERE = os.path.dirname(os.path.abspath(__file__))

try:
    with open(os.path.join(HERE, 'sheetID'), 'r') as f:
        SPREADSHEET_ID = f.read()
except (IOError, FileNotFoundError):
    SPREADSHEET_ID = os.environ['SPREADSHEET_ID']
SHEET_NAME = 'AAS'
RANGE_NAME = SHEET_NAME+'!A1:ZZ'




# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
# SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
# RANGE_NAME = 'Class Data!A2:E'

def login():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    # Call the Sheets API
    sheet = service.spreadsheets()
    return sheet

def read_gvalues(sheet):
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    return result


def write_gvalues(sheet, gvalues):
    sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME, body=gvalues, valueInputOption='USER_ENTERED').execute()

def gvalues2df(gvalues):
    values = gvalues.get('values', [[]])
    return pd.DataFrame(values[1:], columns=values[0])

def df2gvalues(df):
    dtypes = df.dtypes
    df = df.applymap(str)
    vs = [df.columns.tolist()]
    vs += df.values.tolist()
    return {'majorDimension': 'ROWS',
               'range': RANGE_NAME,
               'values': vs}

def read(sheet):
    gvalues = read_gvalues(sheet)
    return gvalues2df(gvalues)

def write(sheet, df):
    gvalues = df2gvalues(df)
    write_gvalues(sheet, gvalues)

if __name__ == '__main__':
    sheet = login()
    gvalues = read_gvalues(sheet)
    df = gvalues2df(gvalues)
    print(df)
    gvalues = df2gvalues(df)
    write_gvalues(sheet, gvalues)