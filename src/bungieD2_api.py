import requests
import urllib.parse

from collections import OrderedDict

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

##
# This section is the functions which allow you to hook into bungie's public Destiny2 API
# All invoke destiny2_api_hook which returns a ResponseWrapper object

# To access the data, access ResponseWrapper.response to grab the map/array you need
##

## function which invokes requests.get() on bungie's public API
def destiny2_api_hook(url):
    """ returns ResponseWrapper object generated from requests.get()

    this function is the main function of this module, allows you to connect to any
    of Bungie's Destiny 2 API endpoints provided url is a valid endpoint

    Arguments:
    url -- endpoint url you'd like to read from
    """
    return ResponseWrapper(requests.get(url, headers = headers))


def get_manifest():
    """ returns current manifest"""
    url = bungie_d2_url + 'Manifest/'
    man = destiny2_api_hook(url)
    if man.response:
        return man.response


def get_definitions(manifest, definition_name):
    """ returns map of hash keyed definition map 

    Can be useful for finding what hashes are mapped to (printing them to console and ctrl F)

    Arguments:
    manifest -- manifest pulled from get_manifest()
    definition_name -- Definition group you'd like to get from the Manifest
    """
    url_def = 'https://www.bungie.net/' + manifest['jsonWorldComponentContentPaths']['en'][definition_name] + '/'
    definitions = requests.get(url_def, headers = headers)
    if definitions.status_code == 200:
        return definitions.json()
    else:
        print('error reading from manifest definitions: ' + url_def)


def get_member_id(gamertag):
    """ returns int representing player's internal membershipId

    This is an exact match look up

    Arguments:
    gamertag -- player's bungie net global name (ex: exampleName#1234)
    """
    url = bungie_d2_url + 'SearchDestinyPlayer/All/{displayName}/'.format(displayName = urllib.parse.quote(gamertag))
    memberships = destiny2_api_hook(url)
    if memberships.response:
        return memberships.response[0]['membershipId']


def get_historical_stats(memberId, characterId, groups = [], modes = []):
    """ returns historical stats map (general stats)

    general stats: pvp, patrol, raid, story, strikes, pve competitive [gambit]

    Arguments:
    memberId -- players memberId generated from get_member_id()
    characterId -- character of player (3 possible), 0 is all characters combined
    TODO: implement way to get characterIds into this library, could be useful for viewing stat comparisons across characters
    """
    groups_query_str = ','.join(groups)
    modes_query_str = ','.join(modes)
    url = bungie_d2_url + "All/Account/{memberId}/Character/{characterId}/Stats/?groups={groups}&modes={modes}".format( \
        memberId = memberId, characterId = characterId, groups = groups_query_str, modes = modes_query_str)

    historical_stats = destiny2_api_hook(url)
    if historical_stats.response:
        return historical_stats.response


def get_metrics(memberId):
    """returns metrics map tracking metrics

    anything that in-game emblem trackers track will be in metrics

    Arguments:
    memberId -- players memberId generated from get_member_id()
    """
    # 1100 is metrics
    # check API docs for more possible args to GetProfile 
    # possibly rewriting this to get_profile and allowing tuple args in the future
    url = bungie_d2_url + "3/Profile/{memberId}/?components=1100".format(memberId = memberId)
    metrics = destiny2_api_hook(url)
    if metrics.response:
        return metrics.response


##
#  functions which make use of responses returned by api hooks above
##

def summary_to_str(stats_summary_dict, name):
    """ returns a string representation of a player's stats summary
    
    Arguments:
    stats_summary_dict -- OrderedDict / Dict generated by a *_summary functions (defined below)
    name -- str, name of the stats being displayed (Example: RAID)
    """
    stats_str = ''
    if stats_summary_dict:
        stats_str = '====== {name} ======'.format(name = name)
        for key, val in stats_summary_dict.items():
            stats_str += '{key}: {value}\n'.format(key = key, value = val)
        stats_str += '===== END {name} ====='.format(name = name)
    
    return stats_str


def pvp_summary(historical_stats_general):
    """returns an OrderedDict of player's pvp summary

    currently keyed: Efficiency (K+A/D), K/D, and Weapon of Choice

    Arguments:
    historical_stats)general -- historical stats map generated by get_historical_stats() (only general)
    """
    all_pvp = historical_stats_general['allPvP']
    if all_pvp:
        all_time = all_pvp['allTime']
        if all_time:
            pvp_dict = OrderedDict()
            pvp_dict['Efficiency'] = all_time['efficiency']['basic']['displayValue']
            pvp_dict['K/D'] = all_time['killsDeathsRatio']['basic']['displayValue']
            pvp_dict['Weapon of Choice'] = all_time['weaponBestType']['basic']['displayValue']
            return pvp_dict


def pve_summary(historical_stats_general):
    """ returns OrderedDict of player's general pve summary
    
    historical stats keys: Activities, Kills, Orbs of Light, Revives, Weapon of Choice, Days Played

    Arguments:
    historical_stats_general -- historical stats map generated by get_historical_stats (general / PvE)
    """
    all_pve = historical_stats_general['allPvE']
    if all_pve:
        all_time = all_pve['allTime']
        if all_time:
            pve_dict = OrderedDict()
            pve_dict['Activities'] = all_time['activitiesEntered']['basic']['displayValue']
            pve_dict['Kills'] = all_time['kills']['basic']['displayValue']
            pve_dict['Orbs of Light'] = all_time['orbsDropped']['basic']['displayValue']
            pve_dict['Revives'] = all_time['resurrectionsPerformed']['basic']['displayValue']
            pve_dict['Weapon of Choice'] = all_time['weaponBestType']['basic']['displayValue']
            pve_dict['Days Played'] = all_time['secondsPlayed']['basic']['displayValue']
            return pve_dict



def raid_summary(historical_stats_general, metrics):
    """return a OrderedDict of player's raid summary

    historical stats gives keys: Total Clears, Days Played, and Weapon of Choice
    metrics reports individual Raid clears keys

    Arguments:
    historical_stats_general -- historical stats map generated by get_historical_stats() 
    metrics -- metrics map generated by get_metrics() [currently, this function name might change in the future]
    """
    raid = historical_stats_general['raid']
    if raid:
        all_time = raid['allTime']
        if all_time:
            raid_dict = OrderedDict()
            # yes this is the actual access path for getting metrics, why? Ask Bungie
            metrics_actual = metrics['metrics']['data']['metrics']

            raid_dict['Total Clears'] = all_time['activitiesCleared']['basic']['displayValue']
            # 2506886274 : VoG clears
            raid_dict['Vault of Glass Clears'] = metrics_actual['2506886274']['objectiveProgress']['progress']
            # 954805812 : DSC clears
            raid_dict['Deep Stone Crypt Clears'] = metrics_actual['954805812']['objectiveProgress']['progress']
            # 1168279855 : GoS clears
            raid_dict['Garden of Salvation Clears'] = metrics_actual['1168279855']['objectiveProgress']['progress']
            # 905240985 : LW clears
            raid_dict['Last Wish Clears'] = metrics_actual['905240985']['objectiveProgress']['progress']

            raid_dict['Weapon of Choice'] = all_time['weaponBestType']['basic']['displayValue']
            raid_dict['Days Played'] = all_time['secondsPlayed']['basic']['displayValue']
            return raid_dict


def trials_summary(historical_stats_trials, metrics):
    """returns an OrderedDict of player's Trials of Osiris (not Trials of Nine) summary

    metrics keys: Flawless Tickets, Seasonal Flawless Tickets
    historical stats keys: Efficiency (K+A/D), K/D, Weapon of Choice, Days Played\

    Arguments:
    historical_stats_trials -- map generated by get_historical_stats with modes = 84 (trials of Osiris)
    metrics -- map generated by get_metrics()
    """
    trials = historical_stats_trials['trials_of_osiris']
    if trials:
        all_time = trials['allTime']
        if all_time:
            trials_dict = OrderedDict()
            metrics_actual = metrics['metrics']['data']['metrics']

            ## NOTE: GetHistoricalStats isn't working properly for trials stats
            ## The alternative right now is to pull all historical match history (GetActivityHistory)
            ## and then calculate stats manually with DestinyPostGameCarnageReport (PGCR)
            ## store all of this to a db and then pull / update per memberId as needed
            ## However, this is beyond the scope of this library so hopefully Bungie fixes this endpoint

            trials_dict['K/D'] = all_time['killsDeathsRatio']['basic']['displayValue']
            trials_dict['Efficiency'] = all_time['efficiency']['basic']['displayValue']
            trials_dict['Win Rate'] = str(round(all_time['activitiesWon']['basic']['value'] / all_time['activitiesEntered']['basic']['value'] * 100, 2))

            # 1765255052 - Flawless Tickets
            trials_dict['Flawless Tickets'] = metrics_actual['1765255052']['objectiveProgress']['progress']
            # 1114483243 - Seasonal Flawless Tickets
            trials_dict['Seasonal Flawless Tickets'] = metrics_actual['1114483243']['objectiveProgress']['progress']
            trials_dict['Days Played'] = all_time['secondsPlayed']['basic']['displayValue']
            return trials_dict

