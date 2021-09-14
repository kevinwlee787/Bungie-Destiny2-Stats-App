from src.bungieD2_api import *

## UNCOMMENT THESE IF YOU WANT TO FIND CERTAIN DEFS FROM THE MANIFEST
# used for getting hash defs if needed
# loading manifest
## manifest = get_manifest()
# loading metric defs
## destiny_metric_definitions = get_definitions(manifest, 'DestinyMetricDefinition')
## print(destiny_metric_definitions)

# uncomment the line below this to get input
# gamertag = input("Enter your Bungie name (Code with # required!): ")

# comment out this line if you want to hardcode your own bnet name
gamertag = 'Charmander787#5161'

# grabbing the internal memberId based on the Bnet name
memberId = get_member_id(gamertag)

# grabbing historical stats and metrics data
# groups: 1 => general
# modes: 84 => TrialsOfOsiris
#        4 => raids
#        5 => allPvP
#        7 => allPvE
# See DestinyActivityModeType for more possible modes to pass in
historical_stats = get_historical_stats(memberId, 0, groups = ['1'], modes = ['84', '4', '5', '7'])
metrics = get_metrics(memberId)

# generating pvp and raid summaries based on historical_stats and metrics
print(summary_to_str(pvp_summary(historical_stats), 'PVP'))
print(summary_to_str(trials_summary(historical_stats, metrics), 'TRIALS'))
print(summary_to_str(pve_summary(historical_stats), 'PVE'))
print(summary_to_str(raid_summary(historical_stats, metrics), 'RAID'))
