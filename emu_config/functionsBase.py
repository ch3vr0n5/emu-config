import xml.etree.ElementTree as ET
import os
# functionsBase.py

# return evaluated variables in config.json


# Function to load XML into a dictionary
def load_xml_dictionary(file_path, xml_path):
    # Parse XML file
    tree = ET.parse(file_path)

    # Get the root element
    root = tree.getroot()

    # Find the designated element
    root_node = root.find(xml_path)

    # Call recursive function to parse XML tree
    output = parse_element(root_node)

    return output

# Recursive function to parse an XML element and its children
def parse_element(element):
    output = {}
    
    for child in element:
        if len(child):  # child has its own children
            output[child.tag] = parse_element(child)
        else:
            output[child.tag] = "" if child.text is None else child.text
    
    return output