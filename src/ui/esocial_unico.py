# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'esocial_unico.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QPushButton, QSizePolicy,
    QTableWidget, QTableWidgetItem, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(961, 524)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 20, 221, 16))
        self.btn_adiciona_empresa = QPushButton(self.centralwidget)
        self.btn_adiciona_empresa.setObjectName(u"btn_adiciona_empresa")
        self.btn_adiciona_empresa.setGeometry(QRect(360, 20, 75, 21))
        self.edit_inscricao = QLineEdit(self.centralwidget)
        self.edit_inscricao.setObjectName(u"edit_inscricao")
        self.edit_inscricao.setGeometry(QRect(250, 19, 113, 20))
        self.tableWidget = QTableWidget(self.centralwidget)
        if (self.tableWidget.columnCount() < 4):
            self.tableWidget.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setEnabled(True)
        self.tableWidget.setGeometry(QRect(15, 61, 761, 451))
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.btn_obtem_dados_esocial = QPushButton(self.centralwidget)
        self.btn_obtem_dados_esocial.setObjectName(u"btn_obtem_dados_esocial")
        self.btn_obtem_dados_esocial.setGeometry(QRect(780, 90, 171, 21))
        self.btn_executa_rpa = QPushButton(self.centralwidget)
        self.btn_executa_rpa.setObjectName(u"btn_executa_rpa")
        self.btn_executa_rpa.setGeometry(QRect(780, 210, 171, 21))
        self.btn_relacionar_rubricas = QPushButton(self.centralwidget)
        self.btn_relacionar_rubricas.setObjectName(u"btn_relacionar_rubricas")
        self.btn_relacionar_rubricas.setGeometry(QRect(780, 180, 171, 21))
        self.btn_relaciona_empresas_dominio = QPushButton(self.centralwidget)
        self.btn_relaciona_empresas_dominio.setObjectName(u"btn_relaciona_empresas_dominio")
        self.btn_relaciona_empresas_dominio.setGeometry(QRect(780, 150, 171, 21))
        self.btn_excluir = QPushButton(self.centralwidget)
        self.btn_excluir.setObjectName(u"btn_excluir")
        self.btn_excluir.setGeometry(QRect(780, 240, 171, 21))
        self.btn_conexoes = QPushButton(self.centralwidget)
        self.btn_conexoes.setObjectName(u"btn_conexoes")
        self.btn_conexoes.setGeometry(QRect(780, 60, 171, 21))
        self.btn_obtem_dados_esocial_xml = QPushButton(self.centralwidget)
        self.btn_obtem_dados_esocial_xml.setObjectName(u"btn_obtem_dados_esocial_xml")
        self.btn_obtem_dados_esocial_xml.setGeometry(QRect(780, 120, 171, 21))
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Inscri\u00e7\u00e3o (apenas raiz, no caso de CNPJ)", None))
        self.btn_adiciona_empresa.setText(QCoreApplication.translate("MainWindow", u"Adicionar", None))
        ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Inscri\u00e7\u00e3o", None));
        ___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"C\u00f3digo Dom\u00ednio", None));
        ___qtablewidgetitem2 = self.tableWidget.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Nome Dom\u00ednio", None));
        ___qtablewidgetitem3 = self.tableWidget.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Status", None));
        self.btn_obtem_dados_esocial.setText(QCoreApplication.translate("MainWindow", u"Obter dados do portal e-Social", None))
        self.btn_executa_rpa.setText(QCoreApplication.translate("MainWindow", u"Executar RPA", None))
        self.btn_relacionar_rubricas.setText(QCoreApplication.translate("MainWindow", u"Relacionar Rubricas", None))
        self.btn_relaciona_empresas_dominio.setText(QCoreApplication.translate("MainWindow", u"Relacionar empresas Dom\u00ednio", None))
        self.btn_excluir.setText(QCoreApplication.translate("MainWindow", u"Excluir", None))
        self.btn_conexoes.setText(QCoreApplication.translate("MainWindow", u"Configurar conex\u00f5es", None))
        self.btn_obtem_dados_esocial_xml.setText(QCoreApplication.translate("MainWindow", u"Obter dados dos XMLs e-Social", None))
    # retranslateUi

