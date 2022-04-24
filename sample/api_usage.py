import sys
import pathlib

sys.path.insert(1, str(pathlib.Path().absolute()) + '\\')

from src.bungie_api.bungieD2_api import *

""" UNCOMMENT THESE IF YOU WANT TO FIND CERTAIN DEFS FROM THE MANIFEST """
# loading manifest
manifest = get_manifest()

""" Sometimes you only want certain hashes """
""" Useful for finding hash definitions for metrics"""
#destiny_metric_definitions = get_definitions(manifest, 'DestinyMetricDefinition')
""" Recently used to find hash for Vow of Disciple (new raid) completions """
#print(destiny_metric_definitions['3585185883'])

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

count = 100
it = iter(characters.keys())
# generating history for all 3 characters
# this can be hardcoded as you can have a maximum of 3 characters
trials_1 = get_activity_history(player, next(it), count, modes = ['84'])
trials_2 = get_activity_history(player, next(it), count, modes = ['84'])
trials_3 = get_activity_history(player, next(it), count, modes = ['84'])

hist = merge_list(count, trials_1, trials_2, trials_3, comparator_activity)

it = iter(characters.keys())

count = 25
trials_lists_list = []
pvp_lists_list = []

"""This prints out every current character of the account and generates the recent activity lists"""
for characterHash, data in characters.items():
    print("Character Id: {}".format(characterHash))
    print('Class: {}'.format(destiny_class_definitions[str(data['classHash'])]['displayProperties']['name']))
    print('Light: {}'.format(data['light']))
    print('Emblem: {}'.format(bungie_net + data['emblemBackgroundPath']))
    Title = 'No Title'
    if 'titleRecordHash' in data:
        Title = str(destiny_record_definitions[str(data['titleRecordHash'])]['displayProperties']['name'])
    print('Title: {}\n'.format(Title))

    # recent activity time
    trials_lists_list.append(get_activity_history(player, characterHash, count,  modes = ['84']))
    pvp_lists_list.append(get_activity_history(player, characterHash, count, modes = ['70']))

hist_trials = merge_list(count, trials_lists_list[0], trials_lists_list[1], trials_lists_list[2], comparator_activity)
hist_pvp = merge_list(count, pvp_lists_list[0], pvp_lists_list[1], pvp_lists_list[2], comparator_activity)

""" summary function usages"""
print(summary_to_str(pvp_summary(historical_stats), 'PVP'))
print()

print(summary_to_str(recent_pvp_summary(hist_pvp), 'Past {} Crucible Matches'.format(count)))
print()

print(summary_to_str(trials_summary(historical_stats), 'TRIALS'))
print()

print(summary_to_str(recent_pvp_summary(hist_trials), 'Past {} Trials Matches'.format(count)))
print()

print(summary_to_str(pve_summary(historical_stats), 'PVE'))
print()

print(summary_to_str(raid_summary(historical_stats, profile), 'RAID'))
print()