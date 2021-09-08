import requests
import urllib.parse

## my API Key
api_key = 'b73301de1b9e48de9d350c0610414a13'
headers = {'X-API-Key': api_key}

## Base URLs
bungie_net = 'https://www.bungie.net/'
bungie_d2_url = bungie_net + 'Platform/Destiny2/'

## Class which wraps response generated in function: destiny2_api_hook(url)
class ResponseWrapper:
    def __init__(self, resp):
        self.status = resp.status_code
        self.url = resp.url
        ## members which are initialized after .json() is called on the resp returned by requests.get()
        self.response = None
        self.message = None
        self.error_code = None
        self.error_status = None
        # connection successful
        if self.status == 200:
            result = resp.json()
            self.message = result['Message']
            self.error_code = result['ErrorCode']
            self.error_status = result['ErrorStatus']
            # there is data
            if self.error_code == 1:
                # getting response and putting into response member 
                try:
                    self.response = result['Response']
                except Exception as ex:
                    print('ResponseSummary: 200 status and error_code 1, but there was no Response')
                    print('Exception: {ex}  Type: {type}'.format(ex = ex, type = ex.__class__.__name__))
            else:
                # 200 status code, but error code isn't 1
                print('No data returned from endpoint: {url} {error} was the error code with status 200.'.format(url = self.url, error = self.error_code))
        else:
            # didn't read successfully
            print('Error reading from endpoint: {url} Status: {status_code}'.format(url = self.url, status_code = self.status))

"""
This section is the functions which allow you to hook into bungie's public Destiny2 API
All invoke destiny2_api_hook which returns a ResponseWrapper object

To access the data, access ResponseWrapper.response to grab the map/array you need
"""

## function which invokes requests.get() on bungie's public API
def destiny2_api_hook(url):
    return ResponseWrapper(requests.get(url, headers = headers))

## getting current manifest (definitions of hashes)
def get_manifest():
    url = bungie_d2_url + 'Manifest'
    man = destiny2_api_hook(url)
    if man.response:
        return man.response

## function which gets the exact hash keyed definition map from the manifest
## a backend function to run when you need to find out what a hash is mapped to
## doesn't call destiny2_api_hook since this purely reads a json file from the url_def
def get_definitions(manifest, definition_name):
    url_def = 'https://www.bungie.net/' + manifest['jsonWorldComponentContentPaths']['en'][definition_name]
    definitions = requests.get(url_def, headers = headers)
    if definitions.status_code == 200:
        return definitions.json()
    else:
        print('error reading from manifest definitions: ' + url_def)

## returns membershipId correlated with bungie.net name (gamertag#xxxx)
def get_member_id(gamertag):
    url = bungie_d2_url + 'SearchDestinyPlayer/All/{displayName}'.format(displayName = urllib.parse.quote(gamertag))
    memberships = destiny2_api_hook(url)
    if memberships.response:
        return memberships.response[0]['membershipId']

## returns historical stats map (general stats: pvp, patrol, raid, story, strikes, pve competitive [gambit])
def get_historical_stats(memberId, characterId):
    url = bungie_d2_url + "All/Account/{memberId}/Character/{characterId}/Stats".format(memberId = memberId, characterId = characterId)
    historical_stats = destiny2_api_hook(url)
    if historical_stats.response:
        return historical_stats.response

## returns metrics map tracking metrics (anything that emblem trackers can have in-game)
def get_metrics(memberId):
    url = bungie_d2_url + "3/Profile/{memberId}/?components=1100".format(memberId = memberId)
    metrics = destiny2_api_hook(url)
    if metrics.response:
        return metrics.response


"""
functions which make use of responses returned by api hooks above
"""

## generates a general summary of pvp performance
## only data needed is historical stats (general)
## currently displays : Efficiency (K+A/D), K/D and Weapon of Choice
def pvp_summary(historical_stats):
    all_pvp = historical_stats['allPvP']
    if all_pvp:
        all_time = all_pvp['allTime']
        if all_time:
            print('====== PVP SUMMARY ======')
            print('Efficiency: {}'.format(all_time['efficiency']['basic']['displayValue']))
            print('K/D: {}'.format(all_time['killsDeathsRatio']['basic']['displayValue']))
            print('Weapon of Choice: {}'.format(all_time['weaponBestType']['basic']['displayValue']))
            print('===== END PVP SUMMARY =====')


## prints out a raid summary, needs historical stats map and metrics map
## historical stats gives Total Clears, Days Played, and Weapon of Choice
## metrics reports individual Raid clears
def raid_summary(historical_stats, metrics):
    raid = historical_stats['raid']
    if raid:
        all_time = raid['allTime']
        if all_time:
            print('====== RAID SUMMARY =======')
            print('Total Clears: {}'.format(all_time['activitiesCleared']['basic']['displayValue']))
            # yes, we have to access ['metrics']['data']['metrics'] to actually get to the hash keyed progress map
            metrics_actual = metrics['metrics']['data']['metrics']

            # 2506886274 : VoG clears
            print('Vault of Glass Clears: {}'.format(metrics_actual['2506886274']['objectiveProgress']['progress']))
            # 954805812 : DSC clears
            print('Deep Stone Crypt Clears: {}'.format(metrics_actual['954805812']['objectiveProgress']['progress']))
            # 1168279855 : GoS clears
            print('Garden of Salvation Clears: {}'.format(metrics_actual['1168279855']['objectiveProgress']['progress']))
            # 905240985 : LW clears
            print('Last Wish Clears: {}'.format(metrics_actual['905240985']['objectiveProgress']['progress']))
            
            # general stats
            print('Days Played: {}'.format(all_time['secondsPlayed']['basic']['displayValue']))
            print('Weapon of Choice: {}'.format(all_time['weaponBestType']['basic']['displayValue']))
            print('====== END RAID SUMMARY =====')
            
        



    
    


