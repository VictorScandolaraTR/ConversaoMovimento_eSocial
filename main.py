from PySide6.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from src.esocial import eSocialXML
from src.ui.esocial_unico import Ui_MainWindow as Interface
from src.ui.dialog_configuaracoes import Ui_dialog_configuracioes as DialogConfiguracoes
from sqlalchemy import create_engine, Table, update
import pandas as pd
import os, json, sys

class eSocial(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.__window = Interface()
        self.__diretorio_trabalho = "xml"
        self.__engine = create_engine(f"sqlite:///{self.__diretorio_trabalho}/operacao.db")
        self.__empresas, self.__empresas_em_uso = self.carrega_empresas()
    
    def init_gui(self):
        """
        Declarar componentes que serão utilizados da interface
        """
        self.__window.setupUi(self)
        self.setWindowTitle('Conversão de Movimentos - e-Social')
        
        self.__tabela_empresas = self.__window.tableWidget
        self.__edit_inscricao = self.__window.edit_inscricao
        self.__btn_adiciona_empresa = self.__window.btn_adiciona_empresa
        self.__btn_conexoes = self.__window.btn_conexoes
        self.__btn_obtem_dados_esocial = self.__window.btn_obtem_dados_esocial
        self.__btn_relaciona_empresas_dominio = self.__window.btn_relaciona_empresas_dominio
        self.__btn_relacionar_rubricas = self.__window.btn_relacionar_rubricas
        self.__btn_executa_rpa = self.__window.btn_executa_rpa
        self.__btn_excluir = self.__window.btn_excluir

        self.__tabela_empresas.setColumnWidth(2,344)
        self.__tabela_empresas.setColumnWidth(3,200)

        self.__tabela_empresas.clicked.connect(self.seleciona_registro)
        self.__btn_adiciona_empresa.clicked.connect(self.adiciona_empresa)
        self.__btn_conexoes.clicked.connect(self.configura_conexoes)
        self.__btn_obtem_dados_esocial.clicked.connect(self.acessa_portal_esocial)
        self.__btn_relaciona_empresas_dominio.clicked.connect(self.relaciona_empresa_dominio)
        self.__btn_relacionar_rubricas.clicked.connect(self.relacionar_rubricas)
        self.__btn_executa_rpa.clicked.connect(self.executar_rpa)
        self.__btn_excluir.clicked.connect(self.exclui_empresa)

        self.__btn_conexoes.setEnabled(False)
        self.__btn_obtem_dados_esocial.setEnabled(False)
        self.__btn_relaciona_empresas_dominio.setEnabled(False)
        self.__btn_relacionar_rubricas.setEnabled(False)
        self.__btn_executa_rpa.setEnabled(False)
        self.__btn_excluir.setEnabled(False)

        self.atualiza_tabela_empresas()
        self.show()

    def carrega_empresas(self):
        df = pd.read_sql("SELECT * FROM EMPRESAS",con=self.__engine)
        
        empresas = {}

        for i in range(len(df)):
            empresas[str(i)] = {
                "inscricao": df.loc[i,"inscricao"],
                "codi_emp": df.loc[i,"codi_emp"],
                "nome_emp": df.loc[i,"nome_emp"],
                "status": df.loc[i,"status"],
                "base_dominio": df.loc[i,"base_dominio"],
                "usuario_dominio": df.loc[i,"usuario_dominio"],
                "senha_dominio": df.loc[i,"senha_dominio"],
                "empresa_padrao_rubricas": df.loc[i,"empresa_padrao_rubricas"],
                "usuario_esocial": df.loc[i,"usuario_esocial"],
                "senha_esocial": df.loc[i,"senha_esocial"],
                "certificado_esocial": df.loc[i,"certificado_esocial"],
                "tipo_certificado_esocial": df.loc[i,"tipo_certificado_esocial"],
                "usuario_sgd": df.loc[i,"usuario_sgd"],
                "senha_sgd": df.loc[i,"senha_sgd"]
            }
            
        empresas_em_uso = []

        for i in empresas:
            empresas_em_uso.append(empresas[i]["inscricao"])

        return empresas, empresas_em_uso

    def atualiza_tabela_empresas(self):
        quantidade_empresas = len(self.__empresas)

        if (quantidade_empresas==0):
            return
        else:
            self.__tabela_empresas.setRowCount(quantidade_empresas)

            linha = 0
            while linha < quantidade_empresas:
                self.__tabela_empresas.setItem(linha, 0, QtWidgets.QTableWidgetItem(self.__empresas.get(str(linha)).get("inscricao")))
                self.__tabela_empresas.setItem(linha, 1, QtWidgets.QTableWidgetItem(self.__empresas.get(str(linha)).get("codi_emp")))
                self.__tabela_empresas.setItem(linha, 2, QtWidgets.QTableWidgetItem(self.__empresas.get(str(linha)).get("nome_emp")))

                status = self.__empresas.get(str(linha)).get("status")

                match status:
                    case "E":
                        status = "Dados carregados do e-Social"
                    case "D":
                        status = "Dados carregados do Domínio"
                    case "P":
                        status = "Planilha de rubricas geradas"
                    case "R":
                        status = "Processo concluído"

                self.__tabela_empresas.setItem(linha, 3, QtWidgets.QTableWidgetItem(status))

                linha = linha + 1
    
    def adiciona_empresa(self):
        os.system(f"mkdir {self.__diretorio_trabalho}")
        proxima_linha = len(self.__empresas)
        inscricao = self.__edit_inscricao.text()

        if(inscricao==""):
            print("Preencha o campo inscrição.")
            return
        if(inscricao in self.__empresas_em_uso):
            print("Empresa já cadastrada.")
            return
        
        os.system(f"mkdir {self.__diretorio_trabalho}\\{inscricao}")
        os.system(f"mkdir {self.__diretorio_trabalho}\\{inscricao}\\downloads")
        os.system(f"mkdir {self.__diretorio_trabalho}\\{inscricao}\\eventos")
        os.system(f"mkdir {self.__diretorio_trabalho}\\{inscricao}\\importar")

        conexao = self.__engine.connect()
        conexao.execute(f"INSERT INTO EMPRESAS (inscricao) VALUES ('{inscricao}')")
        self.atualiza_tabela_empresas()

        self.__empresas[str(proxima_linha)] = {
            "inscricao": inscricao,
            "codi_emp": "",
            "nome_emp": "",
            "status": "",
            "base_dominio": "",
            "usuario_dominio": "",
            "senha_dominio": "",
            "empresa_padrao_rubricas": "",
            "usuario_esocial": "",
            "senha_esocial": "",
            "certificado_esocial": "",
            "tipo_certificado_esocial": "",
            "usuario_sgd": "",
            "senha_sgd": ""
        }

        self.__empresas_em_uso.append(inscricao)
        
        self.__edit_inscricao.setText("")
        self.atualiza_tabela_empresas()

    def exclui_empresa(self):
        self.atualiza_status("Excluindo...")
        inscricao = self.__tabela_empresas.selectedItems()[0].text()

        conexao = self.__engine.connect()
        conexao.execute(f"DELETE FROM EMPRESAS WHERE inscricao = {inscricao}")

        os.system(f"del /q {self.__diretorio_trabalho}\\{inscricao}\\downloads")
        os.system(f"del /q {self.__diretorio_trabalho}\\{inscricao}\\eventos")
        os.system(f"del /q {self.__diretorio_trabalho}\\{inscricao}\\importar")
        os.system(f"del /q {self.__diretorio_trabalho}\\{inscricao}")
        os.system(f"rmdir {self.__diretorio_trabalho}\\{inscricao}\\downloads")
        os.system(f"rmdir {self.__diretorio_trabalho}\\{inscricao}\\eventos")
        os.system(f"rmdir {self.__diretorio_trabalho}\\{inscricao}\\importar")
        os.system(f"rmdir {self.__diretorio_trabalho}\\{inscricao}")
        
        self.__empresas, self.__empresas_em_uso = self.carrega_empresas()
        self.atualiza_tabela_empresas()

    def configura_conexoes(self):
        window = eSocialConfiguracoes()
        window.init_gui()
    
    def seleciona_registro(self):
        indice = self.__tabela_empresas.selectedItems()[0].row()
        status = self.__empresas[str(indice)]["status"]

        match status:
            case ""|None:
                self.__btn_conexoes.setEnabled(True)
                self.__btn_obtem_dados_esocial.setEnabled(True)
                self.__btn_relaciona_empresas_dominio.setEnabled(False)
                self.__btn_relacionar_rubricas.setEnabled(False)
                self.__btn_executa_rpa.setEnabled(False)
                self.__btn_excluir.setEnabled(True)
            case "E":
                self.__btn_conexoes.setEnabled(True)
                self.__btn_obtem_dados_esocial.setEnabled(True)
                self.__btn_relaciona_empresas_dominio.setEnabled(True)
                self.__btn_relacionar_rubricas.setEnabled(False)
                self.__btn_executa_rpa.setEnabled(False)
                self.__btn_excluir.setEnabled(True)
                self.__tabela_empresas.selectedItems()[3].setText("Dados carregados do e-Social")
            case "D":
                self.__btn_conexoes.setEnabled(True)
                self.__btn_obtem_dados_esocial.setEnabled(True)
                self.__btn_relaciona_empresas_dominio.setEnabled(True)
                self.__btn_relacionar_rubricas.setEnabled(True)
                self.__btn_executa_rpa.setEnabled(False)
                self.__btn_excluir.setEnabled(True)
                self.__tabela_empresas.selectedItems()[3].setText("Dados carregados do Domínio")
            case "P":
                self.__btn_conexoes.setEnabled(True)
                self.__btn_obtem_dados_esocial.setEnabled(True)
                self.__btn_relaciona_empresas_dominio.setEnabled(True)
                self.__btn_relacionar_rubricas.setEnabled(True)
                self.__btn_executa_rpa.setEnabled(False)
                self.__btn_excluir.setEnabled(True)
                self.__tabela_empresas.selectedItems()[3].setText("Planilha de rubricas geradas")
            case "R":
                self.__btn_conexoes.setEnabled(True)
                self.__btn_obtem_dados_esocial.setEnabled(True)
                self.__btn_relaciona_empresas_dominio.setEnabled(True)
                self.__btn_relacionar_rubricas.setEnabled(True)
                self.__btn_executa_rpa.setEnabled(True)
                self.__btn_excluir.setEnabled(True)
                self.__tabela_empresas.selectedItems()[3].setText("Processo concluído")

    def atualiza_status(self, status, status_bd = ""):
        self.__tabela_empresas.selectedItems()[3].setText(status)
        inscricao = self.__tabela_empresas.selectedItems()[0].text()
        indice = self.__tabela_empresas.selectedItems()[0].row()

        if(status_bd!=""):
            self.__empresas[str(indice)]["status"] = "E"
            conexao = self.__engine.connect()
            conexao.execute(f"UPDATE EMPRESAS SET status = '{status_bd}' WHERE inscricao = '{inscricao}'")
    
    def acessa_portal_esocial(self):
        self.atualiza_status("Buscando dados do e-Social...")
        indice = self.__tabela_empresas.selectedItems()[0].row()
        inscricao = self.__tabela_empresas.selectedItems()[0].text()
        esocial = eSocialXML(f"{self.__diretorio_trabalho}\\{inscricao}")

        usuario = self.__empresas.get(indice).get("usuario_esocial")
        senha = self.__empresas.get(indice).get("senha_esocial")
        tipo = self.__empresas.get(indice).get("tipo_certificado_esocial")
        certificado = self.__empresas.get(indice).get("certificado_esocial")
        esocial.configura_conexao_esocial(usuario, senha, certificado, tipo)
        esocial.baixar_dados_esocial()
        
        self.atualiza_status("Lendo informações...")
        esocial.extrair_arquivos_xml()
        esocial.carregar_informacoes_xml()

        self.atualiza_status("Dados carregados do e-Social","E")
        self.seleciona_registro()

    def relaciona_empresa_dominio(self):
        self.atualiza_status("Consultando banco de dados Domínio...")
        inscricao = self.__tabela_empresas.selectedItems()[0].text()
        esocial = eSocialXML(f"{self.__diretorio_trabalho}\\{inscricao}")
        esocial.configura_conexao_dominio("movto_esocial","EXTERNO","123456")
        empresas = esocial.relaciona_empresas(str(self.__tabela_empresas.selectedItems()[0].text()))
        indice = self.__tabela_empresas.selectedItems()[0].row()

        if(len(empresas)==1):
            self.__tabela_empresas.selectedItems()[1].setText(str(empresas[0]["codigo"]))
            self.__tabela_empresas.selectedItems()[2].setText(str(empresas[0]["nome"]))
            self.__empresas[str(indice)]["codi_emp"] = str(empresas[0]["codigo"])
            self.__empresas[str(indice)]["nome_emp"] = str(empresas[0]["nome"])
        else:
            print("Mais de um resultado")
            self.__tabela_empresas.selectedItems()[1].setText(str(empresas[0]["codigo"]))
            self.__tabela_empresas.selectedItems()[2].setText(str(empresas[0]["nome"]))
            self.__empresas[str(indice)]["codi_emp"] = str(empresas[0]["codigo"])
            self.__empresas[str(indice)]["nome_emp"] = str(empresas[0]["nome"])

        self.atualiza_status("Dados carregados do Domínio","D")
        self.seleciona_registro()

    def relacionar_rubricas(self):
        indice = self.__tabela_empresas.selectedItems()[0].row()
        self.atualiza_status("Gerando planilha de relações de rubricas...")
        inscricao = self.__tabela_empresas.selectedItems()[0].text()
        esocial = eSocialXML(f"{self.__diretorio_trabalho}\\{inscricao}")
        esocial.carregar_informacoes_xml()
        esocial.gera_excel_relacao(self.__tabela_empresas.selectedItems()[0].text())
        self.atualiza_status("Planilha de rubricas geradas","P")
        self.seleciona_registro()

    def executar_rpa(self):
        self.atualiza_status("Função RPA não configurada")

class eSocialConfiguracoes(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.__window = DialogConfiguracoes()
    
    def init_gui(self):
        """
        Declarar componentes que serão utilizados da interface
        """
        self.__window.setupUi(self)
        self.setWindowTitle('Configuração de credenciais')
        self.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = eSocial()
    window.init_gui()
    app.exec()