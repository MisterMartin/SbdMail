import imaplib
import datetime
import email
import base64
import os
import struct
import json
from LaspSBD import LaspSBD

'''
An interface for fetching Iridium SBD messages with LASP specific attachments

The attachments are decoded and avaiable as a dictionary.

Each email attachment is saved as a file.

This class is very specific to the structure of the Iridium generated
SBD emails. They are MIME encoded, with one base64 attachment. For some
reason, the message parts all have a content type of 'multipart', and
we simply pull the attachment out of the first part which has one.

The code will almost certainly not work with emails that don't follow this
structure.

See RFC 2060 (Section 6.4.4) for documentation on the IMAP search query syntax
https://datatracker.ietf.org/doc/html/rfc2060.html

'''

class SbdProcessor:
    VERBOSE = False

    def __init__(self, args:dict)->None:
        '''SbdProcessor constructor.

        args is a dictionary which must contain the following elements:
            args['imap']: str, the email imap server URL.
            args['account']: str, the email account on the server.
            args['password']: str: the email account password or applocation key.
            args['subject']: str: the imap email subject to search for.
            args['days']: str: An integer (string), the number of days to look back on the imap server.
            args['keep']: str: The directory to save the message files to.
            args['json']: bool: If true, print JSON rather than human format.
            args['verbose']: True/False
        '''

        self.args = args
        self.VERBOSE = self.args['verbose']

        # this is done to make SSL connection with GMAIL
        self.server = imaplib.IMAP4_SSL(self.args['imap'])
        
        # logging the user in
        self.server.login(args['account'], args['password'])
        
        # calling function to check for email under this label
        self.server.select('Inbox')
        
    def display(self, data:dict)->None:
        '''Print the parsed message'''
        if self.args['json']:
            print(json.dumps(data))
        else:
            print(
                f"{data['dateSent']} ",
                f"Iridium GPS Lat:{data['iridium']['lat']:.4f}",
                f"Lon: {data['iridium']['lon']:.4f}",
                f"Alt: {data['iridium']['alt']:d}",
                f"iMet GPS Lat:{data['imet']['lat']:.4f}",
                f"Lon: {data['imet']['lon']:.4f}",
                f"Iridium IntT: {data['iridium']['intT']:.1f}",
                f"Iridium batV: {data['iridium']['batV']:.1f}",
                f"Iridium frame: {data['iridium']['frame']:.0f}"
        )
        
    def process(self)->None:
        sbdDecoder = LaspSBD()
        msg_ids = self.search()

        # Process each message
        for msg_id in msg_ids:
            msg = self.get_email(msg_id).decode()
            if self.VERBOSE:
                print(msg)
            m = email.message_from_string(msg)
            dateSent = datetime.datetime.strptime( m['date'].strip(), '%d %b %Y %H:%M:%S %z')
            for part in m.walk():
                if(part.get_content_disposition() == 'attachment'):
                    payload = part.get_payload()
                    payloadBytes = base64.b64decode(payload)
                    if self.VERBOSE:
                        print(payload)

                    # Put the date in first so that it will be at the beginning of the dictionary
                    data = {'dateSent': dateSent.isoformat()}
                    data.update(sbdDecoder.decode(msg=payloadBytes))

                    self.display(data)

                    if (self.args['keep']):
                        filename = part.get_filename()
                        path = os.path.abspath(f'{self.args["keep"]}/{filename}')
                        f = open(path, 'w')
                        f.write(payload)
                        if self.VERBOSE:
                            print(f'saved to {path}')
                        f.close()
    
    def search(self):
        '''Query the imap server for messages

        The search terms will be for messages whose subject contain self.args['subject'],
        and were sent within the last self.args['days'].

        Return a list of message ids.
        '''
        date = (datetime.date.today() - datetime.timedelta(int(self.args['days']))).strftime("%d-%b-%Y")
        status, data = self.server.search(
            None, 
            f'(SENTSINCE "{date}")', 
            f'(SUBJECT "{self.args["subject"]}")'
            )
        # TODO Check for return status == 'OK'
        mail_ids = data[0].split()
        if self.VERBOSE:
            print(f'Email search returned status:{status}, number of msgs:{len(mail_ids)}, msg ids:{mail_ids}')
        return mail_ids
    
    def get_email(self, mail_id):
        '''Fetch the email with the message id: mail_id
        
        It is fetched from the imap server. This can be a tedious
        process on a slow Internet connection.
        '''

        if self.VERBOSE:
            print(f'***** fetching message {mail_id}')
        status, data = self.server.fetch(mail_id, '(RFC822)')
        # TODO: Check for status 'ok'
        msg = data[0][1]
        return msg

