import os
from argparse import ArgumentParser
from ConfigIni import ConfigIni
from SbdProcessor import SbdProcessor

if __name__ == "__main__":
    
    def parseArgs(appName:str) -> (dict, str):
        '''Get configuration from the ini file and the command line arguments.'''


        defaults = {
            "Main" : {
                "EmailAccount" : "myemail@gmail.com",
                "EmailPassword": "hidden",
                "SearchSubject": "SBD Msg",
                "DaysToSearch": "2",
                "ImapServer": "imap.gmail.com",
                "KeepFilesDirectory": "~/"
            }
        }
        config = ConfigIni(appName=appName, defaults=defaults)
        config.save()

        description = f'''
Arguments not specified on the command line are taken from
{config.configPath()}.
Edit that file to set default values. Be careful of sharing it,
if account/password details are specified there.

Run the program once to create the initial .ini file,
Then edit that file to set your chosen defaults.
'''

        parser = ArgumentParser(description=description)
        parser.add_argument("-a", "--account", help="email account",                 action="store", default=config.values()['Main']['EmailAccount'])
        parser.add_argument("-p", "--password",help="mailbox password",              action="store", default=config.values()['Main']['EmailPassword'])
        parser.add_argument("-s", "--subject", help="subject contains [SBD Msg]",    action="store", default=config.values()['Main']['SearchSubject'])
        parser.add_argument("-d", "--days",    help="last N days [2]",               action="store", default=config.values()['Main']['DaysToSearch'])
        parser.add_argument("-i", "--imap",    help="imap server [imap.gmail.com]",  action="store", default=config.values()['Main']['ImapServer'])
        parser.add_argument("-k", "--keep",    help="keep message in directory",     action="store", default=os.path.expanduser(config.values()['Main']['KeepFilesDirectory']))
        parser.add_argument('-j', '--json',    help='output json instead of text',   action='store_true')
        parser.add_argument("-v", "--verbose", help="verbose",                       action="store_true", default = False)
        args = parser.parse_args()

        if not (args.account and args.password):
            parser.print_help()
            sys.exit(1) 

        # Convert args to a dictionary
        args = vars(args)
        # Add the config path
        args['configPath'] = config.configPath()
        return(args)

    args = parseArgs('SbdMail')

    processor = SbdProcessor(args=args)
    processor.process()
