import json
import threading, queue

from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QPushButton, 
                             QLineEdit, QMessageBox, QAction, QStackedWidget, QTabWidget,
                             QVBoxLayout, QLabel, QHBoxLayout)

from PyQt5.QtCore import Qt, pyqtSignal

from .Ui_APIKeySettings import Ui_APIKeySettings

class SettingsView(QWidget):

    changedView = pyqtSignal(int)

    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        self.config = None

        with open('settings.txt', 'r') as config_file:
            self.config = json.load(config_file)

        for i in self.config['exchange']:
            self.config['exchange'][i]['out_queue'] =  queue.Queue()
            self.config['exchange'][i]['in_queue'] =  queue.Queue()  

        self.ui = Ui_APIKeySettings()
        self.ui.setupUi(self)

        if 'binance' in self.config['exchange']:
            self.ui.binance_apikey.setText(self.config['exchange']['binance']['auth']['apiKey'])
            self.ui.binance_secretkey.setText(self.config['exchange']['binance']['auth']['secret'])
        
        if 'hitbtc' in self.config['exchange']:
            self.ui.hitbtc_apikey.setText(self.config['exchange']['hitbtc']['auth']['apiKey'])
            self.ui.hitbtc_secretkey.setText(self.config['exchange']['hitbtc']['auth']['secret'])
        

        self.ui.pushButton.clicked.connect(self.on_click)
        
    
    #@pyqtSlot()
    def on_click(self):
        buttonReply = QMessageBox.question(self, 'Update and back to home view', 'All changes will be stored loacly to setting file. \n ', 
                                           QMessageBox.Save,  QMessageBox.Close)
        print(int(buttonReply))
        if buttonReply == QMessageBox.Save:

            self.config['exchange']['binance'] = {'auth': {'apiKey': self.ui.binance_apikey.text(),
                                                           'secret': self.ui.binance_secretkey.text()} }
                                                 
            self.config['exchange']['hitbtc'] = {'auth': {'apiKey': self.ui.hitbtc_apikey.text(),
                                                         'secret': self.ui.hitbtc_secretkey.text()}}
                                            

            with open('settings.txt', 'w') as config_file:
                json.dump(self.config, config_file)


            self.changedView.emit(0)
        elif buttonReply == QMessageBox.Close:
            self.changedView.emit(0)
            
    
   
        
    