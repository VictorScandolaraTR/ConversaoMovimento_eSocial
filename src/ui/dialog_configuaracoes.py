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
from PySide6.QtWidgets import (QApplication, QDialog, QGroupBox, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QWidget)

class Ui_dialog_configuracioes(object):
    def setupUi(self, dialog_configuracioes):
        if not dialog_configuracioes.objectName():
            dialog_configuracioes.setObjectName(u"dialog_configuracioes")
        dialog_configuracioes.resize(551, 233)
        self.groupBox_2 = QGroupBox(dialog_configuracioes)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(10, 10, 531, 181))
        self.edit_usuario_dominio = QLineEdit(self.groupBox_2)
        self.edit_usuario_dominio.setObjectName(u"edit_usuario_dominio")
        self.edit_usuario_dominio.setGeometry(QRect(200, 80, 113, 20))
        self.edit_banco_dominio = QLineEdit(self.groupBox_2)
        self.edit_banco_dominio.setObjectName(u"edit_banco_dominio")
        self.edit_banco_dominio.setGeometry(QRect(200, 50, 113, 20))
        self.edit_senha_dominio = QLineEdit(self.groupBox_2)
        self.edit_senha_dominio.setObjectName(u"edit_senha_dominio")
        self.edit_senha_dominio.setGeometry(QRect(200, 110, 113, 20))
        self.edit_senha_dominio.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(10, 80, 181, 16))
        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(10, 110, 181, 16))
        self.label_7 = QLabel(self.groupBox_2)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(10, 50, 181, 16))
        self.edit_usuario_sgd = QLineEdit(self.groupBox_2)
        self.edit_usuario_sgd.setObjectName(u"edit_usuario_sgd")
        self.edit_usuario_sgd.setGeometry(QRect(410, 50, 113, 20))
        self.label_8 = QLabel(self.groupBox_2)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(330, 80, 81, 16))
        self.label_9 = QLabel(self.groupBox_2)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(330, 50, 81, 16))
        self.edit_senha_sgd = QLineEdit(self.groupBox_2)
        self.edit_senha_sgd.setObjectName(u"edit_senha_sgd")
        self.edit_senha_sgd.setGeometry(QRect(410, 80, 113, 20))
        self.edit_senha_sgd.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.label_10 = QLabel(self.groupBox_2)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setGeometry(QRect(10, 140, 181, 16))
        self.edit_empresa_rubricas_dominio = QLineEdit(self.groupBox_2)
        self.edit_empresa_rubricas_dominio.setObjectName(u"edit_empresa_rubricas_dominio")
        self.edit_empresa_rubricas_dominio.setGeometry(QRect(200, 140, 113, 20))
        self.edit_empresa_rubricas_dominio.setEchoMode(QLineEdit.Normal)
        self.edit_diretorio_trabalho = QLineEdit(self.groupBox_2)
        self.edit_diretorio_trabalho.setObjectName(u"edit_diretorio_trabalho")
        self.edit_diretorio_trabalho.setGeometry(QRect(200, 20, 271, 20))
        self.btn_diretorio_trabalho = QPushButton(self.groupBox_2)
        self.btn_diretorio_trabalho.setObjectName(u"btn_diretorio_trabalho")
        self.btn_diretorio_trabalho.setGeometry(QRect(470, 20, 51, 23))
        self.label_11 = QLabel(self.groupBox_2)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(10, 20, 181, 16))
        self.btn_concertar_configuracoes = QPushButton(dialog_configuracioes)
        self.btn_concertar_configuracoes.setObjectName(u"btn_concertar_configuracoes")
        self.btn_concertar_configuracoes.setGeometry(QRect(300, 200, 75, 23))
        self.btn_confirmar_configuracoes = QPushButton(dialog_configuracioes)
        self.btn_confirmar_configuracoes.setObjectName(u"btn_confirmar_configuracoes")
        self.btn_confirmar_configuracoes.setGeometry(QRect(400, 200, 75, 23))

        self.retranslateUi(dialog_configuracioes)

        QMetaObject.connectSlotsByName(dialog_configuracioes)
    # setupUi

    def retranslateUi(self, dialog_configuracioes):
        dialog_configuracioes.setWindowTitle(QCoreApplication.translate("dialog_configuracioes", u"Configura\u00e7\u00f5es", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("dialog_configuracioes", u"Configura\u00e7\u00f5es Dom\u00ednio", None))
        self.label_5.setText(QCoreApplication.translate("dialog_configuracioes", u"Usu\u00e1rio Dom\u00ednio Folha", None))
        self.label_6.setText(QCoreApplication.translate("dialog_configuracioes", u"Senha Dom\u00ednio Folha", None))
        self.label_7.setText(QCoreApplication.translate("dialog_configuracioes", u"Banco de dados Dom\u00ednio Folha", None))
        self.label_8.setText(QCoreApplication.translate("dialog_configuracioes", u"Senha SGD", None))
        self.label_9.setText(QCoreApplication.translate("dialog_configuracioes", u"Usu\u00e1rio SGD", None))
        self.label_10.setText(QCoreApplication.translate("dialog_configuracioes", u"Empresa rubricas", None))
        self.btn_diretorio_trabalho.setText(QCoreApplication.translate("dialog_configuracioes", u"Buscar", None))
        self.label_11.setText(QCoreApplication.translate("dialog_configuracioes", u"Diret\u00f3rio de trabalho", None))
        self.btn_concertar_configuracoes.setText(QCoreApplication.translate("dialog_configuracioes", u"Cancelar", None))
        self.btn_confirmar_configuracoes.setText(QCoreApplication.translate("dialog_configuracioes", u"Confirmar", None))
    # retranslateUi

