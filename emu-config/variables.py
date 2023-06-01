import os
import tempfile
import platform
import functions as fn

# github token
github_token = os.environ['GITHUB_TOKEN']

# get os and current working dir
os_name = fn.get_os()
os_name_full = fn.get_os('full')
os_bitness = platform.architecture()[0]  # gets either '32bit' or '64bit'
os_bitness_num = os_bitness.replace("bit","")  # gets either '32' or '64'
path_working = os.getcwd()
path_config_xml = os.path.join(path_working,'emu-config','config.xml')

# get os paths dictionary
paths_os = fn.load_xml_dictionary(path_config_xml,'variables/ospath',2)

# base os dirs
path_user = os.path.expandvars(paths_os[os_name]['user'])
path_app = os.path.expandvars(paths_os[os_name]['app'])
path_config = os.path.expandvars(paths_os[os_name]['config'])
path_desktop = os.path.join(path_user, 'Desktop')

# base dirs
path_app_data = os.path.join(path_app, 'EmuSuite')
path_app_config = os.path.join(path_config, 'EmuSuite')
path_temp = tempfile.gettempdir()

path_base = { 
    'user':path_user,
    'app':path_app,
    'config':path_config,
    'desktop':path_desktop,
    'app_data':path_app_data,
    'app_config':path_app_config,
    'temp':path_temp,
    'os_name':os_name,
    'os_name_full':os_name_full,
    'os_bitness':os_bitness,
    'os_bitness_num':os_bitness_num
}

# Load the path dictionaries
path = fn.load_xml_dictionary(path_config_xml,'variables/paths',1)

# replace ${sep} text in path dictionary values with the proper os.sep
path = {k: v.replace('${sep}', os.sep) for k, v in path.items()}

# replace path dictionary value path_base variables with their evaluated form
for path_key in path_base.keys():
    for replace_key, replace_value in path.items():
        if "path_base['"+path_key+"']" in replace_value:
            path[replace_key] = replace_value.replace("path_base['"+path_key+"']",path_base[path_key])

# replace path dictionary value path variables with their evaluated form
for path_key in path.keys():
    for replace_key, replace_value in path.items():
        if "path['"+path_key+"']" in replace_value:
            path[replace_key] = replace_value.replace("path['"+path_key+"']",path[path_key])

# create dictionaries for each program with paths evaluated
program = fn.load_xml_dictionary(path_config_xml,'programs',2)

# update current version for each program
for program_name in program.keys():
    for property in program[program_name].keys():
        if property == 'currentversion':
            program[program_name][property] = fn.get_program_version(program[program_name]['versionurl'],program[program_name]['versionurltype'],path_base['temp'],github_token)

# replace program dictionary value text with their evaluated form
for path_key in path_base.keys():
    for program_name in program.keys():
        for replace_key, replace_value in program[program_name].items():
            if "path_base['"+path_key+"']" in replace_value and "url" in replace_key:
                program[program_name][replace_key] = replace_value.replace("path_base['"+path_key+"']",path_base[path_key])

#then load custom variables from settings if available

#print(get_download_url())
# for path_value in path_base.values():
#     print(path_value)
# for path_value in path.values():
#     print(path_value)
for key in program.keys():
    for key2, value in program[key].items():
        print(key+":"+key2+":"+value)