import json
import sys
import os
import platform
from kivy.logger import Logger
import logging

def initialize_core():
    config = {}
    core = {}
    os_var = {}
    default = {}

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
    path_config_json = os.path.join(path_working, 'config.json')

    # Check if we're running as a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        path_working = sys._MEIPASS
    else:
        path_working = os.path.dirname(os.path.abspath(__file__))

    # Now, bundle_dir is the directory containing your script,
    # or containing your bundled app if you're running the PyInstaller bundle.
    path_config_json = os.path.join(path_working, 'config.json')

    # if not os.path.isfile(path_config_json):
    #     #print(f"Configuration file {path_config_json} does not exist.")
    #     sys.exit()

    with open(path_config_json, 'r') as f:
        config = json.load(f)
    config = config['configuration']

    # update some dictionary values
    config['os']['var']['name'] = os_name_full
    config['os']['var']['name_short'] = os_name
    config['os']['var']['bitness'] = os_bitness
    config['os']['var']['bitness_num'] = os_bitness_num
    config['os'][os_name]['working'] = path_working
    config['os'][os_name]['config_json'] = path_config_json

    os_var = config['os']['var']

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
    default = config['default_settings']

    # export core directories
    app_name = default['appname']

    core = config['os']
    if os_name == 'win':
        core = core['win']
    elif os_name == 'linux':
        core = core['linux']

    for key, value in core.items():
        if isinstance(value, list):
            core[key] = os.path.join(*path_elements(core[key], app_name))

    return config, core, os_var, default



def initialize_core_paths(cache_path, log_path):
    if not os.path.exists(cache_path):
        os.makedirs(cache_path, exist_ok=True)

    if not os.path.exists(log_path):
        os.makedirs(log_path, exist_ok=True)



def initialize_log(log_path, default_log_level):
    from logging.handlers import TimedRotatingFileHandler
    
    log_file = os.path.join(log_path, 'emu-config-debug')
    last_run_log_file = os.path.join(log_path, 'emu-config-debug-last-run.log')

    # Set Log level
    Logger.setLevel(default_log_level)

    # Create handlers
    rotating_file_handler = TimedRotatingFileHandler(f"{log_file}.log", when="midnight", backupCount=10)
    last_run_file_handler = logging.FileHandler(last_run_log_file, mode='w')  # Open in write mode to overwrite existing file

    # Create formatters and add it to handlers
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    rotating_file_handler.setFormatter(file_format)
    last_run_file_handler.setFormatter(file_format)

    # Add handlers to the Logger
    Logger.addHandler(rotating_file_handler)
    Logger.addHandler(last_run_file_handler)

    Logger.info(f"Log: Log file: {log_file} Debug level: {default_log_level}")


