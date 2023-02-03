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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QFormLayout,
    QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMainWindow, QProgressBar, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class UI_dialog_rpa(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(563, 345)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label__title = QLabel(self.centralwidget)
        self.label__title.setObjectName(u"label__title")
        self.label__title.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label__title)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.checkbox__run_in_network = QCheckBox(self.centralwidget)
        self.checkbox__run_in_network.setObjectName(u"checkbox__run_in_network")
        self.checkbox__run_in_network.setChecked(False)

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.checkbox__run_in_network)

        self.label__run_in_network = QLabel(self.centralwidget)
        self.label__run_in_network.setObjectName(u"label__run_in_network")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label__run_in_network)

        self.listbox__options_machines = QListWidget(self.centralwidget)
        self.listbox__options_machines.setObjectName(u"listbox__options_machines")
        self.listbox__options_machines.setSelectionMode(QAbstractItemView.MultiSelection)

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.listbox__options_machines)

        self.checkbox__run_local = QCheckBox(self.centralwidget)
        self.checkbox__run_local.setObjectName(u"checkbox__run_local")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.checkbox__run_local)


        self.verticalLayout.addLayout(self.formLayout)

        self.progressbar__rpa = QProgressBar(self.centralwidget)
        self.progressbar__rpa.setObjectName(u"progressbar__rpa")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.progressbar__rpa.sizePolicy().hasHeightForWidth())
        self.progressbar__rpa.setSizePolicy(sizePolicy1)
        self.progressbar__rpa.setValue(24)

        self.verticalLayout.addWidget(self.progressbar__rpa)

        self.label__action_progress = QLabel(self.centralwidget)
        self.label__action_progress.setObjectName(u"label__action_progress")
        self.label__action_progress.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label__action_progress)

        self.button__run_rpa = QPushButton(self.centralwidget)
        self.button__run_rpa.setObjectName(u"button__run_rpa")

        self.verticalLayout.addWidget(self.button__run_rpa, 0, Qt.AlignBottom)


        self.horizontalLayout.addLayout(self.verticalLayout)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Configurar Execu\u00e7\u00e3o RPA", None))
        self.label__title.setText(QCoreApplication.translate("MainWindow", u"CONFIGURAR EXECU\u00c7\u00c3O RPA", None))
        self.checkbox__run_in_network.setText(QCoreApplication.translate("MainWindow", u"Executar em m\u00e1quina na rede?", None))
        self.label__run_in_network.setText(QCoreApplication.translate("MainWindow", u"Escolha uma ou mais m\u00e1quinas:", None))
        self.checkbox__run_local.setText(QCoreApplication.translate("MainWindow", u"Executar na m\u00e1quina local?", None))
        self.label__action_progress.setText("")
        self.button__run_rpa.setText(QCoreApplication.translate("MainWindow", u"INICIAR", None))
    # retranslateUi

