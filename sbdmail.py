import os
import signal
import sys
from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
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
Fetch recent Iridium email messages and decode them as text or json.
If --keep is specified, the message attachments will be saved:
python3 sbdmail.py -b 9-apr-2023 11-apr-2023 -n 1

Arguments not specified on the command line are taken from
{config.configPath()}.

Run the program once to create the initial .ini file, (it will give errors),
and then edit {config.configPath()}

**Be careful of sharing this file, if account/password details are specified there.**

**You may need to specify an end date one day in the future to retreive very recent messages**
'''

        epilog = f'''
Note: some arguments may already be specified in {config.configPath()}.
'''

        parser = ArgumentParser(description=description, epilog=epilog, formatter_class=RawTextHelpFormatter)
        required = parser.add_argument_group('required arguments')
        required.add_argument("-a", "--account", help="email account",                 action="store", default=config.values()['Main']['EmailAccount'])
        required.add_argument("-p", "--password",help="mailbox password",              action="store", default=config.values()['Main']['EmailPassword'])
        required.add_argument("-t", "--subject", help="subject contains [SBD Msg]",    action="store", default=config.values()['Main']['SearchSubject'])
        required.add_argument("-b", "--begin",   help="since date (d-MMM-yyyy) UTC (e.g. 1-jan-2023)",   action="store")
        required.add_argument("-e", "--end",     help="end date (d-MMM-yyyy) UTC (e.g. 1-jan-2023, does not include this day)", action="store")
        required.add_argument("-i", "--imap",    help="imap server [imap.gmail.com]",  action="store", default=config.values()['Main']['ImapServer'])
        optional = parser.add_argument_group('optional arguments')
        optional.add_argument("-n", "--number",  help="(optional) report the last NUMBER msgs (0==all)",   action="store", default=0, type=int)
        optional.add_argument("-k", "--keep",    help="(optional) keep message in directory",     action="store", default=os.path.expanduser(config.values()['Main']['KeepFilesDirectory']))
        optional.add_argument('-j', '--json',    help='(optional) output json instead of text',   action='store_true')
        optional.add_argument('-r', '--repeat',  help='(optional) repeat the download after REPEAT seconds (0 == no repeat)', action='store', default=0, type=int)
        optional.add_argument("-v", "--verbose", help="(optional) verbose",                       action="store_true", default = False)
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
