# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'esocial_unico.ui'
#
# Created by: PyQt5 UI code generator 5.15.8
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 60, 47, 13))
        self.label.setObjectName("label")
        self.btn_adiciona_empresa = QtWidgets.QPushButton(self.centralwidget)
        self.btn_adiciona_empresa.setGeometry(QtCore.QRect(180, 60, 75, 21))
        self.btn_adiciona_empresa.setObjectName("btn_adiciona_empresa")
        self.edit_inscricao = QtWidgets.QLineEdit(self.centralwidget)
        self.edit_inscricao.setGeometry(QtCore.QRect(70, 59, 113, 20))
        self.edit_inscricao.setObjectName("edit_inscricao")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setEnabled(True)
        self.tableWidget.setGeometry(QtCore.QRect(15, 101, 761, 451))
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        self.btn_obtem_dados_esocial = QtWidgets.QPushButton(self.centralwidget)
        self.btn_obtem_dados_esocial.setGeometry(QtCore.QRect(20, 560, 150, 21))
        self.btn_obtem_dados_esocial.setObjectName("btn_obtem_dados_esocial")
        self.btn_executa_rpa = QtWidgets.QPushButton(self.centralwidget)
        self.btn_executa_rpa.setGeometry(QtCore.QRect(620, 560, 150, 21))
        self.btn_executa_rpa.setObjectName("btn_executa_rpa")
        self.btn_relacionar_rubricas = QtWidgets.QPushButton(self.centralwidget)
        self.btn_relacionar_rubricas.setGeometry(QtCore.QRect(420, 560, 150, 21))
        self.btn_relacionar_rubricas.setObjectName("btn_relacionar_rubricas")
        self.btn_relaciona_empresas_dominio = QtWidgets.QPushButton(self.centralwidget)
        self.btn_relaciona_empresas_dominio.setGeometry(QtCore.QRect(220, 560, 150, 21))
        self.btn_relaciona_empresas_dominio.setObjectName("btn_relaciona_empresas_dominio")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Inscrição"))
        self.btn_adiciona_empresa.setText(_translate("MainWindow", "Adicionar"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Inscrição"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Código Domínio"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Nome Domínio"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Status"))
        self.btn_obtem_dados_esocial.setText(_translate("MainWindow", "Obter dados do e-Social"))
        self.btn_executa_rpa.setText(_translate("MainWindow", "Executar RPA"))
        self.btn_relacionar_rubricas.setText(_translate("MainWindow", "Relacionar Rubricas"))
        self.btn_relaciona_empresas_dominio.setText(_translate("MainWindow", "Relacionar empresas Domínio"))