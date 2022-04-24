import sys
import pathlib

sys.path.insert(1, str(pathlib.Path().absolute()) + '\\')

from src.bungie_api.bungieD2_api import *

## PyQt5 is a dependency
from PyQt5 import QtCore
from PyQt5.QtWidgets import * 
from PyQt5 import QtGui
from PyQt5.QtGui import * 
from PyQt5 import QtCore

from functools import partial

class ApplicationGui(QWidget):

    # 0 is default (ALL)
    characterId = 0
    # list of characters, will be loaded in on_user_name_input
    characters = None

    def __init__(self):
        super().__init__()

        # needed for some Class and Record defs, loading them on app startup
        self.manifest = get_manifest()
        self.destiny_class_definitions = get_definitions(self.manifest, 'DestinyClassDefinition')
        self.destiny_record_definitions = get_definitions(self.manifest, 'DestinyRecordDefinition')

        # name + app icon
        self.setWindowTitle("Destiny 2 Stats App")
        self.setWindowIcon(QtGui.QIcon('.\\images\\tricorn.jpg'))
  
        # 500 x 400 window initially
        # first 2 args are where the window is generated (This is overwritten below)
        # second two args are length / width respectively
        self.setGeometry(250, 250, 500, 400)
        
        # Center of screen
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # QStackedWidget as we will be using pages here
        self.Stack = QStackedWidget(self)
        self.init_user_name_input()

        # using a Grid Layout to put the widgets in the center
        single = QGridLayout(self)
        single.addWidget(self.Stack, 0, 0, alignment = QtCore.Qt.AlignCenter)
        self.setLayout(single)

        # showing all widgets
        self.show()
    
    def init_user_name_input(self):
        """ returns void
        
        method creates the QLineEdit for user input
        once user name inputted, redirects to on_user_name_input() method
        """
        self.user_input = QLineEdit("exampleName#1234", self)
        self.user_input.setFixedSize(250, 30)
        self.user_input.returnPressed.connect(self.on_user_name_input)
        
        self.Stack.addWidget(self.user_input)

    def on_user_name_input(self):
        """returns void
        
        method first pulls str from line_edit_user
        if its a valid Bungie Net Name (get_player() returns Player obj)
        then displays all current characters + All option 
        """
        user_name = str(self.user_input.text())
        self.player = get_player(user_name)

        if self.player:
            self.character_select = QWidget(self)
            verticalLayout = QVBoxLayout()

            allButton = QPushButton('All', self)
            allButton.setFixedSize(490, 96)
            allButton.clicked.connect(lambda: self.on_character_select('0'))
            verticalLayout.addWidget(allButton)

             # characters : 200
            profile = get_profile(self.player, ['200'])
            self.characters = profile['characters']['data']
            
            for id, character in self.characters.items():
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
                button.clicked.connect(partial(self.on_character_select, id))

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

            backLabel = QLabel("Back to Main Menu", self)
            backButton = QPushButton('Back', self)
            backButton.setFixedSize(490, 96)
            backButton.clicked.connect(self.go_back_username)
            verticalLayout.addWidget(backLabel)
            verticalLayout.addWidget(backButton)

            self.character_select.setLayout(verticalLayout)

            self.Stack.addWidget(self.character_select)
            self.Stack.setCurrentIndex(self.Stack.currentIndex() + 1)
            self.setFixedSize(self.Stack.sizeHint().width() + 22, self.Stack.sizeHint().height() + 22)
        else:
            self.bad_name_popup = QMessageBox(self)
            self.bad_name_popup.setText("{} not found, try again".format(user_name))
            self.bad_name_popup.setWindowTitle("PlayerNotFound")
            self.bad_name_popup.show()
    
    def on_character_select(self, id):
        """returns void
        
        generates a 2x2 grid formatted widget:
        pvp pvp
        trials raid

        Arguments:
        id -- id hash of specific character, 0 if for all characters 
        """
        self.characterId = id
        # 4 buttons: pve, pvp, raid, trials
        self.pve_stats_button = QPushButton("PvE Summary", self)
        self.pve_stats_button.setFixedSize(150, 150)
        self.pve_stats_button.clicked.connect(self.on_pve_button_push)

        self.pvp_stats_button = QPushButton("PvP Summary", self)
        self.pvp_stats_button.setFixedSize(150, 150)
        self.pvp_stats_button.clicked.connect(self.on_pvp_button_push)

        self.raid_stats_button = QPushButton("Raid Summary", self)
        self.raid_stats_button.setFixedSize(150, 150)
        self.raid_stats_button.clicked.connect(self.on_raid_button_push)
        
        self.trials_stats_button = QPushButton("Trials Summary", self)
        self.trials_stats_button.setFixedSize(150, 150)
        self.trials_stats_button.clicked.connect(self.on_trials_button_push)


        self.stats_buttons = QWidget(self)
        button_grid = QGridLayout()
        # (widget, col, row)
        button_grid.addWidget(self.pvp_stats_button, 0, 0)
        button_grid.addWidget(self.pve_stats_button, 1, 0)
        button_grid.addWidget(self.trials_stats_button, 0, 1)
        button_grid.addWidget(self.raid_stats_button, 1, 1)
        self.stats_buttons.setLayout(button_grid)

        verticalLayout = QVBoxLayout()
        self.buttons = QWidget()

        back = QPushButton("Back", self)
        back.clicked.connect(self.go_back_character_select)

        verticalLayout.addWidget(back)
        verticalLayout.addWidget(self.stats_buttons)

        self.buttons.setLayout(verticalLayout)
        
        self.Stack.addWidget(self.buttons)
        self.Stack.setCurrentIndex(self.Stack.currentIndex() + 1)

        self.setFixedSize(500, 400)


     # action for pve_stats_button when pressed signal
    def on_pve_button_push(self):
        """ returns void
        
        using pve_summary, get_historical_stats() to generate pvp dict
        StatsWindow takes in a dict and parses it on construction
        """
        pve_dict = pve_summary(get_historical_stats(self.player, self.characterId))
        
        self.pve_stat_window = StatsWindow('PvE Stats', 'vangaurd-logo.jpg', pve_dict)
        self.pve_stat_window.move(self.x() - 270, self.y() + 250)
        self.pve_stat_window.show()


    # action for pvp_stats_button when pressed signal
    def on_pvp_button_push(self):
        """ returns void
        
        using pvp_summary(), get_historical_stats() to generate pvp dict
        StatsWindow takes in a dict and parses it on construction
        """
        pvp_dict = pvp_summary(get_historical_stats(self.player, self.characterId))
        if self.characterId == '0':
            it = iter(self.characters.keys())
            # 70 is all quickplay modes
            hist1 = get_activity_history(self.player, next(it), 100, modes = ['70'])
            hist2 = get_activity_history(self.player, next(it), 100, modes = ['70'])
            hist3 = get_activity_history(self.player, next(it), 100, modes = ['70'])
            pvp_recent_dict = recent_pvp_summary(merge_list(100, hist1, hist2, hist3, comparator_activity))
        else:
            pvp_recent_dict = recent_pvp_summary(get_activity_history(self.player, self.characterId, 100, modes = ['70']))

        
        self.pvp_stat_window = StatsWindow('PvP Stats', 'crucible-logo.png', pvp_dict)
        self.pvp_stat_window.move(self.x() - 270, self.y() - 40)
        self.pvp_stat_window.show()

        self.pvp_stat_window_recent = StatsWindow('PvP Recent Stats', 'crucible-logo.png', pvp_recent_dict)
        self.pvp_stat_window_recent.move(self.x() - 520, self.y() - 40)
        self.pvp_stat_window_recent.show()

    # action for raid_stats_button when pressed signal
    def on_raid_button_push(self):
        """ returns void
        
        using raid_summary(), get_historical_stats, and get_profile (componenets = 1100) to generate the raid dict
        StatsWindow takes in a dict and parses it on construction
        """
        if self.characterId == '0':
            raid_dict = raid_summary(get_historical_stats(self.player, self.characterId), get_profile(self.player, components = ['1100']))
        else:
            raid_dict = raid_summary(get_historical_stats(self.player, self.characterId))
        
        self.raid_stat_window = StatsWindow('Raid Stats', 'raid-logo.jpg', raid_dict)
        self.raid_stat_window.move(self.x() + 520, self.y() + 250)
        self.raid_stat_window.show()

    
    def on_trials_button_push(self):
        """ returns void
        
        using trials_summary, get_historical_stats (with mode = 84 as an arg) and get metrics to generate the trials dict
        StatsWindow takes in a dict and parses it on construction
        """
        # 1 is general stats
        groups = ['1']
        trials = ['TrialsOfOsiris']

        if self.characterId == '0':
            trials_dict = trials_summary(get_historical_stats(self.player, self.characterId, groups, modes = trials), get_profile(self.player, components = ['1100']))
        else:
            trials_dict = trials_summary(get_historical_stats(self.player, self.characterId, groups, modes = trials))
    
        self.trials_stat_window = StatsWindow("Trials Stats", 'trials-logo.jpg', trials_dict)
        self.trials_stat_window.move(self.x() + 520, self.y() - 40)
        self.trials_stat_window.show()

        self.recent_number_input = RecentStatsWindow("Recent Trials", 'trials-logo.jpg', \
            self.player, self.characterId, self.characters.keys(), groups, modes = trials)
        self.recent_number_input.move(self.x() + 770, self.y() - 40)
        self.recent_number_input.show()

    ## methods for going back buttons
    def go_back_username(self):
        """ returns void
        
        used on the character select page to go back to the main user name input menu
        """
        
        self.Stack.setCurrentIndex(self.Stack.currentIndex() - 1)
        toDel = self.Stack.widget(self.Stack.currentIndex() + 1)
        self.Stack.removeWidget(toDel)

        self.setFixedSize(500, 400)
        self.Stack.move(125, 175)

    def go_back_character_select(self):
        """ returns void

        used on stats page to go back to the character select menu
        """
        self.Stack.setCurrentIndex(self.Stack.currentIndex() - 1)
        toDel = self.Stack.widget(self.Stack.currentIndex() + 1)
        self.Stack.removeWidget(toDel)

        self.setFixedSize(self.Stack.sizeHint().width() + 22, self.Stack.sizeHint().height() + 22)

    
class StatsWindow(QWidget):
    """ This class represents a window which displays stats gathered from a dict"""

    def __init__(self, name, icon_img, dictionary):
        super().__init__()

        self.setWindowTitle(name)
        self.setGeometry(450, 300, 250, 250)
        self.setWindowIcon(QtGui.QIcon('.\images\{iconFile}'.format(iconFile = icon_img)))
        # QVBoxLayout is a vertical layout
        layout = QVBoxLayout()
        if dictionary:
            for key, val in dictionary.items():
                lab = QLabel('{}: {}'.format(key, val), self)
                lab.setFont(QFont("Terminal", 8))
                layout.addWidget(lab)
        else:
            layout.addWidget(QLabel("No Data Found", self))
        
        self.setLayout(layout)
        
        self.show()

    def on_number_input(self):
        num = int(self.input.text())
        trials = ['TrialsOfOsiris']

        if self.characterId == '0':
            # for account wide, we need to merge history
            it = iter(self.characters)
            # adding a +1 because api is wrongly reporting the final game, so just tossing it out here.
            hist_1 = get_activity_history(self.player, next(it), num + 1, modes = trials)
            hist_2 = get_activity_history(self.player, next(it), num + 1, modes = trials)
            hist_3 = get_activity_history(self.player, next(it), num + 1, modes = trials)
            trials_recent_dict = recent_pvp_summary(merge_list(num, hist_1, hist_2, hist_3, comparator_activity))
        else:
            # slicing off last element because again, api is bugged
            trials_recent_dict = recent_pvp_summary(get_activity_history(self.player, self.characterId, count = num + 1, modes = trials)[:-1])

        self.statsWindow = StatsWindow("Recent Trials", 'trials-logo.jpg', trials_recent_dict)
        self.statsWindow.show()   


class RecentStatsWindow(QMainWindow):
    """ This class represents a widget which takes an integer input in to determine how many recent matches to analyze """
    def __init__(self, name, icon_img, player, characterId, characters, groups, modes):
        super().__init__()

        self.player = player
        self.characterId = characterId
        self.characters = characters
        self.groups = groups
        self.modes = modes

        window_size = QtCore.QSize(250, 250)
        self.setWindowTitle(name)
        self.setGeometry(0, 0, window_size.width(), window_size.height())
        self.setWindowIcon(QtGui.QIcon('.\images\{iconFile}'.format(iconFile = icon_img)))

        self.Stack = QStackedWidget(self)

        input_size = QtCore.QSize(100, 26)
        default_number = '7'
        self.input = QLineEdit(default_number, self)
        #self.input.setBaseSize(input_size)
        self.input.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.input.returnPressed.connect(self.on_number_input)

        self.Stack.addWidget(self.input)
        self.Stack.move((window_size.width() - input_size.width()) / 2, (window_size.height() - input_size.height()) / 2)

        self.show()

    def on_number_input(self):
        num = int(self.input.text())
        trials = ['TrialsOfOsiris']

        if (self.characterId == '0'):
            # for account wide, we need to merge history
            it = iter(self.characters)
            # adding a +1 because api is wrongly reporting the final game, so just tossing it out here.
            hist_1 = get_activity_history(self.player, next(it), num + 1, modes = trials)
            hist_2 = get_activity_history(self.player, next(it), num + 1, modes = trials)
            hist_3 = get_activity_history(self.player, next(it), num + 1, modes = trials)
            trials_recent_dict = recent_pvp_summary(merge_list(num, hist_1, hist_2, hist_3, comparator_activity))
        else:
            trials_recent_dict = recent_pvp_summary(get_activity_history(self.player, self.characterId, count = num, modes = trials))

        statsWindow = StatsWindow("Recent Trials", 'trials-logo.jpg', trials_recent_dict)
        self.Stack.addWidget(statsWindow)
        self.Stack.setCurrentIndex(self.Stack.currentIndex() + 1)
        self.Stack.setFixedSize(250, 250)
        self.Stack.move(0, 0)