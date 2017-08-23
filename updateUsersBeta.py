# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 16:47:31 2017

@author: Titi
"""

from __future__ import print_function
import httplib2
import os
import psycopg2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def retreive_users():
    """Retreive users from a spreadsheet

    Finds them at the address :
    https://docs.google.com/spreadsheets/d/1Vc5SufRGZVo0OVhrp_hsPt67UfQbdrkH_mRCcWksHs8/edit#gid=0

    TO BE IMPROVED : the range of the selected data should depend on the number of fields
    """
    print("Retrieving data... ", end="")
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1Vc5SufRGZVo0OVhrp_hsPt67UfQbdrkH_mRCcWksHs8'

    rangeName = 'A1:U5200' # TO BE IMPROVED

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    data = result.get('values', [])

    if not data:
        print("ERROR : No data found.")
    else:
        print("done.\n")
        return data


def generate_update_instruction(data, table, fields, header):
    if (header) :
        start = 1
    else :
        start = 0

    instruction = ""

    for row in data[start:] :

        fieldNumber = 0
        instructionRow = "UPDATE " + table + " SET "

        if len(row) > len(fields) :
            row = row[:len(fields)] # Erases the unused data. Requests that data is ordered the same way as the fields.

        while len(row) < len(fields) :
            row.append("undefined")

        for cell in row :
            if (fields[fieldNumber] != "mail") :
                cell = cell.replace('"', '')

                if (cell == "") :
                    cell = "undefined"

                instructionRow += fields[fieldNumber] + ' = "' + cell + '", '

            else :
                mail = cell

            fieldNumber += 1

        instructionRow = instructionRow[:-2] + ' WHERE mail = "' + mail + '";\n'
        instructionRow = instructionRow.replace('undefined', 'null')

        instruction += instructionRow

    instruction = instruction.replace('""', '"null"')
    instruction = instruction.replace("'", "/")
    instruction = instruction.replace('"', "'")
    instruction = instruction + "\n"

    instruction = instruction.encode("UTF-8")

    print("done.\nGenerated Update instruction : \n" + instruction[:350] + "...")
    showMore = (raw_input("/To show the complete instruction please press s/  ") == 's')

    if (showMore) :
        print(instruction)

    return instruction

def generate_insert_instruction(data, table, fields, header):
    instruction = "INSERT INTO " + table + " ("
    for i in range (len(fields)) :
        instruction += fields[i] + ", "

    instruction = instruction[:-2] + ") VALUES\n"

    if (header) :
        start = 1
    else :
        start = 0


    for row in data[start:] :

        if len(row) > len(fields) :
            row = row[:len(fields)] # Erases the unused data. Requests that data is ordered the same way as the fields.

        while len(row) < len(fields) :
            row.append("undefined")

        instruction += "("

        for cell in row :
            cell = cell.replace('"', '')

            if (cell == "") :
                cell = "undefined"

            instruction += '"' + cell + '", '

        instruction = instruction[:-2] + "),\n"
        instruction = instruction.replace('undefined', 'null')

    instruction = instruction.replace('""', '"null"')
    instruction = instruction.replace("'", "/")
    instruction = instruction.replace('"', "'")
    instruction = instruction[:-2] + "\n"
    instruction += "ON CONFLICT (mail) DO NOTHING;" # Makes sure there won't be trouble, but not efficient. TO BE IMROVED.


    instruction = instruction.encode("UTF-8")

    print("done.\nGenerated instruction : \n" + instruction[:350] + "...")
    showMore = (raw_input("/To show the complete instruction please press s/  ") == 's')

    if (showMore) :
        print(instruction)

    return instruction

def direct_update (data,
                   table = "collaborateur",
                   fields = ("prenom", "nom", "mail", "mobile", "structure_juridique", "description", "titre", "departement", "domaine", "est_admin", "mail_responsable", "organisation_path", "metier", "structure_juridique_path", "etablissement_path", "sous_structure", "etablissement_digital", "structure_juridique_digitale", "organisation_unit", "activites", "fonctions_digitales"), 
                   header = True) :
    '''
        Updates the doctocare-database with new data.

        Taking data in the form : [row1 : [attribute1, attribute2, ...], row2 : [attribute1, attribute2, ...]], updates directly the database using the psycopg2 package.

        TO BE IMPROVED : For now, the datastructure is pretty rigid. Can be improved by working on a dictinnary-like way to store data.
    '''

    # Connect to the database using the psycopg2 package #
    print("Connecting to database... ", end="")
    conn = psycopg2.connect(user='postgres', password='doctocare2049',
                            host='130.211.54.253', port='5432')

    curr = conn.cursor()
    print("done.\n")
    # Generate the postgreSQL instructions from the data provided #
    print("Generating Update instruction... ", end="")
    update_instruction = generate_update_instruction(data, table, fields, header)

    print("Generating instruction... ", end="")
    insert_instruction = generate_insert_instruction(data, table, fields, header)

    instruction = update_instruction + insert_instruction
    # Update the data directly in the database #
    try :
        curr.execute(instruction)
    except psycopg2.Error as e :
        print(e.pgerror)

    # Confirm the instruction #
    confirm = raw_input("Are you sure you want to commit this instruction ? /y or n/  ")
    if (confirm == "y") :
        conn.commit()
        print("Database updated !")
    else :
        print("Aborted")

    # Close connection #
    curr.close()
    conn.close()

if __name__ == '__main__':
    data = retreive_users()
    direct_update(data)
