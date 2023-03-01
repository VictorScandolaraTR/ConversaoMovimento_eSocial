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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1053, 470)
        MainWindow.setMinimumSize(QSize(1050, 470))
        MainWindow.setStyleSheet(u"QMainWindow {\n"
"    background-color: #cbcbca;\n"
"}\n"
"QMenuBar {\n"
"    background-color: #a8a7a7;\n"
"    font-size: 14px;\n"
"}\n"
"QMenu {\n"
"    font-size: 14px;\n"
"}\n"
"QLabel {\n"
"    font-size: 13px;\n"
"}\n"
"QCheckBox {\n"
"    font-size: 13px;\n"
"}\n"
"QListWidget {\n"
"    font-size: 13px; \n"
"}\n"
"QPushButton {\n"
"    border-radius: 5px;\n"
"    background-color: #424242;\n"
"    color: #f96400;\n"
"    padding: 5px;\n"
"    font-size: 13px;\n"
"    font-weight: bold;\n"
"    margin-bottom: 10px;\n"
"    border-radius: 3px;\n"
"    height: 20px;\n"
"    border: 1px solid;\n"
"    padding: 2px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #f96400;\n"
"    color: #FFFFFF;\n"
"}\n"
"QPushButton:disabled {\n"
"    background-color: #666666;\n"
"    color: #DDDDDD;\n"
"}\n"
"QLineEdit {\n"
"    margin-bottom: 10px;\n"
"    border-radius: 3px;\n"
"    height: 20px;\n"
"    border: 1px solid;\n"
"    padding: 2px;\n"
"}\n"
"QDateEdit {\n"
"    margin-bottom: 10px;\n"
"    border-r"
                        "adius: 3px;\n"
"    height: 20px;\n"
"    border: 1px solid;\n"
"    padding: 2px;\n"
"}\n"
"QHeaderView::section{\n"
"     background-color: #e6e5e1;\n"
"}\n"
"QTableWidget{\n"
"    background-color:#e8e8e8;\n"
"}")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame_2 = QFrame(self.centralwidget)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.frame_3 = QFrame(self.frame_2)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.frame_3)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.edit_inscricao = QLineEdit(self.frame_3)
        self.edit_inscricao.setObjectName(u"edit_inscricao")

        self.horizontalLayout_2.addWidget(self.edit_inscricao)

        self.btn_adiciona_empresa = QPushButton(self.frame_3)
        self.btn_adiciona_empresa.setObjectName(u"btn_adiciona_empresa")

        self.horizontalLayout_2.addWidget(self.btn_adiciona_empresa)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout_2.addWidget(self.frame_3)

        self.frame_4 = QFrame(self.frame_2)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.tableWidget = QTableWidget(self.frame_4)
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
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.horizontalLayout_3.addWidget(self.tableWidget)

        self.frame = QFrame(self.frame_4)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.btn_conexoes = QPushButton(self.frame)
        self.btn_conexoes.setObjectName(u"btn_conexoes")

        self.verticalLayout.addWidget(self.btn_conexoes)

        self.btn_obtem_dados_esocial = QPushButton(self.frame)
        self.btn_obtem_dados_esocial.setObjectName(u"btn_obtem_dados_esocial")

        self.verticalLayout.addWidget(self.btn_obtem_dados_esocial)

        self.btn_obtem_dados_esocial_xml = QPushButton(self.frame)
        self.btn_obtem_dados_esocial_xml.setObjectName(u"btn_obtem_dados_esocial_xml")

        self.verticalLayout.addWidget(self.btn_obtem_dados_esocial_xml)

        self.btn_relaciona_empresas_dominio = QPushButton(self.frame)
        self.btn_relaciona_empresas_dominio.setObjectName(u"btn_relaciona_empresas_dominio")

        self.verticalLayout.addWidget(self.btn_relaciona_empresas_dominio)

        self.btn_relacionar_rubricas = QPushButton(self.frame)
        self.btn_relacionar_rubricas.setObjectName(u"btn_relacionar_rubricas")

        self.verticalLayout.addWidget(self.btn_relacionar_rubricas)

        self.btn_executa_rpa = QPushButton(self.frame)
        self.btn_executa_rpa.setObjectName(u"btn_executa_rpa")
        self.btn_executa_rpa.setEnabled(True)

        self.verticalLayout.addWidget(self.btn_executa_rpa)

        self.btn_excluir = QPushButton(self.frame)
        self.btn_excluir.setObjectName(u"btn_excluir")

        self.verticalLayout.addWidget(self.btn_excluir)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.horizontalLayout_3.addWidget(self.frame)


        self.verticalLayout_2.addWidget(self.frame_4)


        self.horizontalLayout.addWidget(self.frame_2)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Inscri\u00e7\u00e3o ", None))
        self.btn_adiciona_empresa.setText(QCoreApplication.translate("MainWindow", u"Adicionar", None))
        ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Inscri\u00e7\u00e3o", None));
        ___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"C\u00f3digo Dom\u00ednio", None));
        ___qtablewidgetitem2 = self.tableWidget.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Nome Dom\u00ednio", None));
        ___qtablewidgetitem3 = self.tableWidget.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Status", None));
        self.btn_conexoes.setText(QCoreApplication.translate("MainWindow", u"Configurar conex\u00f5es", None))
        self.btn_obtem_dados_esocial.setText(QCoreApplication.translate("MainWindow", u"Obter dados do portal e-Social", None))
        self.btn_obtem_dados_esocial_xml.setText(QCoreApplication.translate("MainWindow", u"Obter dados dos XMLs e-Social", None))
        self.btn_relaciona_empresas_dominio.setText(QCoreApplication.translate("MainWindow", u"Relacionar empresas Dom\u00ednio", None))
        self.btn_relacionar_rubricas.setText(QCoreApplication.translate("MainWindow", u"Relacionar Rubricas", None))
        self.btn_executa_rpa.setText(QCoreApplication.translate("MainWindow", u"Executar RPA", None))
        self.btn_excluir.setText(QCoreApplication.translate("MainWindow", u"Excluir", None))
    # retranslateUi

