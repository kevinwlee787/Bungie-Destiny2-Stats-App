# importing own module
from bungie_d2_api_work import *

import sys

## PyQt5 is a dependency
from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 


class MainWindow(QMainWindow):
    """ This class is the application's main window """
    ## storing necessary data for whichever user logs into the app
    _user_name = ''
    _member_id = ''
  
    def __init__(self):
        super().__init__()
  
        # setting title
        self.setWindowTitle("Destiny 2 Stats App")

        # background color 
        # self.setStyleSheet("background-color: grey;")
  
        # setting geometry
        # first 2 args are where the window is generated
        # second two args are length / width respectively
        self.setGeometry(250, 250, 500, 400)

        self.line_edit_user = QLineEdit("exampleName#1234", self)

        self.line_edit_user.setGeometry(125, 175, 250, 30)

        self.line_edit_user.returnPressed.connect(self.on_user_name_input)

        # showing all the widgets
        self.show()

    # action whenever user inputs their userName into QLineEdit
    def on_user_name_input(self):
        """returns void
        
        function first pulls str from line_edit_user
        if its a valid Bungie Net Name (get_member_id returns only if valid id)
        then displays currently available stats buttons 
        """
        self._user_name = str(self.line_edit_user.text())
        self._member_id = get_member_id(self._user_name)
            
        # if they enter an invalid name, no memberId gets returned out
        if self._member_id:
            # once the user enters their name, no need for this box anymore
            self.line_edit_user.hide()
            
            
            # instead display 4 buttons: pve, pvp, raid, trials
            self.pve_stats_button = QPushButton("PvE Summary", self)
            self.pve_stats_button.setGeometry(125, 15, 250, 50)
            self.pve_stats_button.clicked.connect(self.on_pve_button_push)

            self.pvp_stats_button = QPushButton("PvP Summary", self)
            self.pvp_stats_button.setGeometry(125, 115, 250 , 50)
            self.pvp_stats_button.clicked.connect(self.on_pvp_button_push)

            self.raid_stats_button = QPushButton("Raid Summary", self)
            self.raid_stats_button.setGeometry(125, 215, 250, 50)
            self.raid_stats_button.clicked.connect(self.on_raid_button_push)

            self.trials_stats_button = QPushButton("Trials Summary", self)
            self.trials_stats_button.setGeometry(125, 315, 250, 50)
            self.trials_stats_button.clicked.connect(self.on_trials_button_push)

            self.pve_stats_button.show()
            self.pvp_stats_button.show()
            self.raid_stats_button.show()
            self.trials_stats_button.show()
        else:
            self.bad_name_popup = QMessageBox(self)
            self.bad_name_popup.setText("{} not found, try again".format(self._user_name))
            self.bad_name_popup.setWindowTitle("PlayerNotFound")
            self.bad_name_popup.show()

    # action for pve_stats_button when pressed signal
    def on_pve_button_push(self):
        """ returns void
        
        using pve_summary, get_historical_stats() to generate pvp dict
        StatsWindow takes in a dict and parses it on construction
        """
        pve_dict = pve_summary(get_historical_stats(self._member_id, 0))
        self.pve_stat_window = StatsWindow("PvE Stats", pve_dict)
        self.pve_stat_window.show()


    # action for pvp_stats_button when pressed signal
    def on_pvp_button_push(self):
        """ returns void
        
        using pvp_summary(), get_historical_stats() to generate pvp dict
        StatsWindow takes in a dict and parses it on construction
        """
        pvp_dict = pvp_summary(get_historical_stats(self._member_id, 0))
        self.pvp_stat_window = StatsWindow("PvP Stats", pvp_dict)
        self.pvp_stat_window.show()

    # action for raid_stats_button when pressed signal
    def on_raid_button_push(self):
        """ returns void
        
        using raid_summary(), get_historical_stats, and get_metrics to generate the raid dict
        StatsWindow takes in a dict and parses it on construction
        """
        raid_dict = raid_summary(get_historical_stats(self._member_id, 0), get_metrics(self._member_id))
        self.raid_stat_window = StatsWindow("Raid Stats", raid_dict)
        self.raid_stat_window.show()
    
    def on_trials_button_push(self):
        """ returns void
        
        using trials_summary, get_historical_stats (with mode = 84 as an arg) and get metrics to generate the trials dict
        StatsWindow takes in a dict and parses it on construction
        """
        trials_dict = trials_summary(get_historical_stats(self._member_id, 0, groups = ['1'], modes = ['84']), get_metrics(self._member_id))
        self.trials_stat_window = StatsWindow("Trials Stats", trials_dict)
        self.trials_stat_window.show()


class StatsWindow(QWidget):
    """ This class represents a window which displays stats gathered from a dict"""

    def __init__(self, name, dictionary):
        super().__init__()
        self.setWindowTitle(name)
        self.setGeometry(450, 300, 150, 150)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # QVBoxLayout is a vertical layout
        layout = QVBoxLayout()
        if dictionary:
            for key, val in dictionary.items():
                layout.addWidget(QLabel('{}: {}'.format(key, val)))
        else:
            layout.addWidget(QLabel("No Data Found"))
        
        self.setLayout(layout)
        self.show()

            
  
# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
window = MainWindow()

# start the app
sys.exit(App.exec())