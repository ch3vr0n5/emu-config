from .functionsNet import *
import os
import re
from copy import deepcopy
from kivy.logger import Logger

# define local functions
def update_versions(programs, cache_path, github_token):
    for program_name in programs.keys():
        for property in programs[program_name]['version'].keys():
            if property == 'current':
                current_version = None
                try:
                    version_url = programs[program_name]['version']['url']
                    version_type = programs[program_name]['version']['type']
                    current_version = get_program_version(program_name, version_url, version_type, cache_path, github_token)
                except Exception as e:
                    Logger.error("Variables:  -"+str(program_name)+": Unable to get program version.")
                    Logger.error("Variables:  -"+str(program_name)+": Exception: "+str(e))
                else:
                    if current_version is not None:
                        programs[program_name]['version']['current'] = current_version
                        Logger.info("Variables:  -"+str(program_name)+" current version: "+str(current_version))
                    else:
                        Logger.error("Variables:  -"+str(program_name)+" unable to retrieve current version: "+str(current_version))

# helper to flatten nested dictionary keys
def flatten(dictionary, parent_key='', separator='^'):
    items = []
    temp_dictionary = dict(dictionary)
    for k, v in temp_dictionary.items():
        new_key = parent_key + separator + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten(v, new_key, separator=separator).items())
        else:
            items.append((new_key, v))
    return dict(items)

# helper to unflatten nested dictionary keys
def unflatten(dictionary, separator='^'):
    result = {}
    for k, v in dictionary.items():
        parts = k.split(separator)
        dictionary = result
        for p in parts[:-1]:
            if p not in dictionary:
                dictionary[p] = {}
            dictionary = dictionary[p]
        dictionary[parts[-1]] = v
    return result

# flatten dictionaries and combine into a single dictionary. then loop through and resolve any references. finally, join paths
def update_dictionaries(dictionary_list):
    # flatten the dictionaries into a single dictionary
    flattened_dictionaries = [flatten(dictionary, separator='^') for dictionary in dictionary_list]
    # instance a transient dictionary for updating
    transient_dictionary = {k: v for d in flattened_dictionaries for k, v in d.items()}

    Logger.debug(f"Variables:  flattened_dictionaries: {flattened_dictionaries}")
    
    # instance a temp dictionary for reference and a loop count for debug
    temp_dictionary = None
    loop_instance = 0

    # Resolve values
    while transient_dictionary != temp_dictionary:
        def replace_reference(input_value):
            # Extract the referenced key
            # Find the start and end indices of the reference
            start_index = input_value.find("$[") + 2
            end_index = input_value.find("]", start_index)

            # Extract the referenced key
            referenced_key = input_value[start_index:end_index]
            find_value = (f"$[{referenced_key}]")
            Logger.debug(f"Variables:  Referenced key: {referenced_key}")

            # Check if referenced key exists
            if referenced_key in transient_dictionary:

                # create checks for referenced key value, make sure it's not a list, and make sure it doesn't have an unresolved key
                referenced_value = transient_dictionary[referenced_key]

                is_contains_key = 0
                is_list = isinstance(referenced_value, list)

                if is_list:
                    for element in enumerate(referenced_value):
                        is_contains_key_start = "$[" in element
                        is_contains_key_end = "]" in element
                        if is_contains_key_start and is_contains_key_end: is_contains_key += 1
                else:
                    is_contains_key_start = "$[" in referenced_value
                    is_contains_key_end = "]" in referenced_value
                    if is_contains_key_start and is_contains_key_end: is_contains_key += 1

                # Replace the reference with the actual value
                if is_contains_key > 0:
                    Logger.debug(f"Variables:  Referenced key value still has unresolved references: {referenced_value}")
                elif is_list:
                    Logger.debug(f"Variables:  Referenced key value is still a list: {referenced_value}")
                else:
                    replaced_value = input_value.replace(find_value,referenced_value)
                    return replaced_value
            else:
                Logger.debug(f"Variables:  No match found for reference: {input_value}") 
                return input_value

        def resolve_reference(input_value, i=None): 
            is_string = isinstance(input_value, str)
            is_contains_key_start = "$[" in input_value
            is_contains_key_end = "]" in input_value

            # skip if input value is nothing
            if input_value is not None or input_value != "":
                Logger.debug(f"Variables:  Checking reference in input_value: {input_value} - Is string: {is_string} - Contains \"$['\" {is_contains_key_start} - Contains \"']\" {is_contains_key_end}")
                # Check if the element is a string and contains a reference
                if is_string and is_contains_key_start and is_contains_key_end:
                    Logger.debug(f"Variables:  Reference found")

                    reference_count = input_value.count("$[")

                    # If there are multiple references in the input string, split and process each part
                    if reference_count > 1:
                        Logger.debug(f"Variables:  Multiple references found: {reference_count}")
                        split_indices = [0] + [m.start() for m in re.finditer("\$\[", input_value)]
                        split_parts = [input_value[i:j] for i,j in zip(split_indices, split_indices[1:]+[None])]



                        split_list = []
                        for part in split_parts:
                            split_list.append(replace_reference(part))
                            updated_value = "".join(split_list) if split_list else None
                        
                    else:
                        updated_value = replace_reference(input_value)

                    if updated_value is not None and input_value != updated_value:
                        if i is not None:
                            transient_dictionary[key][i] = updated_value
                        else:
                            transient_dictionary[key] = updated_value
                        Logger.debug(f"Variables:  Replaced reference : {input_value} with value: {updated_value}")



        if transient_dictionary != temp_dictionary or temp_dictionary == None:
            Logger.debug(f"Variables:  Looping: {loop_instance}")
            # deepcopy makes sure we have a true copy of the dictionary and the mutable values are not references
            temp_dictionary = deepcopy(transient_dictionary)
            loop_instance += 1

        for key, value in transient_dictionary.items():
            Logger.debug(f"Variables:  Checking key: {key}, value: {value}")
            
            # Check if the current value is a list
            if isinstance(value, list):
                # since it is a list, lets check if it can be joined
                is_contains_key = 0
                is_contains_paths = "paths" in str(key)
                for i, element in enumerate(value):
                    is_contains_key_start = "$[" in element
                    is_contains_key_end = "]" in element
                    if is_contains_key_start and is_contains_key_end: is_contains_key += 1

                # join if it can be joined, otherwise, move on to resolving references:
                if is_contains_paths and is_contains_key == 0:
                    new_value = os.path.join(*value)
                    transient_dictionary[key] = new_value
                    Logger.debug(f"Variables:  Joined path for key: {key} Value: {new_value}")
                else:
                    Logger.debug(f"Variables:  is_contains_path: {is_contains_paths} - is_contains_key: {is_contains_key} - Value: {value}")
                    # Resume replacing, Iterate over each element in the list
                    for i, list_value in enumerate(value):
                        resolve_reference(list_value,i)
            elif isinstance(value, str):
                resolve_reference(value)
        # Logger.debug('transient_dictionary: '+json.dumps(transient_dictionary, indent=4))    
        # Logger.debug('temp_dictionary: '+json.dumps(temp_dictionary, indent=4))
    
    # Update the original dictionaries with the replaced values
    for original, flattened in zip(dictionary_list, flattened_dictionaries):
        for key in flattened.keys():
            if key in transient_dictionary:
                flattened[key] = transient_dictionary[key]
        original.update(unflatten(flattened, separator='^'))

    # Remove top level keys
    clean_dictionary_list = []
    for dictionary in dictionary_list:
        # assuming each dictionary has a single top level key
        top_level_key = list(dictionary.keys())[0]  
        clean_dictionary = dictionary[top_level_key]
        clean_dictionary_list.append(clean_dictionary)

    return clean_dictionary_list

def initialize_variables_get_versions(config, cache_path, github_token):
    # some debugging
    paths = {}
    programs = {}

    # Load the dictionaries
    paths = config['paths']
    programs = config['programs']

    # update program versions
    update_versions(programs, cache_path, github_token)

    return paths, programs


def initialize_variables_update_dictionaries(core_temp, os_var_temp, paths_temp, programs_temp):
    core_temp = {'core': core_temp}
    os_var_temp = {'os_var': os_var_temp}
    paths_temp = {'paths': paths_temp}
    programs_temp = {'programs': programs_temp}

    # resolve any dictionary references in key values:
    update_dictionaries([paths_temp, os_var_temp, programs_temp, core_temp])
    # update_dictionaries([paths, core, programs, osvar, config])

    # then load custom variables from settings, including installed versions, if available
    return paths_temp, programs_temp