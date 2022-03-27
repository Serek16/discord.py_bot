from configparser import ConfigParser

def config(section, filename='config.ini'):

    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read("config.ini")

    # get section
    return_params = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            return_params[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    
    return return_params