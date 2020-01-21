import httplib2
import os
import oauth2client
from oauth2client import client, tools, file
import base64
from email import encoders

#needed for attachment
import smtplib  
import mimetypes
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
#List of all mimetype per extension: http://help.dottoro.com/lapuadlp.php  or http://mime.ritey.com/

from apiclient import errors, discovery  #needed for gmail service




## About credentials
# There are 2 types of "credentials": 
#     the one created and downloaded from https://console.developers.google.com/apis/ (let's call it the client_id) 
#     the one that will be created from the downloaded client_id (let's call it credentials, it will be store in C:\Users\user\.credentials)


        #Getting the CLIENT_ID 
            # 1) enable the api you need on https://console.developers.google.com/apis/
            # 2) download the .json file (this is the CLIENT_ID)
            # 3) save the CLIENT_ID in same folder as your script.py 
            # 4) update the CLIENT_SECRET_FILE (in the code below) with the CLIENT_ID filename


        #Optional
        # If you don't change the permission ("scope"): 
            #the CLIENT_ID could be deleted after creating the credential (after the first run)

        # If you need to change the scope:
            # you will need the CLIENT_ID each time to create a new credential that contains the new scope.
            # Set a new credentials_path for the new credential (because it's another file)
def get_credentials():
    # If needed create folder for credential
    home_dir = os.path.expanduser('~') #>> C:\Users\Me
    credential_dir = os.path.join(home_dir, 'farcryServer/.credentials') # >>C:\Users\Me\.credentials   (it's a folder)
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)  #create folder if doesnt exist
    credential_path = os.path.join(credential_dir, 'cred send mail.json')

    #Store the credential
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        CLIENT_SECRET_FILE = 'client_secrets.json'
        APPLICATION_NAME = 'API Python'
        #The scope URL for read/write access to a user's calendar data  

        SCOPES = 'https://www.googleapis.com/auth/gmail.send'

        # Create a flow object. (it assists with OAuth 2.0 steps to get user authorization + credentials)
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME

        credentials = tools.run_flow(flow, store)

    return credentials


## Get creds, prepare message and send it
def create_message_and_send(sender, to, subject,  message_text_plain, message_text_html):
    credentials = get_credentials()

    # Create an httplib2.Http object to handle our HTTP requests, and authorize it using credentials.authorize()
    http = httplib2.Http()

    # http is the authorized httplib2.Http() 
    http = credentials.authorize(http)        #or: http = credentials.authorize(httplib2.Http())

    service = discovery.build('gmail', 'v1', http=http)

    # without attachment
    message_without_attachment = create_message_without_attachment(sender, to, subject, message_text_html, message_text_plain)
    send_Message_without_attachement(service, "me", message_without_attachment, message_text_plain)


def create_message_without_attachment (sender, to, subject, message_text_html, message_text_plain):
    #Create message container
    message = MIMEMultipart('alternative') # needed for both plain & HTML (the MIME type is multipart/alternative)
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = to

    #Create the body of the message (a plain-text and an HTML version)
    message.attach(MIMEText(message_text_plain, 'plain'))
    message.attach(MIMEText(message_text_html, 'html'))

    raw_message_no_attachment = base64.urlsafe_b64encode(message.as_bytes())
    raw_message_no_attachment = raw_message_no_attachment.decode()
    body  = {'raw': raw_message_no_attachment}
    return body


def send_Message_without_attachement(service, user_id, body, message_text_plain):
    try:
        message_sent = (service.users().messages().send(userId=user_id, body=body).execute())
        message_id = message_sent['id']
        # print(attached_file)
        print (f'Message sent (without attachment) \n\n Message Id: {message_id}\n\n Message:\n\n {message_text_plain}')
        # return body
    except errors.HttpError as error:
        print (f'An error occurred: {error}')



def send_mail(content, receiver):
    to = receiver
    sender = "khagkhangg@gmail.com"
    subject = "Verify your email for FARCRY ONLINE."
    message_text_html  = content
    message_text_plain = ""
    create_message_and_send(sender, to, subject, message_text_plain, message_text_html)


if __name__ == '__main__':
    send_mail(content)