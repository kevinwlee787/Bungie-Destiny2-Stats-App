import sys
import pathlib

sys.path.insert(1, str(pathlib.Path().absolute()) + '\\')

from src.bungie_api.bungieD2_api import *

## PyQt5 is a dependency
from PyQt5.QtWidgets import * 
from PyQt5 import QtGui
from PyQt5.QtGui import * 


class MainWindow(QMainWindow):
    """ This class is the application's main window """

    # this is for all characterIds 0
    characterId = 0
  
    def __init__(self):
        super().__init__()
  
        # setting title
        self.setWindowTitle("Destiny 2 Stats App")

        self.setWindowIcon(QtGui.QIcon('.\\images\\tricorn.jpg'))

        # background color 
        # self.setStyleSheet("background-color: grey;")
  
        # setting geometry
        # first 2 args are where the window is generated
        # second two args are length / width respectively
        self.setGeometry(250, 250, 500, 400)
        
        self.line_edit_user = QLineEdit("exampleName#1234", self)

        self.line_edit_user.setGeometry(125, 175, 250, 30)

        self.line_edit_user.returnPressed.connect(self.on_user_name_input)

        self.characterId = 0

        self.manifest = get_manifest()

        self.destiny_class_definitions = get_definitions(self.manifest, 'DestinyClassDefinition')
        self.destiny_record_definitions = get_definitions(self.manifest, 'DestinyRecordDefinition')

        # showing all the widgets
        self.show()

    def on_user_name_input(self):
        """returns void
        
        method first pulls str from line_edit_user
        if its a valid Bungie Net Name (get_player() returns Player obj)
        then displays all current characters + All option 
        """
        user_name = str(self.line_edit_user.text())
        self.player = get_player(user_name)
        
        # if they enter an invalid name, no memberId gets returned out
        if self.player:
            # once the user enters their name, no need for this box anymore
            self.line_edit_user.hide()

            self.character_page = QWidget(self)

            verticalLayout = QVBoxLayout()
            allButton = QPushButton('All', self)
            allButton.setFixedSize(490, 96)
            allButton.clicked.connect(lambda: self.on_all_button_push('0'))
            verticalLayout.addWidget(allButton)

             # characters : 200
            profile = get_profile(self.player, ['200'])
            characters = profile['characters']['data']
            
            for id, character in characters.items():
                ## emblems background are 474 x 96
                # this handles pulling the image from the url and loading it into an Icon
                emblem_url = bungie_net + character['emblemBackgroundPath']
                data = urllib.request.urlopen(emblem_url).read()
                img = QImage()
                img.loadFromData(data)
                pixmap = QPixmap(img)
                icon = QIcon(pixmap)

                # button per character
                button = QPushButton(self)
                button.setIcon(icon)
                button.setIconSize(pixmap.rect().size())
                button.clicked.connect(lambda: self.on_all_button_push(id))

                # labeling each button
                label = QLabel(self)
                characterStr = '{Clss} {Light}'.format(\
                                Clss = self.destiny_class_definitions[str(character['classHash'])]['displayProperties']['name'], \
                                Light = character['light'])
                
                # it's possible to not have a title equipped, have to have light and actual character
                if 'titleRecordHash' in character:
                    characterStr += ' {}'.format(self.destiny_record_definitions[str(character['titleRecordHash'])]['displayProperties']['name'])
                else:
                    characterStr += ' No Title'
                
                label.setText(characterStr)
                
                verticalLayout.addWidget(label)
                verticalLayout.addWidget(button)
            
            self.character_page.setLayout(verticalLayout)

            self.setCentralWidget(self.character_page)
        else:
            self.bad_name_popup = QMessageBox(self)
            self.bad_name_popup.setText("{} not found, try again".format(user_name))
            self.bad_name_popup.setWindowTitle("PlayerNotFound")
            self.bad_name_popup.show()
    
    # action whenever user inputs their userName into QLineEdit
    def on_all_button_push(self, characterId):
        """returns void
        
        displays currently available stats buttons 
        """
        self.characterId = characterId
        self.stats_buttons = QWidget(self)
        button_grid = QGridLayout()
        # instead display 4 buttons: pve, pvp, raid, trials
        self.pve_stats_button = QPushButton("PvE Summary", self)
        self.pve_stats_button.clicked.connect(self.on_pve_button_push)

        self.pvp_stats_button = QPushButton("PvP Summary", self)
        self.pvp_stats_button.clicked.connect(self.on_pvp_button_push)

        self.raid_stats_button = QPushButton("Raid Summary", self)
        self.raid_stats_button.clicked.connect(self.on_raid_button_push)

        self.trials_stats_button = QPushButton("Trials Summary", self)
        self.trials_stats_button.clicked.connect(self.on_trials_button_push)

        # (widget, col, row)
        button_grid.addWidget(self.pvp_stats_button, 0, 0)
        button_grid.addWidget(self.pve_stats_button, 1, 0)
        button_grid.addWidget(self.trials_stats_button, 0, 1)
        button_grid.addWidget(self.raid_stats_button, 1, 1)
        self.stats_buttons.setLayout(button_grid)

        self.setCentralWidget(self.stats_buttons)

    # action for pve_stats_button when pressed signal
    def on_pve_button_push(self):
        """ returns void
        
        using pve_summary, get_historical_stats() to generate pvp dict
        StatsWindow takes in a dict and parses it on construction
        """
        pve_dict = pve_summary(get_historical_stats(self.player, self.characterId))
        self.pve_stat_window = StatsWindow('PvE Stats', 'vangaurd-logo.jpg', pve_dict)
        self.pve_stat_window.show()


    # action for pvp_stats_button when pressed signal
    def on_pvp_button_push(self):
        """ returns void
        
        using pvp_summary(), get_historical_stats() to generate pvp dict
        StatsWindow takes in a dict and parses it on construction
        """
        pvp_dict = pvp_summary(get_historical_stats(self.player, self.characterId))
        self.pvp_stat_window = StatsWindow('PvP Stats', 'crucible-logo.png', pvp_dict)
        self.pvp_stat_window.show()

    # action for raid_stats_button when pressed signal
    def on_raid_button_push(self):
        """ returns void
        
        using raid_summary(), get_historical_stats, and get_profile (componenets = 1100) to generate the raid dict
        StatsWindow takes in a dict and parses it on construction
        """
        raid_dict = raid_summary(get_historical_stats(self.player, self.characterId), get_profile(self.player, components = ['1100']))
        self.raid_stat_window = StatsWindow('Raid Stats', 'raid-logo.jpg', raid_dict)
        self.raid_stat_window.show()
    
    def on_trials_button_push(self):
        """ returns void
        
        using trials_summary, get_historical_stats (with mode = 84 as an arg) and get metrics to generate the trials dict
        StatsWindow takes in a dict and parses it on construction
        """
        trials_dict = trials_summary(get_historical_stats(self.player, self.characterId, groups = ['1'], modes = ['84']), get_profile(self.player, components = ['1100']))
        self.trials_stat_window = StatsWindow("Trials Stats", 'trials-logo.jpg', trials_dict)
        self.trials_stat_window.show()


class StatsWindow(QWidget):
    """ This class represents a window which displays stats gathered from a dict"""

    def __init__(self, name, icon_img, dictionary):
        super().__init__()
        self.setWindowTitle(name)
        self.setGeometry(450, 300, 150, 150)
        self.setWindowIcon(QtGui.QIcon('.\images\{iconFile}'.format(iconFile = icon_img)))

        # QVBoxLayout is a vertical layout
        layout = QVBoxLayout()
        if dictionary:
            for key, val in dictionary.items():
                layout.addWidget(QLabel('{}: {}'.format(key, val)))
        else:
            layout.addWidget(QLabel("No Data Found"))
        
        self.setLayout(layout)
        self.show()

