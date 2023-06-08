import json
import sys
import os
import platform

# get OS information
os_name_sys = os.name
os_sys_platform = sys.platform
os_bitness = platform.architecture()[0]  # gets either '32bit' or '64bit'
os_bitness_num = os_bitness.replace("bit","")  # gets either '32' or '64'

if os_name_sys == 'nt':
        os_name_full = 'windows'
        os_name = 'win'
elif os_name_sys == 'posix':
    if os_sys_platform.startswith('linux'):
        os_name_full = 'linux'
        os_name = 'linux'
    elif os_sys_platform.startswith('darwin'):
        os_name_full = 'mac'
        os_name = 'mac'
    elif os_sys_platform.startswith('android'):
        os_name_full = 'android'
        os_name = 'android'
else:
    os_name_full = 'Unknown'
    os_name = 'Unknown'

path_working = os.getcwd()
path_config_json = os.path.join(path_working,'config.json')

if not os.path.isfile(path_config_json):
    print(f"Configuration file {path_config_json} does not exist.")
    sys.exit()

with open(path_config_json, 'r') as f:
    config = json.load(f)

# quick function to iterate through core paths and evaluate variables from the json
def path_elements(dictionary_path, app_name):
    path_elements = []
    for element in dictionary_path:
        if '${' in element and '}' in element:
            placeholder = element.replace('${', '').replace('}', '')
            if placeholder == 'app_name':
                path_elements.append(app_name)
            else:
                path_elements.append(os.environ.get(placeholder, ''))
        else:
            path_elements.append(element)
    return path_elements

# export default settings
default = config['configuration']['default_settings']

# export core directories
app_name = default['appname']

core = config['configuration']['os']
if os_name == 'win':
    core = {'core': core['win']}
elif os_name == 'linux':
    core = {'core': core['linux']}

for key in core['core'].keys():
    core['core'][key] = os.path.join(*path_elements(core['core'][key], app_name))

# github token
github_token = os.environ.get('GITHUB_TOKEN')

# export os variables
osvar = {
    "osvar": {
        "os_name":os_name,
        "os_name_full":os_name_full,
        "os_bitness":os_bitness,
        "os_bitness_num":os_bitness_num
    }
}