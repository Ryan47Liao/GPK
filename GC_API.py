from pprint import pprint
import pickle
import datetime
import os
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from calendar import calendar


def Create_Service(client_secret_file, api_name, api_version,port,*scopes):
    #Author: https://learndataanalysis.org/google-py-file-source-code/
    print(client_secret_file, api_name, api_version, scopes, sep='-')
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]
    print(SCOPES)
    
    cred = None

    pickle_file = f'token_{API_SERVICE_NAME}_{API_VERSION}.pickle'
    # print(pickle_file)
    
    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server(port = port)

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
        print(API_SERVICE_NAME, 'service created successfully')
        return service
    except Exception as e:
        print(e)
        return None


def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt

if __name__ == '__main__':
    Clinet_secrete = "Client_Secrete_OKR.json" #File path of the client secrete 
    API_name = "calendar"
    API_Version = 'v3'
    Scopes = ["https://www.googleapis.com/auth/calendar"]
    port = 8081 
    
    try:
        service = Create_Service(Clinet_secrete,API_name,API_Version,port,Scopes)
    except Exception as e:
        print(e)
        
    print(dir(service))
    print("Executing...")
    #Test:Creating a Calendar 
    response = service.calendarList().list()
    calendar_lists = response.execute()
    pprint(calendar_lists)
    
    #Select one calender with its ID:
    events = service.events().list(calendarId = 'uci.edu_o69ckj6mpase6nc1vbtelfiu8o@group.calendar.google.com').execute()
    for event in events['items']:
        try:
            print(event['summary'])
        except KeyError:
            pass 
        
    ###
    print("DONE")