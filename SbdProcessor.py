import imaplib
import datetime
import email
import base64
import os
import struct
import json
from LaspSBD import LaspSBD

'''

See RFC 2060 (Section 6.4.4) for documentation on the IMAP search query syntax
https://datatracker.ietf.org/doc/html/rfc2060.html

'''

class SbdProcessor:
    VERBOSE = False

    def __init__(self, args:dict)->None:

        self.args = args
        self.VERBOSE = self.args['verbose']

        # this is done to make SSL connection with GMAIL
        self.server = imaplib.IMAP4_SSL(self.args['imap'])
        
        # logging the user in
        self.server.login(args['account'], args['password'])
        
        # calling function to check for email under this label
        self.server.select('Inbox')
        
    def process(self)->None:
        sbdDecoder = LaspSBD()
        msg_ids = self.search()
        print(type(msg_ids))
        # Process from newer to older
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
                    if self.args['json']:
                        print(f'{json.dumps(data)}')
                    else:
                        print(f'{msg_id.decode()}: {data}')
                    if (self.args['keep']):
                        filename = part.get_filename()
                        path = os.path.abspath(f'{self.args["keep"]}/{filename}')
                        f = open(path, 'w')
                        f.write(payload)
                        if self.VERBOSE:
                            print(f'saved to {path}')
                        f.close()
    # Function to get email content part i.e its body part
    def get_body(self, msg):
        if msg.is_multipart():
            return get_body(msg.get_payload(0))
        else:
            return msg.get_payload(None, True)
    
    def search(self):
        date = (datetime.date.today() - datetime.timedelta(int(self.args['days']))).strftime("%d-%b-%Y")
        status, data = self.server.search(
            None, 
            f'(SENTSINCE "{date}")', 
            f'(SUBJECT "{self.args["subject"]}")'
            )
    # Check for return status == 'OK'
        mail_ids = data[0].split()
        if self.VERBOSE:
            print(f'Email search returned status:{status}, number of msgs:{len(mail_ids)}, msg ids:{mail_ids}')
        return mail_ids
    
    # Function to get the list of emails under this label
    def get_email(self, mail_id):
        if self.VERBOSE:
            print(f'***** fetching message {mail_id}')
        status, data = self.server.fetch(mail_id, '(RFC822)')
        # check for status 'ok'
        msg = data[0][1]
        return msg

