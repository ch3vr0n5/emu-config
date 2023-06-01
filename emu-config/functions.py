import os
import sys
import time
import pickle
import requests
import xml.etree.ElementTree as ET

# get os short name
def get_os(length=''):
    if os.name == 'nt':
        if length == 'full':
            return 'windows'
        else:
            return 'win'
    elif os.name == 'posix':
        if sys.platform.startswith('linux'):
            return 'linux'
        elif sys.platform.startswith('darwin'):
            return 'mac'
        elif sys.platform.startswith('android'):
            return 'android'
    else:
        return 'Unknown'

# load data from xml to dictionary
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
                output[node][subchild.tag] = "" if subchild.text is None else subchild.text
    elif depth == 1:
        for child in root_node:
            output[child.tag] = child.text

    return output

# based on os, lookup url, lookup type (git-api, or web-scrape), include strings and exclude strings
# we can construct the download url. This method prefers the bitness of the OS as well as portable releases for windows
def get_program_url(lookup_url, lookup_method, os_name, includes="", excludes="", bitness="64"):
    if lookup_method == 'git-api':
        response = requests.get(lookup_url)
        if response.status_code == 200:
            release_info = response.json()
            assets = release_info.get('assets', [])

            os_specific_assets = [
                asset for asset in assets 
                if os_name in asset['name'] and
                   includes in asset['name'] and
                   excludes not in asset['name']
            ]

            if os_specific_assets:
                # sort assets by preference for 64bit and 'portable' for windows
                os_specific_assets.sort(key=lambda a: (bitness in a['name'], 'portable' in a['name']), reverse=True)

                # return the download url of the most preferred asset
                return os_specific_assets[0]['browser_download_url']

    return None

def get_program_version(lookup_url, lookup_method, cache_path, github_token):
    if lookup_method == "git-api":
        cache = {}
        cache_file = os.path.join(cache_path,'emu-config-version-response.cache')

        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                cache = pickle.load(f)

        current_time = time.time()
        if lookup_url in cache and current_time - cache[lookup_url]['time'] < 600:  # 600 seconds = 10 minutes
            print("Using cached data")
            return cache[lookup_url]['data']

        if github_token:
            print("GitHub Token Exists.")
            headers = {
                'Authorization': f'Bearer {github_token}',
            }
        try:   
            print("Fetching new version from internet") 
            response = requests.get(lookup_url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print(f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            print(f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            print(f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            print(f"Something went wrong: {err}")
        else:
            if response.status_code == 200:
                data = response.json()
                if "tag_name" in data:
                    program_version = data["tag_name"].replace("v","")

                    # Cache the data along with the current time
                    cache[lookup_url] = {'data': program_version, 'time': current_time}

                    # Write the updated cache to the file
                    with open(cache_file, 'wb') as f:
                        pickle.dump(cache, f)

                    return program_version
                elif "API rate limit exceeded" in data:
                    print("API rate limit exceeded.")
                    return None
                else:
                    print("Error: 'tag_name' not in response. Full response:")
                    print(data)
                    return None
    elif lookup_method == "web-scrape":
        # You can implement web scraping logic here, which depends on the specific page structure
        pass