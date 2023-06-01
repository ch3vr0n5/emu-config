import os
import xml.etree.ElementTree as ET
import functions

# load os specific paths from xml to dictionary and 
def load_xml_dictionary(file_path,xml_path,depth):
    # Parse XML file
    tree = ET.parse(file_path)

    # Get the root element
    root = tree.getroot()

    # Create a dictionary to hold the key values
    output = {}
    
    # Find the designated element
    root_node = root.find(xml_path)

    # Iterate over each child element
    if depth == 2:
        for child in root_node:
            node = child.tag
            output[node] = {}
            for subchild in child:
                # Use the tag as the key and the text as the value
                output[node][subchild.tag] = subchild.text
    elif depth == 1:
        for child in root_node:
            output[child.tag] = child.text

    return output

# get os and current working dir
os_name = functions.get_os()
path_working = os.getcwd()
path_config_xml = os.path.join(path_working,'emu-config','config.xml')

# get os paths dictionary
paths_os = load_xml_dictionary(path_config_xml,'variables/ospath',2)

# base os dirs
path_user = os.path.expandvars(paths_os[os_name]['user'])
path_config = os.path.expandvars(paths_os[os_name]['config'])
path_bin = os.path.expandvars(paths_os[os_name]['bin'])

# Load the path dictionaries
paths = load_xml_dictionary(path_config_xml,'variables/paths',1)
paths = {k: v.replace('path_user', path_user) for k, v in paths.items()}
paths = {k: v.replace('path_emulation', paths['emulation']) for k, v in paths.items()}
paths = {k: v.replace('${sep}', os.sep) for k, v in paths.items()}

# create dictionaries for each program with paths evaluated

#then load custom variables from settings if available

print(paths)