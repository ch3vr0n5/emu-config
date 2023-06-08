from .core import config, core, osvar, github_token
from .functions import *
from .log import log
import json
import re

# some debugging
cache_path = core['core']['cache']

if github_token == '' or github_token is None:
    log.debug('GitHub token not present.') 
else:
    log.debug('GitHub token present.')

if os.path.exists(cache_path):
    log.debug('Cache path already exists: '+cache_path)
else:
    log.debug('Cache path created: '+cache_path)

# Load the dictionaries
paths = {'paths': config['configuration']['paths']}
programs = {'programs': config['configuration']['programs']}

# update program versions
update_program_versions(programs)

# resolve any dictionary references in key values:
update_dictionaries([paths, core, programs, osvar])                 


# then load custom variables from settings if available


# if 'updateconfig' in programs['steamrommanager']:
#     print("yes")
# else:
#     print("no")