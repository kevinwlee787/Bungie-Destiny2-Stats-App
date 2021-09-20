import sys

from src.application import gui as d2app

from PyQt5.QtWidgets import QApplication

# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
window = d2app.MainWindow()

# start the app
sys.exit(App.exec())