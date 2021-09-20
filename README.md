# Bungie-Destiny2-Stats-App
 This application is intended to access Bungie's Destiny 2 public API and report back player statistics
 
 Back-end communicating with Bungie's API is written in **Python**
 
 Front-end GUI / Application written in **PyQt5**
 
 A full requirements.txt file is provided

 Setup:
 Download all files + dependecies (pip)

 Running:
 Either run the __main__.py file or just run the project with python

 From there enter your Bungie Net name and you can explore your stats

 If you don't have an account feel free to mine: Charmander787#5161

 In the future I will be adding the ability to look at top content creator / streamer's stats
 
 For those who don't know about Destiny 2: https://www.bungie.net/en-us/
 
 More information and documentation on the Bungie API here: https://bungie-net.github.io/multi/index.html
 
 # 2021 - 09 - 20 Restructured project files, More backend and front end features
 Changed get_member_id into get_player as player platform matters and added related Class: player
 Added ability to pull activity history into get_activity_history

 Front end now displays the player's active characters and their respective equipped emblems, light level, and title!
 Goal is to be able to view stats on a per character and overall basis
 Added icons to each tab, images dir is where the raw img files are located
 
 After this commit, gui / application is runnable by either running this project folder or by calling __main__.py
 sample folder contains scripts using the bungie_api package/modules. They are example usages and mainly display using print() statements
 
 For the future: 
 refining per character stats as some stats seem to be irrelevant
 adding ability to merge activity history to be global
 utilize activity history to display meaningful stats

 # 2021 - 09 - 14 Revised Backend, WIP Front End
 Revised a few of the functions, added docstrings and organized code, WIP Front End developed in Python with PyQt5 library
 
 # 2021 - 09 - 08 First Commit
 Initial Commit, general backend written in python commited, __main__.py provided as example of using functions