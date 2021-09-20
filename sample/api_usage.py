import sys
import pathlib

sys.path.insert(1, str(pathlib.Path().absolute()) + '\\')

from src.bungie_api.bungieD2_api import *

""" UNCOMMENT THESE IF YOU WANT TO FIND CERTAIN DEFS FROM THE MANIFEST """
# loading manifest
manifest = get_manifest()

""" Sometimes you only want certain hashes """
##destiny_metric_definitions = get_definitions(manifest, 'DestinyMetricDefinition')
## print(destiny_metric_definitions)

""" these return a map of the hashes into their definitions"""
destiny_class_definitions = get_definitions(manifest, 'DestinyClassDefinition')
destiny_record_definitions = get_definitions(manifest, 'DestinyRecordDefinition')

""" Either hardcode your name or get input """
# gamertag = input("Enter your Bungie name (Code with # required!): ")
gamertag = 'Charmander787#5161'

# grabbing the internal memberId based on the Bnet name
# memberId = get_member_id(gamertag)
player = get_player(gamertag)


# grabbing historical stats and metrics data
# groups: 1 => general
# modes: 84 => TrialsOfOsiris
#        4 => raids
#        5 => allPvP
#        7 => allPvE
# See DestinyActivityModeType for more possible modes to pass in
historical_stats = get_historical_stats(player, 0, groups = ['1'], modes = ['84', '4', '5', '7'])

# 1100 is Metrics data
# 200 is Character data
profile = get_profile(player, components = ['1100', '200'])
characters = profile['characters']['data']

count = 25
# this just gets your first character
hist = get_activity_history(player, next(iter(characters.keys())), count, modes = ['84'])

"""This prints out every current character of the account"""
for characterHash, data in characters.items():
    print('Class: {}'.format(destiny_class_definitions[str(data['classHash'])]['displayProperties']['name']))
    print('Light: {}'.format(data['light']))
    print('Emblem: {}'.format(bungie_net + data['emblemBackgroundPath']))
    Title = 'No Title'
    if 'titleRecordHash' in data:
        Title = str(destiny_record_definitions[str(data['titleRecordHash'])]['displayProperties']['name'])
    print('Title: {}\n'.format(Title))
    

"""generates pvp and raid summaries based on historical_stats and metrics"""
print(summary_to_str(pvp_summary(historical_stats), 'PVP'))
print()
print(summary_to_str(trials_summary(historical_stats, profile), 'TRIALS'))
print()
print(summary_to_str(pve_summary(historical_stats), 'PVE'))
print()
print(summary_to_str(raid_summary(historical_stats, profile), 'RAID'))
print()


""" generates past 100 match summary for trials """
print(summary_to_str(recent_trials_summary(hist), 'Past {} Trials Matches'.format(count)))
print()
