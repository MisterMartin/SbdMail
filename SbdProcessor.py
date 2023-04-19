'''
An interface for fetching Iridium SBD emails containing LASP specific attachments

The attachments are decoded and avaiable as a dictionary.

Each email attachment is saved in a file in its base64 representation.

The attachment is decoded according to the LASP structure. It is
printed as text, or as json.

A time range can be specified. ***Note that for the most recent
messages, the end time should be 1 day later than expected.***

This class is very specific to the structure of the Iridium generated
SBD emails. They are MIME encoded, with one base64 attachment. For some
reason, the message parts all have a content type of 'multipart', and
we simply pull the attachment out of the first part which has one.

The code will almost certainly not work with emails that don't follow this
structure.

This works only with an IMAP server. The IMAP protocol is somewhat arcane,
but the imaplib and email modules take most of the pain out of it.
See RFC 2060 (Section 6.4.4) for documentation on the IMAP search query syntax
https://datatracker.ietf.org/doc/html/rfc2060.html

***Note that gmail (and probably all other imap servers) will not let you
attach with your normal credentials. You must obtain an application password
from Gmail. Google "gmail application password" for instructions.*** 

'''

import imaplib
from datetime import datetime
import email
import base64
import os
import struct
import json
import time
from LaspSBD import LaspSBD

class SbdProcessor:
    VERBOSE = False

    def __init__(self, args:dict)->None:
        """SbdProcessor constructor.

        Parameters
        ----------
        args is a dictionary which must contain the following configuration elements:
            args['imap']: str, the email imap server URL.
            args['account']: str, the email account on the server.
            args['password']: str: the email account password or applocation key.
            args['subject']: str: the imap email subject to search for.
            args['begin']: str: Begin date (dd-mm-yyyy).
            args['end']: str: End date (dd-mm-yyyy)
            args['keep']: str: The directory to save the message files to.
            args['json']: bool: If true, print JSON rather than human format.
            args['repeat']: int: Number of seconds to wait and repeat; 0 if none
            args['verbose']: True/False
        """

        self.args = args
        self.VERBOSE = self.args['verbose']
        
        # Connect to the email server.
        self.connect()
        
    def process(self)->None:
        """The main processing loop

        1. Connect to the imap server
        2. Search for message IDs meeting the subject and date criteria
        3. Iterate over the IDs, downloading each message and decoding the 
           SBD attachment.
        4. Sleep/repeat (optional)

        """

        nProcessed = 0
        sbdDecoder = LaspSBD()

        while 1:
            self.connect()
            msg_ids = self.search()
            # Process each message
            msg_ids.reverse()
            for msg_id in msg_ids:
                if self.args['number'] != 0 and nProcessed >= self.args['number']:
                    break;
                msg = self.get_email(msg_id).decode()
                if self.VERBOSE:
                    print(msg)
                m = email.message_from_string(msg)
                dateSent = datetime.strptime( m['date'].strip(), '%d %b %Y %H:%M:%S %z')
                for part in m.walk():
                    if(part.get_content_disposition() == 'attachment'):
                        payload = part.get_payload()
                        payloadBytes = base64.b64decode(payload)
                        if self.VERBOSE:
                            print(payload)

                        # Put the date in first so that it will be at the beginning of the dictionary
                        data = {'dateSent': dateSent.isoformat()}

                        try:
                            # Update dictionary with decoded sbd data dictionary.
                            # If there is an error in the decoding, sbdDecoder will throw ValueError.
                            data.update(sbdDecoder.decode(msg=payloadBytes))

                            # Print the results
                            self.print(data)

                            # Save to a file
                            if (self.args['keep']):
                                filename = part.get_filename()
                                path = os.path.abspath(f'{self.args["keep"]}/{filename}')
                                f = open(path, 'w')
                                f.write(payload)
                                if self.VERBOSE:
                                    print(f'saved to {path}')
                                f.close()
                        except ValueError as e:
                            print(f'Error decoding an attachment: {e}')
                            print(f'Email on {dateSent}')

                        nProcessed += 1

            if self.args['repeat'] == 0:
                self.disconnect()
                break
            else:
                # Disconnect and sleep until the next round
                self.disconnect()
                time.sleep(self.args['repeat'])
                print()
                nProcessed = 0

    def search(self):
        """Query the imap server for messages

        The search terms will be for messages whose subject contain self.args['subject'],
        and were sent within the last self.args['days'].

        Return a list of message ids.
        """

        beginDate = (datetime.strptime(self.args['begin'], '%d-%b-%Y')).strftime("%d-%b-%Y")
        endDate = (datetime.strptime(self.args['end'], '%d-%b-%Y')).strftime("%d-%b-%Y")
        dates = f'(SINCE "{beginDate}" BEFORE "{endDate}")'
        subject = f'(SUBJECT "{self.args["subject"]}")'
        if self.args['verbose']:
            print('imap query:', dates, subject)
        status, data = self.server.search(
            None, 
            dates, 
            subject
            )
        # TODO Check for return status == 'OK'
        mail_ids = data[0].split()
        if self.VERBOSE:
            print(f'Email search returned status:{status}, number of msgs:{len(mail_ids)}, msg ids:{mail_ids}')
        return mail_ids
    
    def get_email(self, mail_id):
        """Fetch the email with the message id: mail_id
        
        It is fetched from the imap server. This can be a tedious
        process on a slow Internet connection.
        """

        if self.VERBOSE:
            print(f'***** fetching message {mail_id}')
        status, data = self.server.fetch(mail_id, '(RFC822)')
        # TODO: Check for status 'ok'
        msg = data[0][1]
        return msg

    def connect(self)->None:
        # this is done to make SSL connection with GMAIL
        self.server = imaplib.IMAP4_SSL(self.args['imap'])
        
        # logging the user in
        self.server.login(self.args['account'], self.args['password'])
        
        # calling function to check for email under this label
        self.server.select('Inbox')

    def disconnect(self)->None:
        """Disconnect from the imap server"""

        self.server.close()
        self.server.logout()

    def print(self, data:dict)->None:
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
        
