import os
import requests
import pickle
import time
import re
from .log import log
from .variablesBase import base

cache_path = base['app_cache']
os_name = base['os_name']
os_bitness_num = base['os_bitness_num']
github_token = base['github_token']
device_type = ''

def is_valid_version(version):
    return bool(re.match("^[0-9.-]*$", version))

if github_token == '' or github_token is None:
    github_token_exists = False
    log.debug('GitHub token not present.') 
else:
    log.debug('GitHub token present.')
    github_token_exists = True

if os.path.exists(cache_path):
    log.debug('Cache path already exists: '+cache_path)
else:
    os.makedirs(cache_path, exist_ok=True)
    log.debug('Cache path created: '+cache_path)

# based on os, lookup url, lookup type (git-hub, or web-scrape), include strings and exclude strings
# we can construct the download url. This method prefers the bitness of the OS as well as portable releases for windows
def get_program_url(lookup_url, lookup_method, includes="", excludes=""):
    log.debug("get_program_url: lookupurl:"+lookup_url+" lookup_method:"+lookup_method+" includes:"+includes+" excludes:"+excludes)
    
    cache = {}
    cache_file = os.path.join(cache_path,'emu-config-download-response.cache')
    
    if lookup_method == 'git-hub':

        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                cache = pickle.load(f)

        current_time = time.time()
        if lookup_url in cache and current_time - cache[lookup_url]['time'] < 600:  # 600 seconds = 10 minutes
            log.debug("get_program_url: Using cached data")
            log.debug("get_program_url: Returned "+cache[lookup_url]['data'])
            return cache[lookup_url]['data']

        if github_token_exists:
            headers = {
                'Authorization': f'Bearer {github_token}',
            }
        try:   
            log.debug("get_program_url: Fetching new version from internet") 
            response = requests.get(lookup_url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            log.error("get_program_url: "+f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            log.error("get_program_url: "+f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            log.error("get_program_url: "+f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            log.error("get_program_url: "+f"Something went wrong: {err}")
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
                log.error("get_program_url: "+"Error: response.status_code = "+str(response.status_code)+". It should be 200.")
    return None


def get_program_version(program_name, lookup_url, lookup_method):
    program_version = None
    log.debug(str(program_name)+": get_program_version: lookupurl:"+lookup_url+" lookup_method:"+lookup_method)

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
            log.debug(str(program_name)+": get_program_version: "+"Using cached data")
            log.debug(str(program_name)+": get_program_version: Returned "+str(cache_data))
            return cache_data
        else: 
            log.debug(str(program_name)+": get_program_version: CACHE: cache_url_exists: "+str(cache_url_exists))
            log.debug(str(program_name)+": get_program_version: CACHE: current_time_check: "+str(current_time_check))
            log.debug(str(program_name)+": get_program_version: CACHE: cache_version_check: "+str(cache_version_check))
            log.debug(str(program_name)+": get_program_version: CACHE: setting program_version to cache_data as fallback: "+str(cache_data))
            program_version = cache_data

    if lookup_method == "git-hub":
        headers = {}

        try:   
            log.debug(str(program_name)+": get_program_version: "+"Fetching new version from internet") 
            if github_token_exists:
                headers = {
                    'Authorization': f'Bearer {github_token}',
                }
                response = requests.get(lookup_url, headers=headers)
            else:
                response = requests.get(lookup_url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            log.error(str(program_name)+": get_program_version: "+f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            log.error(str(program_name)+": get_program_version: "+f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            log.error(str(program_name)+": get_program_version: "+f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            log.error(str(program_name)+": get_program_version: "+f"Something went wrong: {err}")
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

                        log.debug(str(program_name)+": get_program_version: "+"New version fetched: "+str(program_version)) 
                        return program_version
                    else:
                        log.error(str(program_name)+": get_program_version: Invalid version: "+str(program_version))
                        return program_version
                elif "API rate limit exceeded" in data:
                    log.error(str(program_name)+": get_program_version: "+"API rate limit exceeded.")
                    return program_version
                else:
                    log.error(str(program_name)+": get_program_version: "+"'tag_name' not in response. Full response:")
                    log.error(str(program_name)+": get_program_version: "+str(data))
                    return program_version
            else:
                log.error(str(program_name)+": get_program_version: "+"Error: response.status_code = "+str(response.status_code)+". It should be 200.")
                return program_version
        finally:
                return program_version
    if lookup_method == "git-lab":

        try:   
            log.debug(str(program_name)+": get_program_version: "+"Fetching new version from internet") 
            response = requests.get(lookup_url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            log.error(str(program_name)+": get_program_version: "+f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            log.error(str(program_name)+": get_program_version: "+f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            log.error(str(program_name)+": get_program_version: "+f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            log.error(str(program_name)+": get_program_version: "+f"Something went wrong: {err}")
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
                    log.error(str(program_name)+": get_program_version: "+"API rate limit exceeded.")
                    return program_version
                else:
                    log.error(str(program_name)+": get_program_version: "+"'tag_name' not in response. Full response:")
                    log.error(str(program_name)+": get_program_version: "+str(data))
                    return program_version
            else:
                log.error(str(program_name)+": get_program_version: "+"Error: response.status_code = "+str(response.status_code)+". It should be 200.")
                return program_version
        finally:
                return program_version
    elif lookup_method == "web-scrape":
        # web-scrape if needed
        pass