import os
import configparser

class ConfigIni:
    '''Manage a .ini based configuration
    
    - An application name is used for the .ini file. 
    - The file will be stored in ~/.config/appName/appName.ini
    - The constructor provides a list of sections, keys and default values.

    '''

    def __init__(self, appName:str, defaults:dict) -> None:
        '''Construct a configuration
        
        app_name: General, use the application name here. A file named
           ~/.config/appName/appName.ini will be created/opened.

        defaults: a dictionary containing sections. Each section contains a
            dict of the configuration keys and their default values.
        
        '''
        self.config = configparser.ConfigParser()
        # Preserve case
        self.config.optionxform = lambda option: option
        self.appName = appName
        self.defaults = defaults
    
        self.configFilePath = os.path.expanduser(f'~/.config/{self.appName}/{self.appName}.ini')
        self.config.read(filenames=[self.configFilePath])

        for section in defaults:
            if section not in self.config.sections():
                self.config[section] = {}
            for key,default in defaults[section].items():
                self.config[section][key] = self.config[section].get(key, default)

    def set(self, section: str, key: str, value: str) -> None:
        '''Set the value for a key'''
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config[section][key] = value

    def save(self) -> None:
        '''Save the configuration'''

        os.makedirs(os.path.dirname(self.configFilePath), exist_ok=True)
        self.config.write(open(self.configFilePath, 'w+'))

    def values(self) -> dict:
        '''Return a dictionary of dictionaries of the configuration items'''
        retval = {}
        for section in self.config.keys():
            retval[section] = dict(self.config.items(section))
        return retval

    def sections(self) -> list:
        return self.config.sections()

    def configPath(self):
        '''Return the path to the configuration'''
        return self.configFilePath

if __name__ == '__main__':

    defaults = {
        "Main" : {
            "EmailAccount" : "myemail@gmail.com",
            "EmailPassword": "hidden",
            "SearchSubject": "SBD Message",
            "DaysToSearch": "2",
            "ImapServer": "imap.gmail.com",
            "KeepFilesDirectory": "~/"
        }
    }
    config = ConfigIni(appName='TestConfig', defaults=defaults)
    config.set(section='bogus', key='aNumber', value='3.1415926')
    config.set(section='bogus', key='bNumber', value='-200')

    config.save()

    print(f'Configuration path: {config.configPath()}')
    print(f'Full configuration: {config.values()}')
    print(f'Sections: {config.sections()}')
    print(f'Main: {config.values()["Main"]}')
