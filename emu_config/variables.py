from .variablesBase import base
from .functionsBase import load_xml_dictionary
from .functions import *
from .functionsNet import get_program_version
from .log import log
import json
import re

# Config file location
config_file = base['path_config_xml']
os_sep = base['os_sep']

# Load the path dictionaries
path = load_xml_dictionary(config_file,'paths')

# replace ${sep} text in path dictionary values with the proper os.sep
path = {k: v.replace('${sep}', os_sep) for k, v in path.items()}
path['dict_name'] = 'path'
log.debug('path dictionary before replacement: '+json.dumps(path, indent=4))

# replace path dictionary value path_base variables with their evaluated form
path = replace_placeholders_in_dict(base, path)
path = resolve_placeholders(path)

# create dictionaries for each program with paths evaluated
program = load_xml_dictionary(config_file,'programs')
program['dict_name'] = 'program'
log.debug('program dictionary before replacement: '+json.dumps(program, indent=4))

# update current version for each program
for program_name in program.keys():
    if program_name != 'dict_name':
        for property in program[program_name].keys():
            if property == 'currentversion':
                current_version = None
                try:
                    current_version = get_program_version(program_name, program[program_name]['version']['url'], program[program_name]['version']['type'])
                except Exception as e:
                    log.error(str(program_name)+": Unable to get program version.")
                    log.error(str(program_name)+": Exception: "+str(e))
                else:
                    if current_version is not None:
                        program[program_name][property] = current_version
                        log.info(str(program_name)+" current version: "+str(current_version))
                    else:
                        log.error(str(program_name)+" unable to retrieve current version: "+str(current_version))
                # finally: 
                #     if current_version is not None:
                #         program[program_name][property] = current_version
                #         log.info(str(program_name)+" current version: "+str(current_version))
                #     else:
                #         log.error(str(program_name)+" unable to retrieve current version: "+str(current_version))
log.debug('program dictionary after version replacement: '+json.dumps(program, indent=4))                  
# replace the text dictionary keys in target dictionary values with evaluated values of those keys from source dictionary
program = replace_placeholders_in_dict(base, program)
program = resolve_placeholders(program)

# then load custom variables from settings if available


# if 'updateconfig' in program['steamrommanager']:
#     print("yes")
# else:
#     print("no")