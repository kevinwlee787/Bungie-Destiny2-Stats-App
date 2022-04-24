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
    """ class representing an api response returned by requests.get()"""
    def __init__(self, resp):
        self.status = resp.status_code
        self.url = resp.url
        ## members which are initialized after .json() is called on the resp returned by requests.get()
        # Note response will be None if the request fails
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
def destiny2_api_hook(url: str) -> ResponseWrapper:
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

    Useful for finding out hashDefinitions

    Arguments:
    manifest -- manifest pulled from get_manifest()
    definition_name -- Definition group you'd like to get from the Manifest
    """
    url_def = 'https://www.bungie.net/' + manifest['jsonWorldComponentContentPaths']['en'][definition_name] + '/'
    definitions = requests.get(url_def, headers = headers)
    # not using destiny2_api_hook since we dont access ['Response']
    if definitions.status_code == 200:
        return definitions.json()
    else:
        print('error reading from manifest definitions: ' + url_def)


class Player:
    """ Class representing a Destiny 2 account
    
    membershipType is platform
    membershipId is unique id required in other api endpoint accesors below
    displayName is player's current Bungie Net name with the #hash appended to it (generated from displayName + # + code)
    """
    def __init__(self, membershipType, membershipId, displayName, code):
        self.membershipType = membershipType
        self.membershipId = membershipId
        self.bungieName = displayName + '#' + str(code)


def get_player(gamertag: str) -> Player:
    """ returns Player obj representing player's acc

    This is an exact match look up

    Arguments:
    gamertag -- player's bungie net global name (ex: exampleName#1234)
    """
    url = bungie_d2_url + 'SearchDestinyPlayer/All/{displayName}/'.format(displayName = urllib.parse.quote(gamertag))
    player = destiny2_api_hook(url)
    if player.response:
        return Player(player.response[0]['membershipType'], player.response[0]['membershipId'], \
            player.response[0]['bungieGlobalDisplayName'], player.response[0]['bungieGlobalDisplayNameCode'])


def get_historical_stats(player: Player, characterId = 0, groups: list = ['1'], modes: list = ['0']):
    """ returns historical stats map from Destiny2.GetHistoricalStats 

    Under default args, general stats are returned only: 
    pvp, patrol, raid, story, strikes, pve competitive [gambit]

    Arguments:
    player -- Player obj generated from get_player()
    characterId -- character of player, default is 0 since 0 pulls from all characters
    groups -- list of group of stats { 1: General, 2: Weapons, 3: Medals}
    modes -- list of modes, see DestinyActivityModeType to see all possible; defualt is {None: 0}
    """
    groups_query_str = ','.join(groups)
    modes_query_str = ','.join(modes)
    url = bungie_d2_url + "All/Account/{memberId}/Character/{characterId}/Stats/?groups={groups}&modes={modes}".format( \
        memberId = player.membershipId, characterId = characterId, groups = groups_query_str, modes = modes_query_str)

    historical_stats = destiny2_api_hook(url)
    if historical_stats.response:
        return historical_stats.response


def get_profile(player: Player, components: list):
    """ returns Destiny Profile information

    Refer to DestinyComponentType enum: https://bungie-net.github.io/multi/schema_Destiny-DestinyComponentType.html
    
    Arguments:
    player -- Player generated from get_player()
    components -- list of components
    """
    compList = ','.join(components)
    url = bungie_d2_url + "{memberType}/Profile/{id}/?components={compList}".format(memberType = player.membershipType, id = player.membershipId, compList = compList)
    profile = destiny2_api_hook(url)
    if profile.response:
        return profile.response


def get_activity_history(player: Player, characterId: int, count = 25, modes: list = ['None'], page = 0) -> list:
    """ returns list of most recent n = count activities
    
    Arguments:
    player -- Player generated by get_player()
    characterId -- characterId (can get from get_profile()), no default as this requires per character
    count -- number of recent activities, default 25
    modes -- default None returns all activity types, otherwise filters based on this arg, see DestinyActivityModeType for possible modes
    page -- page to return, default 0
    """
    modeList = ','.join(modes)
    url = bungie_d2_url + '{type}/Account/{id}/Character/{character}/Stats/Activities/?mode={modes}&page={page}&count={count}'.format(\
        type = player.membershipType, id = player.membershipId, character = characterId, modes = modeList, page = page, count = count)
    
    activities = destiny2_api_hook(url)
    if activities.response:
        # this is a dict, but activities key accesses the list of activities 
        return activities.response['activities']


def comparator_activity(activity1: str, activity2: str) -> bool:
    """ returns True if activity1 > activity2, False otherwise
    
    Used as a comparator for merge lists
    
    Format of the activity strs:
    2021-09-11T05:15:44Z

    YYYY-MM-DDTHH:MM:SS

    Arguments:
    activity1 -- activity from get_activity_history
    activity2 -- activity from get_activity_history
    """
    
    date_time1 = activity1['period'].split('T')
    date_time2 = activity2['period'].split('T')

    date1 = date_time1[0].split('-')
    date2 = date_time2[0].split('-')

    year1 = date1[0]
    year2 = date2[0]

    if year1 > year2:
        return True
    elif year1 < year2:
        return False
    else:
        month1 = date1[1]
        month2 = date2[1]
        if month1 > month2:
            return True
        elif month2 < month1:
            return False
        else:
            day1 = date1[2]
            day2 = date2[2]
            if day1 > day2:
                return True
            elif day1 < day2:
                return False
            else:
                time1 = date_time1[1].split(':')
                time2 = date_time2[1].split(':')

                hour1 = time1[0]
                hour2 = time2[0]

                if hour1 > hour2:
                    return True
                elif hour1 < hour2:
                    return False
                else:
                    minute1 = time1[1]
                    minute2 = time2[1]
                    if minute1 > minute2:
                        return True
                    else:
                        ## no need to check minutes, no way an activity happens at the same minute (Atleast a trials activity)
                        return False
                
##
#  functions which make use of responses returned by api hooks above
#  plan is to separate this into its own module
##

def summary_to_str(stats_summary_dict: dict, name: str) -> str:
    """ returns a string representation of a player's stats summary
    
    Arguments:
    stats_summary_dict -- OrderedDict / Dict generated by a *_summary functions (defined below)
    name -- str, name of the stats being displayed (Example: RAID)
    """
    stats_str = ''
    if stats_summary_dict:
        stats_str = '====== {name} ======\n'.format(name = name)
        for key, val in stats_summary_dict.items():
            stats_str += '{key}: {value}\n'.format(key = key, value = val)
        stats_str += '===== END {name} ====='.format(name = name)
    
    return stats_str

def pvp_summary(historical_stats_general: dict) -> dict:
    """returns an OrderedDict of player's pvp summary

    currently keyed: Efficiency (K+A/D), K/D, and Weapon of Choice

    Arguments:
    historical_stats_general -- historical stats map generated by get_historical_stats() (only general / PvP needed)
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


def pve_summary(historical_stats_general: dict) -> dict:
    """ returns OrderedDict of player's general pve summary
    
    historical stats keys: Activities, Kills, Orbs of Light, Revives, Weapon of Choice, Days Played

    Arguments:
    historical_stats_general -- historical stats map generated by get_historical_stats (only general / PvE needed)
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


def raid_summary(historical_stats_general: dict, metrics: dict = None) -> dict:
    """return a OrderedDict of player's raid summary

    historical stats gives keys: Total Clears, Days Played, and Weapon of Choice
    metrics reports individual Raid clears keys

    Arguments:
    historical_stats_general -- historical stats map generated by get_historical_stats() 
    metrics -- metrics map generated by get_profile() with 1100 as components
    """
    raid = historical_stats_general['raid']
    if raid:
        all_time = raid['allTime']
        if all_time:
            raid_dict = OrderedDict()

            raid_dict['Total Clears'] = all_time['activitiesCleared']['basic']['displayValue']

            if metrics:
                # yes this is the actual access path for getting metrics, why? Ask Bungie
                metrics_actual = metrics['metrics']['data']['metrics']
                # 3585185883 : VoTD clears
                raid_dict['Vow of The Disciple Clears'] = metrics_actual['3585185883']['objectiveProgress']['progress']
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


def trials_summary(historical_stats_trials: dict, metrics: dict = None) -> dict:
    """ returns OrderedDict of all trials statistics: general historical stats, metrics (optional),
    and recent activities from an activity list (optional)

    Arguments:
    historical_stats_trials -- map generated by get_historical_stats with modes = 84 (trials of Osiris)
    metrics -- map generated by get_profile() with components = 1100
    
    """
    trials = historical_stats_trials['trials_of_osiris']
    if trials:
        all_time = trials['allTime']
        if all_time:
            trials_dict = OrderedDict()
            
            ## NOTE: GetHistoricalStats isn't working properly for trials stats
            ## The alternative right now is to pull all historical match history (GetActivityHistory)
            ## and then calculate stats manually with DestinyPostGameCarnageReport (PGCR)
            ## store all of this to a db and then pull / update per memberId as needed
            ## However, this is beyond the scope of this library so hopefully Bungie fixes this endpoint

            trials_dict['K/D'] = all_time['killsDeathsRatio']['basic']['displayValue']
            trials_dict['Efficiency'] = all_time['efficiency']['basic']['displayValue']
            trials_dict['Win Rate'] = str(round(all_time['activitiesWon']['basic']['value'] / all_time['activitiesEntered']['basic']['value'] * 100, 2))
            
            if metrics:
                metrics_actual = metrics['metrics']['data']['metrics']
                # 1765255052 - Flawless Tickets
                trials_dict['Flawless Tickets'] = metrics_actual['1765255052']['objectiveProgress']['progress']
                # 1114483243 - Seasonal Flawless Tickets
                trials_dict['Seasonal Flawless Tickets'] = metrics_actual['1114483243']['objectiveProgress']['progress']
            
            trials_dict['Days Played'] = all_time['secondsPlayed']['basic']['displayValue']
            return trials_dict


def recent_pvp_summary(activity_list: list) -> dict:
    """ returns OrderedDict of recent trials OR pvp statistics
    
    Arguments:
    activity_list -- list of activities generated by get_activity_history on any pvp mode(s)
    """
    if activity_list:
        kills = 0
        # note a defeat counts assists (used for the Efficiency metric)
        defeats = 0
        deaths = 0
        # recording losses as a 1 means a defeat from match 'standing' key
        losses = 0
        for datum in activity_list:
            kills += datum['values']['kills']['basic']['value']
            defeats += datum['values']['opponentsDefeated']['basic']['value']
            deaths += datum['values']['deaths']['basic']['value']
            losses += datum['values']['standing']['basic']['value']

        count = len(activity_list)
        pvp_dict = OrderedDict()
        pvp_dict['Recent KD'] = '{:.2f}'.format(kills / (deaths if deaths != 0 else 1))
        pvp_dict['Recent Efficiency'] = '{:.2f}'.format(defeats / (deaths if deaths != 0 else 1))
        pvp_dict['Recent Win Rate'] = '{:.2f}'.format(((count - losses) / count) * 100)
        return pvp_dict
    
    
def merge_list(n: int, list1: list, list2: list, list3: list, cmp) -> list:
    """ returns a sorted list based on a comparator
    
    The motivation for this is to be able to past in history of up to 3 characters and 
    most recent n activities based on time

    It's possible that the player didn't play all the most recent matches on 1 character and 
    so this function allows you to get a merged list (ie for account rather than general data)

    cmp is a comparator

    Time complexity: O(n); Space complexity: O(n)

    Arguments:
    n -- total size of new list
    list1 -- list generated from get_activity_history or list sorted GREATEST to LEAST
    list2 -- list generated from get_activity_history or list sorted GREATEST to LEAST
    list3 -- list generated from get_activity_history or list sorted GREATEST to LEAST
    cmp -- comparator returning TRUE if arg 1 > arg 2, FALSE otherwise
    """
    merged_list = []

    size_1 = len(list1)
    size_2 = len(list2)
    size_3 = len(list3)

    i = 0
    j = 0
    k = 0
    while i < size_1 and j < size_2 and k < size_3:
        if cmp(list1[i], list2[j]) and cmp(list1[i], list3[k]):
            merged_list.append(list1[i])
            i += 1
        elif cmp(list2[j], list1[i]) and cmp(list2[j], list3[k]):
            merged_list.append(list2[j])
            j += 1
        else:
            merged_list.append(list3[k])
            k += 1
        
        n -= 1
        if n == 0:
            return merged_list
    
    if i == size_1:
        while j < size_2 and k < size_3:
            if cmp(list2[j], list3[k]):
                merged_list.append(list2[j])
                j += 1
            else:
                merged_list.append(list3[k])
                k += 1
            
            n -= 1
            if n == 0:
                return merged_list
        
        merged_list = merged_list + list2[j:] + list3[k:]
    elif j == size_2:
        while i < size_1 and k < size_3:
            if cmp(list1[i], list3[k]):
                merged_list.append(list1[i])
                i += 1
            else:
                merged_list.append(list3[k])
                k += 1

            n -= 1
            if n == 0:
                return merged_list
            
        merged_list = merged_list + list1[i:] + list3[k:]
    else:
        while i < size_1 and j < size_2:
            if cmp(list1[i], list2[j]):
                merged_list.append(list1[i])
                i += 1
            else:
                merged_list.append(list2[j])
                j += 1

            n -= 1
            if n == 0:
                return merged_list

        merged_list = merged_list + list1[i:] + list2[j:]

    return merged_list
