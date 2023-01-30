from PySide6.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from src.esocial import eSocialXML
from src.ui.esocial import Ui_MainWindow as Interface
import os, json, sys

class eSocial(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.__window = Interface()
        self.__esocial = eSocialXML("xml")
    
    def init_gui(self):
        """
        Declarar componentes que serão utilizados da interface
        """
        self.__window.setupUi(self)
        self.setWindowTitle('Conversão de Movimentos - e-Social')
        
        self.__tab_processo = self.__window.tab_processo
        
        self.__btn_previows = self.__window.btn_previows
        self.__btn_next = self.__window.btn_next

        self.__edit_usuario_esocial = self.__window.edit_usuario_esocial
        self.__edit_senha_esocial = self.__window.edit_senha_esocial
        self.__combo_tipo_certificado = self.__window.combo_tipo_certificado
        self.__edit_certificado = self.__window.edit_certificado
        self.__btn_procurar_certificado = self.__window.btn_procurar_certificado

        self.__edit_dsn_dominio = self.__window.edit_dsn_dominio
        self.__edit_usuario_dominio = self.__window.edit_usuario_dominio
        self.__edit_senha_dominio = self.__window.edit_senha_dominio
        self.__btn_lista_empresas = self.__window.btn_lista_empresas
        self.__list_empresas = self.__window.list_empresas

        self.__edit_empresa_rubricas = self.__window.edit_empresa_rubricas
        self.__date_filtro = self.__window.date_filtro
        self.__btn_gera_planilha_rubricas = self.__window.btn_gera_planilha_rubricas

        self.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = eSocial()
    window.init_gui()
    app.exec()
    
    '''app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Interface()
    ui.setupUi(MainWindow)
    MainWindow.show()
    app.exec()'''

'''os.system("cls")
esocial = eSocialXML("xml")
esocial.carregar_informacoes_xml()

relacao_empresas = esocial.relaciona_empresas()
relacao_empregados = esocial.relaciona_empregados()

esocial.gera_excel_relacao(relacao_empresas)

esocial.gerar_afastamentos_importacao()
esocial.gerar_ferias_importacao()

'''f = open("s1010.json","w")
f.write(json.dumps(esocial.processar_rubricas()))
f.close()

f = open("s1200.json","w")
f.write(json.dumps(esocial.dicionario_s1200))
f.close()

f = open("s1210.json","w")
f.write(json.dumps(esocial.dicionario_s1210))
f.close()

f = open("s2230.json","w")
f.write(json.dumps(esocial.dicionario_s2230))
f.close()

f = open("s2299.json","w")
f.write(json.dumps(esocial.dicionario_s2299))
f.close()

f = open("s2399.json","w")
f.write(json.dumps(esocial.dicionario_s2399))
f.close()'''