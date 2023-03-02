# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog_rpa.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QFrame,
    QGroupBox, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QMainWindow, QProgressBar, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_dialog_rpa(object):
    def setupUi(self, dialog_rpa):
        if not dialog_rpa.objectName():
            dialog_rpa.setObjectName(u"dialog_rpa")
        dialog_rpa.resize(690, 528)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(dialog_rpa.sizePolicy().hasHeightForWidth())
        dialog_rpa.setSizePolicy(sizePolicy)
        dialog_rpa.setStyleSheet(u"QMainWindow {\n"
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
"QLineEdit {\n"
"    margin-bottom: 10px;\n"
"    border-radius: 3px;\n"
"    height: 20px;\n"
"    border: 1px solid;\n"
"    padding: 2px;\n"
"}\n"
"QDateEdit {\n"
"    margin-bottom: 10px;\n"
"    border-radius: 3px;\n"
"    height: 20px;\n"
"    border: 1px solid;\n"
"    padding: 2px;\n"
"}\n"
""
                        "QHeaderView::section{\n"
"     background-color: #e6e5e1;\n"
"}\n"
"QTableWidget{\n"
"    background-color:#e8e8e8;\n"
"}")
        self.centralwidget = QWidget(dialog_rpa)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy1)
        self.centralwidget.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.frame_5 = QFrame(self.frame)
        self.frame_5.setObjectName(u"frame_5")
        sizePolicy.setHeightForWidth(self.frame_5.sizePolicy().hasHeightForWidth())
        self.frame_5.setSizePolicy(sizePolicy)
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_5)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.checkbox__run_local = QCheckBox(self.frame_5)
        self.checkbox__run_local.setObjectName(u"checkbox__run_local")

        self.verticalLayout_4.addWidget(self.checkbox__run_local)

        self.checkbox__run_in_network = QCheckBox(self.frame_5)
        self.checkbox__run_in_network.setObjectName(u"checkbox__run_in_network")
        self.checkbox__run_in_network.setChecked(False)

        self.verticalLayout_4.addWidget(self.checkbox__run_in_network)


        self.verticalLayout_3.addWidget(self.frame_5)

        self.groupBox = QGroupBox(self.frame)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.listbox__options_machines = QListWidget(self.groupBox)
        self.listbox__options_machines.setObjectName(u"listbox__options_machines")
        self.listbox__options_machines.setSelectionMode(QAbstractItemView.MultiSelection)

        self.horizontalLayout_2.addWidget(self.listbox__options_machines)


        self.verticalLayout_3.addWidget(self.groupBox)


        self.verticalLayout.addWidget(self.frame)

        self.frame_2 = QFrame(self.centralwidget)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.progressbar__rpa = QProgressBar(self.frame_2)
        self.progressbar__rpa.setObjectName(u"progressbar__rpa")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.progressbar__rpa.sizePolicy().hasHeightForWidth())
        self.progressbar__rpa.setSizePolicy(sizePolicy2)
        self.progressbar__rpa.setValue(24)

        self.verticalLayout_2.addWidget(self.progressbar__rpa)

        self.label__action_progress = QLabel(self.frame_2)
        self.label__action_progress.setObjectName(u"label__action_progress")
        self.label__action_progress.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.label__action_progress)


        self.verticalLayout.addWidget(self.frame_2)

        self.frame_3 = QFrame(self.centralwidget)
        self.frame_3.setObjectName(u"frame_3")
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_3)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.button__run_rpa = QPushButton(self.frame_3)
        self.button__run_rpa.setObjectName(u"button__run_rpa")

        self.horizontalLayout.addWidget(self.button__run_rpa)


        self.verticalLayout.addWidget(self.frame_3)

        dialog_rpa.setCentralWidget(self.centralwidget)

        self.retranslateUi(dialog_rpa)

        QMetaObject.connectSlotsByName(dialog_rpa)
    # setupUi

    def retranslateUi(self, dialog_rpa):
        dialog_rpa.setWindowTitle(QCoreApplication.translate("dialog_rpa", u"Configurar Execu\u00e7\u00e3o RPA", None))
        self.checkbox__run_local.setText(QCoreApplication.translate("dialog_rpa", u"Executar na m\u00e1quina local?", None))
        self.checkbox__run_in_network.setText(QCoreApplication.translate("dialog_rpa", u"Executar em m\u00e1quina na rede?", None))
        self.groupBox.setTitle(QCoreApplication.translate("dialog_rpa", u"Escolha uma ou mais m\u00e1quinas:", None))
        self.label__action_progress.setText("")
        self.button__run_rpa.setText(QCoreApplication.translate("dialog_rpa", u"INICIAR", None))
    # retranslateUi

