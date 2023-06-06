import os
import tempfile
import platform
import sys
from .functionsBase import load_xml_dictionary
import xml.etree.ElementTree as ET

# what do we call this thing?
app_name = 'emu-config'

# get os and current working dir
os_bitness = platform.architecture()[0]  # gets either '32bit' or '64bit'
os_bitness_num = os_bitness.replace("bit","")  # gets either '32' or '64'
path_working = os.getcwd()
path_config_xml = os.path.join(path_working,'config.xml')
os_name_sys = os.name
os_sys_platform = sys.platform
os_sep = os.sep

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

# github token
github_token = os.environ.get('GITHUB_TOKEN')

# base directories
if os_name == 'win':
    path_home       = os.path.expandvars('${HOMEDRIVE}${HOMEPATH}')
    path_app_data   = os.path.join(os.path.expandvars('${LOCALAPPDATA}'),'Programs',app_name)
    path_app_config = os.path.join(os.path.expandvars('${LOCALAPPDATA}'),app_name)
    path_app_cache  = os.path.join(os.path.expandvars('${LOCALAPPDATA}'),app_name,'cache')
    path_app_log    = os.path.join(os.path.expandvars('${LOCALAPPDATA}'),app_name,'log')
elif os_name == 'linux':
    path_home       = os.path.expandvars('${HOME}')
    path_app_data   = os.path.join(path_home,'.local','share',app_name)
    path_app_config = os.path.join(path_home,'.config',app_name)
    path_app_cache  = os.path.join(path_home,'.local','state',app_name,'cache')
    path_app_log    = os.path.join(path_home,'.local','state',app_name,'log')
elif os_name == 'mc':
    pass
elif os_name == 'android':
    pass
else:
    exit
path_emulation  = os.path.join(path_home,'Emulation')
path_desktop = os.path.join(path_home,'Desktop',app_name)
path_temp = tempfile.gettempdir()

base = { 
    'home':path_home,
    'desktop':path_desktop,
    'app_data':path_app_data,
    'app_config':path_app_config,
    'app_log':path_app_log,
    'app_cache':path_app_cache,
    'temp':path_temp,
    'os_name':os_name,
    'os_name_full':os_name_full,
    'os_bitness':os_bitness,
    'os_bitness_num':os_bitness_num,
    'path_working':path_working,
    'path_config_xml':path_config_xml,
    'github_token':github_token,
    'emulation':path_emulation,
    'os_sep':os_sep,
    'dict_name':"base"
}

# get default settings
default = load_xml_dictionary(base['path_config_xml'],'default_settings')