
import json

from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QPushButton, 
                             QLineEdit, QMessageBox, QAction, QStackedWidget, QLabel)

from PyQt5.QtGui import QStandardItemModel, QStandardItem

from PyQt5.QtCore import (pyqtSlot, QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt, QTime, pyqtSlot,
                         QObject)


from .Ui_AggrPortfolioView import Ui_AggrPortfolioView

class GeneralView(QWidget):

    def __init__(self,parent=None):
        super().__init__()

        self.ui = Ui_AggrPortfolioView()
        self.ui.setupUi(self)

        self.ui.treeView.setRootIsDecorated(True)
        self.ui.treeView.setAlternatingRowColors(True)

        self.model = QStandardItemModel(0, 3, self)
        self.ui.treeView.setModel(self.model)

        self.model.setHorizontalHeaderLabels(['Exchange', 'Volume', 'Totla in'])

        
        # balance = [ {'exchange':'binance', 'account': 'xxx1', 'symbol':'BTC', 'balance':{'total':234} },
        #             {'exchange':'binance', 'account': 'xxx1', 'symbol':'ETH', 'balance':{'total':15} },
        #             {'exchange':'kraken', 'account': 'xxx1', 'symbol':'ETH', 'balance':{'total':115} }, ]
        
        # for i in balance:
        #     self.update_tree(i)

        self.ui.treeView.expandAll()  
        

    #@pyqtSlot()
    def on_click(self):
        pass

    @pyqtSlot(str)
    def slot_update_tree(self,balance):

        #print(balance)
        balance = json.loads(balance)
    
        # parent1 = QStandardItem('binance')
        # currency1 = QStandardItem('BTC')
        # parent1.appendRow(currency1)
        
        # currency2 = QStandardItem('ETH')
        # parent1.appendRow(currency2)
        # self.model.appendRow(parent1)

        
        exchange = self.model.findItems(balance['exchange'])
        
        if exchange:
            
            all_currency = exchange[0].rowCount()
            new_currency = True
            print(all_currency)
            
            for c in range(all_currency):
                curency = exchange[0].itme(0,0) 
                
                if curency.text() == balance['symbol']:
                    new_currency = False
                    
                    for i in range(curency.columnCount()):
                        print(curency.text(), curency.item(0,i).text() )
                        #print('update:', exchange[0].text(), curency.text() )
                    
                    print( curency.text(), curency.model().item(0,0).text() ,curency.rowCount() ,curency.columnCount() )
                    curency.takeChild(0,1).setText(balance['balance']['total'])
                        
                    break
                
                
            
            if new_currency:
                
                name = QStandardItem(balance['symbol'])
                total = QStandardItem( str( balance['balance']['total'] ) )
                exchange[0].appendRow([name, total])

                            
        else:
   
            parent1 = QStandardItem(balance['exchange'])
            
            child1 = QStandardItem(balance['symbol'])
            child2 = QStandardItem( str( balance['balance']['total'] ) )
            
            parent1.appendRow([child1, child2])
    
            self.model.appendRow(parent1)
        
    
            
            


    