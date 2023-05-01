# SbdMail

Download Iridium SBD emails and decode the LASP specific attachments. 

The attachments will be printed either as human text or json. The downloaded
attachments may be saved as files.

A configuration file is written in `~/.config/SbdMail/SbdMail.ini`

## Installation 

You can download this repository and work from there. But better yet, you can 
use pip to install it and then run the module:

```
pip3 install git+https://github.com/MisterMartin/SbdMail
    
python3 -m SbdMail -h

usage: __main__.py [-h] [-a ACCOUNT] [-p PASSWORD] [-t SUBJECT] [-b BEGIN] [-e END] [-i IMAP] [-n NUMBER] [-k KEEP] [-j] [-r REPEAT] [-c] [-v]

Fetch recent Iridium email messages and decode them as text or json.
If --keep is specified, the message attachments will be saved:
python3 sbdmail.py -b 9-apr-2023 11-apr-2023 -n 1

Arguments not specified on the command line are taken from
/Users/charlie/.config/SbdMail/SbdMail.ini.

Run the program once to create the initial .ini file, (it will give errors),
and then edit /Users/charlie/.config/SbdMail/SbdMail.ini

** Be careful of sharing this file, if account/password details are specified there.**

** You may need to specify an end date one day in the future to retreive very recent messages. **

options:
  -h, --help            show this help message and exit

required arguments:
  -a ACCOUNT, --account ACCOUNT
                        email account
  -p PASSWORD, --password PASSWORD
                        mailbox password
  -t SUBJECT, --subject SUBJECT
                        subject contains [SBD Msg]
  -b BEGIN, --begin BEGIN
                        since date (d-MMM-yyyy) UTC (e.g. 1-jan-2023)
  -e END, --end END     end date (d-MMM-yyyy) UTC (e.g. 1-jan-2023, does not include this day)
  -i IMAP, --imap IMAP  imap server [imap.gmail.com]

optional arguments:
  -n NUMBER, --number NUMBER
                        (optional) report the last NUMBER msgs
  -k KEEP, --keep KEEP  (optional) keep messages in directory
  -j, --json            (optional) output json instead of text
  -r REPEAT, --repeat REPEAT
                        (optional) repeat the download after REPEAT seconds
  -c, --config          Print the configuration (including switches) and exit
  -v, --verbose         (optional) verbose

Note: some arguments may already be specified in ~/.config/SbdMail/SbdMail.ini. 
You will need an application key to connect to a Gmail IMAP server.
```
