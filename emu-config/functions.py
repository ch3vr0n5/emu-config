import os
import sys

def get_os():
    if os.name == 'nt':
        return 'win'
    elif os.name == 'posix':
        if sys.platform.startswith('linux'):
            return 'linux'
        elif sys.platform.startswith('darwin'):
            return 'mac'
        elif sys.platform.startswith('android'):
            return 'android'
    else:
        return 'Unknown'