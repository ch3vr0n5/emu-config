import os
import tempfile
import platform
import sys
from .core import *
import xml.etree.ElementTree as ET

# get os and current working dir
os_bitness = platform.architecture()[0]  # gets either '32bit' or '64bit'
os_bitness_num = os_bitness.replace("bit","")  # gets either '32' or '64'
os_sep = os.sep

# print(json.dumps(config, indent=4))



# print(core)

path_home       = os.path.join(*path_elements(core['home']))
path_app_data   = os.path.join(*path_elements(core['data']))
path_app_config = os.path.join(*path_elements(core['config']))
path_app_cache  = os.path.join(*path_elements(core['cache']))
path_app_log    = os.path.join(*path_elements(core['log']))
path_emulation  = os.path.join(*path_elements(core['emulation']))
path_desktop    = os.path.join(*path_elements(core['desktop']))
path_temp       = tempfile.gettempdir()

base = { 
    # 'home':path_home,
    # 'desktop':path_desktop,
    # 'app_data':path_app_data,
    # 'app_config':path_app_config,
    # 'app_log':path_app_log,
    # 'app_cache':path_app_cache,
    # 'temp':path_temp,
    # 'emulation':path_emulation,
    'os_name':os_name,
    'os_name_full':os_name_full,
    'os_bitness':os_bitness,
    'os_bitness_num':os_bitness_num,
    'path_working':path_working,
    'path_config_json':path_config_json,
    'github_token':github_token,
    'os_sep':os_sep,
    'dict_name':"base"
}

# print(base)