import sys
import threading, queue
import asyncio
from time import sleep


from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QPushButton, 
                             QLineEdit, QMessageBox, QAction, QStackedWidget)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5 import QtWidgets, QtCore

from views import SettingsView, GeneralView

from drivers.worker import DriverWorkerObject
   

class App(QMainWindow):
    
    signal_start_background_job = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 simple window - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        
        self.settings_view = SettingsView(self)
        self.general_view = GeneralView(self)

        self.worker = DriverWorkerObject()
        self.thread = QtCore.QThread()
        self.worker.moveToThread(self.thread)
        self.thread.start()

        

        self.signal_start_background_job.connect(self.worker.background_job)
        self.signal_start_background_job.emit()
        


        exchanges = self.settings_view.config['exchange']

        # for i in exchanges:
        #     th = DriverThread(i)
        #     th.start()
        
    
        self.worker.sig_balance.connect(self.general_view.slot_update_tree)
        
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.statusBar().showMessage('Message in statusbar.')

        mainMenu = self.menuBar() 
        settingsMenu = mainMenu.addMenu('Settings')

        apikey_button = QAction(QIcon('exit24.png'), 'API Keys', self)
        apikey_button.setShortcut('Ctrl+K')
        apikey_button.setStatusTip('Setting API Keys')        
        apikey_button.triggered.connect(self.on_settings)
        
        exitButton = QAction(QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)

        settingsMenu.addAction(apikey_button)
        settingsMenu.addAction(exitButton)
        
        
        
        
        self.Stack = QStackedWidget (self)
        self.setCentralWidget(self.Stack)
        
        self.Stack.addWidget (self.general_view)
        self.Stack.addWidget (self.settings_view)        
        self.Stack.setCurrentIndex(0)

        self.settings_view.changedView.connect(self.on_chenge_view)
        

        self.show()

    def on_settings(self):
        self.Stack.setCurrentIndex(1)
    
    @pyqtSlot(int)
    def on_chenge_view(self, value):
        self.Stack.setCurrentIndex(value)



 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
    #[c.join() for c in drivers_list]