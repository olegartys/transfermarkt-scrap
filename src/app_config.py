import json


class AppConfig(object):
    '''
    Aggregates configuration options for the application.
    '''

    def __init__(self, config_path):
        ''' Constructs the new AppConfig instance.

        Parameters
        ----------
            config_path
                Path to the config file in JSON format.
        '''

        with open(config_path, 'r') as config_file:
            self.__dict__ = json.load(config_file)
