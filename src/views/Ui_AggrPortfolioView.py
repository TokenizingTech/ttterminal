# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_AggrPortfolioView.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AggrPortfolioView(object):
    def setupUi(self, AggrPortfolioView):
        AggrPortfolioView.setObjectName("AggrPortfolioView")
        AggrPortfolioView.resize(677, 519)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(AggrPortfolioView)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.treeView = QtWidgets.QTreeView(AggrPortfolioView)
        self.treeView.setObjectName("treeView")
        self.horizontalLayout.addWidget(self.treeView)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(AggrPortfolioView)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.label_3 = QtWidgets.QLabel(AggrPortfolioView)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(AggrPortfolioView)
        QtCore.QMetaObject.connectSlotsByName(AggrPortfolioView)

    def retranslateUi(self, AggrPortfolioView):
        _translate = QtCore.QCoreApplication.translate
        AggrPortfolioView.setWindowTitle(_translate("AggrPortfolioView", "Form"))
        self.label_2.setText(_translate("AggrPortfolioView", "Total"))
        self.label_3.setText(_translate("AggrPortfolioView", "2.3 BTC"))

