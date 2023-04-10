import os
import signal
import sys
from argparse import ArgumentParser
from ConfigIni import ConfigIni
from SbdProcessor import SbdProcessor

if __name__ == "__main__":
    def sigint_handler(x, y):
        '''Catch SIGINT so that we can terminate without a backtrace
        '''
        print('')
        print(f'{sys.argv[0]} terminated by SIGINT')
        sys.exit(0)

    def parseArgs(appName:str) -> (dict, str):
        '''Get configuration from the ini file and the command line arguments.'''


        defaults = {
            "Main" : {
                "EmailAccount" : "myemail@gmail.com",
                "EmailPassword": "hidden",
                "SearchSubject": "SBD Msg",
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
        parser.add_argument("-t", "--subject", help="subject contains [SBD Msg]",    action="store", default=config.values()['Main']['SearchSubject'])
        parser.add_argument("-b", "--begin",   help="since date (d-MMM-yyyy) UTC (e.g. 1-jan-2023)",   action="store")
        parser.add_argument("-e", "--end",     help="end date (d-MMM-yyyy) UTC (e.g. 1-jan-2023, does not include this day)", action="store")
        parser.add_argument("-i", "--imap",    help="imap server [imap.gmail.com]",  action="store", default=config.values()['Main']['ImapServer'])
        parser.add_argument("-n", "--number",  help="report the last NUMBER msgs (0==all)",   action="store", default=0, type=int)
        parser.add_argument("-k", "--keep",    help="keep message in directory",     action="store", default=os.path.expanduser(config.values()['Main']['KeepFilesDirectory']))
        parser.add_argument('-j', '--json',    help='output json instead of text',   action='store_true')
        parser.add_argument('-r', '--repeat',  help='repeat the down load after REPEAT seconds (0 == no repeat)', action='store', default=0, type=int)
        parser.add_argument("-v", "--verbose", help="verbose",                       action="store_true", default = False)
        args = parser.parse_args()

        if not (args.account and args.password and args.begin and args.end):
            parser.print_help()
            sys.exit(1) 

        # Convert args to a dictionary
        argsDict = vars(args)

        # Add the config path
        argsDict['configPath'] = config.configPath()

        return(argsDict)

    args = parseArgs('SbdMail')

    # Catch SIGINT
    signal.signal(signal.SIGINT, sigint_handler)

    processor = SbdProcessor(args=args)
    processor.process()
