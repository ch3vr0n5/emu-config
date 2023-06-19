from .log import log
import os
from .functionsNet import *
import win32com.client
import configparser
import subprocess

# used to compare version numbers
def parse_version(version):
    return [int(x) for x in version.split('.')]

def create_junction(source_folder, target_folder, os_name):
    if os_name.lower() == "windows":
        command = f'mklink /J "{target_folder}" "{source_folder}"'
        subprocess.check_call(command, shell=True)

    elif os_name.lower() == "linux":
        command = ['ln', '-s', source_folder, target_folder]
        subprocess.check_call(command)

    else:
        raise ValueError(f"Unknown OS name: {os_name}")


def create_shortcut(shortcut_location, target_path, os_name):
    if os_name.lower() == "windows":
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_location)
        shortcut.Targetpath = target_path
        shortcut.WindowStyle = 3
        shortcut.save()

    elif os_name.lower() == "linux":
        config = configparser.ConfigParser()
        config.optionxform = str  # to preserve case in options
        config['Desktop Entry'] = {
            'Type': 'Application',
            'Name': os.path.basename(target_path),
            'Exec': target_path,
            'Icon': target_path,  # assuming the icon is in the same path
            'Terminal': 'false'
        }

        with open(shortcut_location, 'w') as f:
            config.write(f)

        command = ['chmod', '+x', shortcut_location]
        subprocess.check_call(command)


    else:
        raise ValueError(f"Unknown OS name: {os_name}")
