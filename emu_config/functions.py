import re
from .log import log
import json
import copy

# used to compare version numbers
def parse_version(v):
    return [int(x) for x in v.split('.')]

# # replaces dictionary key text from config.xml loaded dictionaries with their evaluated versions
# def replace_placeholders_in_dict(source, target):
#     def get_nested_dict_value(d, keys):
#         if keys:
#             return get_nested_dict_value(d.get(keys[0], {}), keys[1:])
#         else:
#             #log.debug(str(d))
#             return d
            
#     def replace_in_value(source, value):
#         if isinstance(value, dict):
#             #log.debug(str(value))
#             return {k: replace_in_value(source, v) for k, v in value.items()}
#         elif isinstance(value, str):
#             dict_name = source.get('dict_name')
#             matches = re.findall(fr"{dict_name}(\['\w+'\])+", value)
#             for match in matches:
#                 keys = match.split('[')[1:]  # Omit the first split result "dict_name"
#                 keys = [key.rstrip(']').strip("'") for key in keys]  # Clean up the keys
#                 replacement = get_nested_dict_value(source, keys)
#                 if replacement is not None:
#                     log.debug(f"Replacing: {dict_name + match} with: {str(replacement)}")
#                     value = value.replace(dict_name + match, str(replacement))
#                 else:
#                     log.debug(f"No value found for key: {keys} in source dictionary.")
#             return value
#         else:
#             return value

#     def traverse_dict(source, target):
#         return {k: replace_in_value(source, v) for k, v in target.items()}

#     # Use traverse_dict to iterate over the source and target dictionaries
#     return traverse_dict(source, target)

def resolve_placeholders(original_source):
    resolved = False
    count = 0
    while not resolved and count < 10:
        new_dict = replace_placeholders_in_dict(original_source, original_source)
        if new_dict == original_source:
            resolved = True
        else:
            original_source = new_dict
            count += 1
    return original_source


def replace_placeholders_in_dict(original_source, target):
    source = copy.deepcopy(original_source)  # copy the source dictionary
    dict_name = source.pop('dict_name', None)

    def get_nested_dict_value(d, keys):
        if keys:
            key = keys[0]
            if len(keys) == 1:
                return d.get(key)
            else:
                if isinstance(d.get(key), dict):
                    return get_nested_dict_value(d.get(key, {}), keys[1:])
                else:
                    return None
        else:
            return d

    def replace_in_value(source, value):
        if isinstance(value, dict):
            return {k: replace_in_value(source, v) for k, v in value.items()}
        elif isinstance(value, str):
            matches = re.findall(fr"{dict_name}((?:\['[\w\d_]+'\])*)", value)
            for match in matches:
                keys = match.split('[')[1:]  # Omit the first split result "dict_name"
                keys = [key.rstrip(']').strip("'") for key in keys]  # Clean up the keys

                # Don't try to replace "dict_name" itself, or if keys list is empty
                if not keys or keys[0] == 'dict_name':
                    continue

                replacement = get_nested_dict_value(source, keys)
                if replacement is not None:
                    value = value.replace(dict_name + match, str(replacement))
                else:
                    print(f"Could not replace {dict_name + match} in string: {value}")
            return value
        else:
            return value

    def traverse_dict(source, target):
        return {k: replace_in_value(source, v) for k, v in target.items()}

    # Use traverse_dict to iterate over the source and target dictionaries
    new_target = traverse_dict(source, target)

    # # If there are still placeholders left in new_target, call the function recursively
    # if any(fr"{dict_name}((?:\['[\w\d_]+'\])*)" in str(v) for v in new_target.values()):
    #     return replace_placeholders_in_dict(original_source, new_target)  # use the original source dictionary for recursion
    # else:
    return new_target

