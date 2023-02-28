# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog_configuracoes.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QGroupBox,
    QHBoxLayout, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_dialog_configuracioes(object):
    def setupUi(self, dialog_configuracioes):
        if not dialog_configuracioes.objectName():
            dialog_configuracioes.setObjectName(u"dialog_configuracioes")
        dialog_configuracioes.resize(727, 495)
        dialog_configuracioes.setMinimumSize(QSize(727, 495))
        dialog_configuracioes.setStyleSheet(u"QMainWindow {\n"
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
        self.verticalLayout = QVBoxLayout(dialog_configuracioes)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_7 = QGroupBox(dialog_configuracioes)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.horizontalLayout_4 = QHBoxLayout(self.groupBox_7)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.edit_diretorio_trabalho = QLineEdit(self.groupBox_7)
        self.edit_diretorio_trabalho.setObjectName(u"edit_diretorio_trabalho")

        self.horizontalLayout_4.addWidget(self.edit_diretorio_trabalho)

        self.btn_diretorio_trabalho = QPushButton(self.groupBox_7)
        self.btn_diretorio_trabalho.setObjectName(u"btn_diretorio_trabalho")

        self.horizontalLayout_4.addWidget(self.btn_diretorio_trabalho)


        self.verticalLayout.addWidget(self.groupBox_7)

        self.frame_2 = QFrame(dialog_configuracioes)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.frame_4 = QFrame(self.frame_2)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_4)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox_6 = QGroupBox(self.frame_4)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.horizontalLayout_12 = QHBoxLayout(self.groupBox_6)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.edit_banco_dominio = QLineEdit(self.groupBox_6)
        self.edit_banco_dominio.setObjectName(u"edit_banco_dominio")

        self.horizontalLayout_12.addWidget(self.edit_banco_dominio)


        self.verticalLayout_2.addWidget(self.groupBox_6)

        self.groupBox_5 = QGroupBox(self.frame_4)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.horizontalLayout_13 = QHBoxLayout(self.groupBox_5)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.edit_usuario_dominio = QLineEdit(self.groupBox_5)
        self.edit_usuario_dominio.setObjectName(u"edit_usuario_dominio")

        self.horizontalLayout_13.addWidget(self.edit_usuario_dominio)


        self.verticalLayout_2.addWidget(self.groupBox_5)

        self.groupBox_4 = QGroupBox(self.frame_4)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.horizontalLayout_11 = QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.edit_senha_dominio = QLineEdit(self.groupBox_4)
        self.edit_senha_dominio.setObjectName(u"edit_senha_dominio")
        self.edit_senha_dominio.setEchoMode(QLineEdit.PasswordEchoOnEdit)

        self.horizontalLayout_11.addWidget(self.edit_senha_dominio)


        self.verticalLayout_2.addWidget(self.groupBox_4)

        self.groupBox_3 = QGroupBox(self.frame_4)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.horizontalLayout_9 = QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.edit_empresa_rubricas_dominio = QLineEdit(self.groupBox_3)
        self.edit_empresa_rubricas_dominio.setObjectName(u"edit_empresa_rubricas_dominio")
        self.edit_empresa_rubricas_dominio.setEchoMode(QLineEdit.Normal)

        self.horizontalLayout_9.addWidget(self.edit_empresa_rubricas_dominio)


        self.verticalLayout_2.addWidget(self.groupBox_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.horizontalLayout_3.addWidget(self.frame_4)

        self.frame_5 = QFrame(self.frame_2)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_5)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBox_2 = QGroupBox(self.frame_5)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.horizontalLayout_10 = QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.edit_usuario_sgd = QLineEdit(self.groupBox_2)
        self.edit_usuario_sgd.setObjectName(u"edit_usuario_sgd")

        self.horizontalLayout_10.addWidget(self.edit_usuario_sgd)


        self.verticalLayout_3.addWidget(self.groupBox_2)

        self.groupBox = QGroupBox(self.frame_5)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout_8 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.edit_senha_sgd = QLineEdit(self.groupBox)
        self.edit_senha_sgd.setObjectName(u"edit_senha_sgd")
        self.edit_senha_sgd.setEchoMode(QLineEdit.PasswordEchoOnEdit)

        self.horizontalLayout_8.addWidget(self.edit_senha_sgd)


        self.verticalLayout_3.addWidget(self.groupBox)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)


        self.horizontalLayout_3.addWidget(self.frame_5)


        self.verticalLayout.addWidget(self.frame_2)

        self.frame = QFrame(dialog_configuracioes)
        self.frame.setObjectName(u"frame")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.btn_concertar_configuracoes = QPushButton(self.frame)
        self.btn_concertar_configuracoes.setObjectName(u"btn_concertar_configuracoes")

        self.horizontalLayout.addWidget(self.btn_concertar_configuracoes)

        self.btn_confirmar_configuracoes = QPushButton(self.frame)
        self.btn_confirmar_configuracoes.setObjectName(u"btn_confirmar_configuracoes")

        self.horizontalLayout.addWidget(self.btn_confirmar_configuracoes)


        self.verticalLayout.addWidget(self.frame)


        self.retranslateUi(dialog_configuracioes)

        QMetaObject.connectSlotsByName(dialog_configuracioes)
    # setupUi

    def retranslateUi(self, dialog_configuracioes):
        dialog_configuracioes.setWindowTitle(QCoreApplication.translate("dialog_configuracioes", u"Configura\u00e7\u00f5es", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("dialog_configuracioes", u"Diret\u00f3rio de trabalho", None))
        self.btn_diretorio_trabalho.setText(QCoreApplication.translate("dialog_configuracioes", u"Buscar", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("dialog_configuracioes", u"Banco de dados Dom\u00ednio Folha", None))
        self.edit_banco_dominio.setPlaceholderText("")
        self.groupBox_5.setTitle(QCoreApplication.translate("dialog_configuracioes", u"Usu\u00e1rio Dom\u00ednio Folha", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("dialog_configuracioes", u"Senha Dom\u00ednio Folha", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("dialog_configuracioes", u"Empresa rubricas", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("dialog_configuracioes", u"Usu\u00e1rio SGD", None))
        self.groupBox.setTitle(QCoreApplication.translate("dialog_configuracioes", u"Senha SGD", None))
        self.btn_concertar_configuracoes.setText(QCoreApplication.translate("dialog_configuracioes", u"Cancelar", None))
        self.btn_confirmar_configuracoes.setText(QCoreApplication.translate("dialog_configuracioes", u"Confirmar", None))
    # retranslateUi

