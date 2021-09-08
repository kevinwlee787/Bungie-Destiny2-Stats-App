from src.bungie_d2_api_work import *

# used for getting hash defs if needed
# loading manifest
# manifest = get_manifest()
# loading metric defs
# destiny_metric_definitions = get_definitions(manifest, 'DestinyMetricDefinition')
# print(destiny_metric_definitions)

# uncomment the line below this to get input
# gamertag = input("Enter your Bungie name (Code with # required!): ")

# comment out this line if you want to hardcore your own bnet name
gamertag = 'Charmander787#5161'

# grabbing the internal memberId based on the Bnet name
memberId = get_member_id(gamertag)

# grabbing historical stats and metrics data
historical_stats = get_historical_stats(memberId, 0)
metrics = get_metrics(memberId)

# generating pvp and raid summaries based on historical_stats and metrics
pvp_summary(historical_stats)
raid_summary(historical_stats, metrics)