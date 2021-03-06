# Bungie-Destiny2-Stats-App
 This application is intended to access Bungie's Destiny 2 public API and report back player statistics
 
 Back-end communicating with Bungie's API is written in **Python**
 
 Front-end GUI / Application written with the **PyQt5** library
 
 A full requirements.txt file is provided

 ## Setup
 Clone this repo into your own dir
 
 Install dependencies (pip on requirements.txt file)

 ## Running
 Either run the __main__.py file or just run the project dir with **python**

 From there enter your Bungie Net name and you can explore your stats

 If you don't have an account feel free to view mine: Charmander787#5161
 
 ## Extra Info
 
 For those who don't know about Destiny 2: https://www.bungie.net/en-us/
 
 More information and documentation on the Bungie API here: https://bungie-net.github.io/multi/index.html

# 2022 - 4 - 23 Implemented User Input for Recent Stats
Implemented ability for user to decide how many games to analyze (Trials Tab only right now)
Added raid stat tracking for new Witch Queen Raid: Vow of The Disciple

###### For the future
more appealing gui
maybe refactor code

# 2021 - 10 - 12 Implemented Recent Stats for Account
 Implemented comparator used with merge_list on lists pulled from get_activity_history
 Added unit tests for this comparator
 Added recent overall trials stats to the app
 Added recent overall and individual pvp stats to the app
 Added standardized locations where StatsWindows show up (they will be generated corresponding to where the main window is upon clicking a stats button)

 ###### For the future
 Add popular streamers / content creators' bungie tags to the home menu
 more appealing colors / images
 splitting modules up, the bungieD2_api.py module is growing and functions should be split as complexity grows

 # 2021 - 10 - 1 Refactored back - end, added more functions related to handling recent activity
 Added merge_list method which merges 2 (3 optional) sorted lists defined by a comparator, also added unit tests for this function
 Refactored some of the summary functions
 Redesigned front end PyQt5 code. Utilizing QStackedWidget to implement 'back' buttons
 Added recent trials performance alongside overall (Only available per character), considering also adding this for PvP / Crucible as well
 Solved a bug with individual character stats by using functools.partial rather than lambda

 ###### For the future
 Implement comparator for activities so we can get recent match data accountwide (merging all 3 character's lists by time/date)
 Add popular streamers / content creators' bungie tags to the home menu
 Make the app more appealing on the eyes (less grey, black, white; more color)
 split the bungieD2_api.py module into separate modules with better module names

 
 # 2021 - 09 - 20 Restructured project files, More backend and front end features
 Changed get_member_id into get_player as player platform matters and added related Class: player
 Added ability to pull activity history into get_activity_history

 Front end now displays the player's active characters and their respective equipped emblems, light level, and title!
 Goal is to be able to view stats on a per character and overall basis
 Added icons to each tab, images dir is where the raw img files are located
 
 After this commit, gui / application is runnable by either running this project folder or by calling __main__.py
 sample folder contains scripts using the bungie_api package/modules. There are example usages and mainly display using print() statements
 
 ###### For the future
 refining per character stats as some stats seem to be irrelevant
 adding ability to merge activity history to be global
 utilize activity history to display meaningful stats

 # 2021 - 09 - 14 Revised Backend, WIP Front End
 Revised a few of the functions, added docstrings and organized code, WIP Front End developed in Python with PyQt5 library
 
 # 2021 - 09 - 08 First Commit
 Initial Commit, general backend written in python commited, __main__.py provided as example of using functions