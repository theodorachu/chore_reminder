# using sheets
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import sendgrid
import os
from sendgrid.helpers.mail import *

#datetime
import datetime
now = datetime.datetime.now()

# variables
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SPREADSHEET_ID = '157HR8D8jJCmZldtQL78wfsM58O_2kIEUusM1KZXm7bw'
RANGE_NAME = 'Chores!A4:C50'

def main():
	creds = None
	if os.path.exists('token.pickle'):
		with open('token.pickle', 'rb') as token:
			creds = pickle.load(token)
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
			creds = flow.run_local_server()
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)
	service = build('sheets', 'v4', credentials=creds)

	sheet = service.spreadsheets()
	result = sheet.values().get(spreadsheetId = SPREADSHEET_ID, range = RANGE_NAME).execute()
	values = result.get('values', [])
	
	if not values:
		print('No data found.')
	else:
		for row in values: #Date, task, person
			date = row[0]
			today = now.strftime("%d/%m/%Y")
			if date == today:
				# this week
				sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
				from_email = Email("chores@2202bryant.com")
				to_email = Email(row[2])
				subject = "It's your chore week!"
				
				body = "Your chore for the week is %s." %(row[1])
				if row[1] == 'kitchen':
					body += "\n Your tasks are: clean whatever is in the sink (or get the one responsible to do it), sanitize counter + table, clean fridge shelves & throw out old things, swiffer floor, take out all recycling & trash, and beat/sanitize the sink rug."
				if row[1] == 'floors+bath':
					body += "\n Your tasks are: sweep/vacuum + swiffer main hallway, sanitize bathroom sink & toilets, sanitize bathroom mat with disinfectant spray, sanitize bath tub, swiffer bathroom floors, take out bathroom trash."

				content = Content("text/plain", body)
				mail = Mail(from_email, subject, to_email, content)
				response = sg.client.mail.send.post(request_body=mail.get())

if __name__ == '__main__':
	main()


