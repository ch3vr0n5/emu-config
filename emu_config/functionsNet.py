import os
import requests
import pickle
import time
import re
from kivy.logger import Logger

def is_valid_version(input_version):
    pattern = re.compile(r'^\d+(\.\d+){1,3}(-\d+)?$')
    return bool(pattern.match(input_version))

# based on os, lookup url, lookup type (git-hub, or web-scrape), include strings and exclude strings
# we can construct the download url. This method prefers the bitness of the OS as well as portable releases for windows
def get_program_url(lookup_url, lookup_method, cache_path, github_token, os_name, os_bitness_num, device_type, includes="", excludes=""):
    Logger.debug("Net Functions: lookupurl:"+lookup_url+" lookup_method:"+lookup_method+" includes:"+includes+" excludes:"+excludes)

    if github_token is None or github_token == '': github_token_exists = False 
    else: github_token_exists = True
    
    cache = {}
    cache_file = os.path.join(cache_path,'emu-config-download-response.cache')
    
    if lookup_method == 'git-hub':

        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                cache = pickle.load(f)

        current_time = time.time()
        if lookup_url in cache and current_time - cache[lookup_url]['time'] < 600:  # 600 seconds = 10 minutes
            Logger.debug("Net Functions: Using cached data")
            Logger.debug("Net Functions: Returned "+cache[lookup_url]['data'])
            return cache[lookup_url]['data']

        if github_token_exists:
            headers = {
                'Authorization': f'Bearer {github_token}',
            }
        try:   
            Logger.debug("Net Functions: Fetching new version from internet") 
            response = requests.get(lookup_url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            Logger.error("Net Functions: "+f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            Logger.error("Net Functions: "+f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            Logger.error("Net Functions: "+f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            Logger.error("Net Functions: "+f"Something went wrong: {err}")
        else:
            if response.status_code == 200:
                release_info = response.json()
                assets = release_info.get('assets', [])

                os_specific_assets = [
                    asset for asset in assets
                        if ((os_name == 'linux' and 
                                (('AppImage' in asset['name'] or os_name in asset['name']) and
                                includes in asset['name'] and 
                                excludes not in asset['name']))
                            # steam deck and other device specifics, need to parse "device type"
                            or (os_name == 'linux' and device_type != '' and
                                (('AppImage' in asset['name'] or os_name in asset['name']) and
                                device_type in asset['name'] and
                                includes in asset['name'] and 
                                excludes not in asset['name']))
                            or (os_name in asset['name'] and
                                includes in asset['name'] and
                                excludes not in asset['name']))
                ]


                if os_specific_assets:
                    # sort assets by preference for 64bit,'portable' for windows, and device type (like steamdeck)
                    os_specific_assets.sort(key=lambda a: (os_bitness_num in a['name'], 'portable' in a['name'], 'SteamDeck' in a['name']), reverse=True)

                    download_url = os_specific_assets[0]['browser_download_url']

                    # Cache the data along with the current time
                    cache[lookup_url] = {'data': download_url, 'time': current_time}

                    # Write the updated cache to the file
                    with open(cache_file, 'wb') as f:
                        pickle.dump(cache, f)

                    # return the download url of the most preferred asset
                    return download_url
            else:
                Logger.error("Net Functions: "+"Error: response.status_code = "+str(response.status_code)+". It should be 200.")
    return None


def get_program_version(program_name, lookup_url, lookup_method, cache_path, github_token):
    program_version = None
    Logger.debug("Net Functions:  "+str(program_name)+" - lookupurl:"+lookup_url+" - lookup_method:"+lookup_method)

    if github_token is None or github_token == '': github_token_exists = False 
    else: github_token_exists = True

    cache = {}
    cache_file = os.path.join(cache_path,'emu-config-version-response.cache')

    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            cache = pickle.load(f)

    current_time = time.time()
    cache_time = cache[lookup_url]['time']
    cache_data = cache[lookup_url]['data']
    current_time_check = current_time - cache_time < 600
    cache_version_check = is_valid_version(cache_data)
    cache_url_exists = lookup_url in cache
    if cache_url_exists and cache_version_check:  # 600 seconds = 10 minutes
        if current_time_check:
            Logger.debug("Net Functions:  "+str(program_name)+" - Using cached data")
            Logger.debug("Net Functions:  "+str(program_name)+" - Returned "+str(cache_data))
            return cache_data
        else: 
            Logger.debug("Net Functions:  "+str(program_name)+" - CACHE: cache_url_exists: "+str(cache_url_exists))
            Logger.debug("Net Functions:  "+str(program_name)+" - CACHE: current_time_check: "+str(current_time_check))
            Logger.debug("Net Functions:  "+str(program_name)+" - CACHE: cache_version_check: "+str(cache_version_check))
            Logger.debug("Net Functions:  "+str(program_name)+" - CACHE: setting program_version to cache_data as fallback: "+str(cache_data))
            program_version = cache_data

    if lookup_method == "git-hub":
        headers = {}

        try:   
            Logger.debug("Net Functions:  "+str(program_name)+" - "+"Fetching new version from internet") 
            if github_token_exists:
                headers = {
                    'Authorization': f'Bearer {github_token}',
                }
                response = requests.get(lookup_url, headers=headers)
            else:
                response = requests.get(lookup_url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            Logger.error("Net Functions:  "+str(program_name)+" - "+f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            Logger.error("Net Functions:  "+str(program_name)+" - "+f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            Logger.error("Net Functions:  "+str(program_name)+" - "+f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            Logger.error("Net Functions:  "+str(program_name)+" - "+f"Something went wrong: {err}")
        else:
            if response.status_code == 200:
                data = response.json()
                if 'latest' not in lookup_url:
                    data = data[0]
                if "tag_name" in data:
                    program_version = data["tag_name"].replace("v","")

                    if is_valid_version(str(program_version)):
                        # Cache the data along with the current time
                        cache[lookup_url] = {'data': program_version, 'time': current_time}

                        # Write the updated cache to the file
                        with open(cache_file, 'wb') as f:
                            pickle.dump(cache, f)

                        Logger.debug("Net Functions:  "+str(program_name)+" - "+"New version fetched: "+str(program_version)) 
                        return program_version
                    else:
                        Logger.error("Net Functions:  "+str(program_name)+" - Invalid version: "+str(program_version))
                        return program_version
                elif "API rate limit exceeded" in data:
                    Logger.error("Net Functions:  "+str(program_name)+" - "+"API rate limit exceeded.")
                    return program_version
                else:
                    Logger.error("Net Functions:  "+str(program_name)+" - "+"'tag_name' not in response. Full response:")
                    Logger.error("Net Functions:  "+str(program_name)+" - "+str(data))
                    return program_version
            else:
                Logger.error("Net Functions:  "+str(program_name)+" - "+"Error: response.status_code = "+str(response.status_code)+". It should be 200.")
                return program_version
        finally:
                return program_version
    if lookup_method == "git-lab":

        try:   
            Logger.debug("Net Functions:  "+str(program_name)+" - "+"Fetching new version from internet") 
            response = requests.get(lookup_url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            Logger.error("Net Functions:  "+str(program_name)+" - "+f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            Logger.error("Net Functions:  "+str(program_name)+" - "+f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            Logger.error("Net Functions:  "+str(program_name)+" - "+f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            Logger.error("Net Functions:  "+str(program_name)+" - "+f"Something went wrong: {err}")
        else:
            if response.status_code == 200:
                data = response.json()
                data = data[0]
                if "tag_name" in data:
                    program_version = data["tag_name"].replace("v","")
                # data = json.loads(response.text)
                # if "version" in data['stable']:
                #     program_version = data['stable'].get('version', 'Unknown').replace('v', '')

                    # Cache the data along with the current time
                    cache[lookup_url] = {'data': program_version, 'time': current_time}

                    # Write the updated cache to the file
                    with open(cache_file, 'wb') as f:
                        pickle.dump(cache, f)

                    return program_version
                elif "API rate limit exceeded" in data:
                    Logger.error("Net Functions:  "+str(program_name)+" - "+"API rate limit exceeded.")
                    return program_version
                else:
                    Logger.error("Net Functions:  "+str(program_name)+" - "+"'tag_name' not in response. Full response:")
                    Logger.error("Net Functions:  "+str(program_name)+" - "+str(data))
                    return program_version
            else:
                Logger.error("Net Functions:  "+str(program_name)+" - "+"Error: response.status_code = "+str(response.status_code)+". It should be 200.")
                return program_version
        finally:
                return program_version
    elif lookup_method == "web-scrape":
        # web-scrape if needed
        pass