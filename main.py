from PySide6.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from src.esocial import eSocialXML
from src.ui.esocial_unico import Ui_MainWindow as Interface
import os, json, sys

class eSocial(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.__window = Interface()
        self.__esocial = eSocialXML("xml")
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
        self.__btn_obtem_dados_esocial = self.__window.btn_obtem_dados_esocial
        self.__btn_relaciona_empresas_dominio = self.__window.btn_relaciona_empresas_dominio
        self.__btn_relacionar_rubricas = self.__window.btn_relacionar_rubricas
        self.__btn_executa_rpa = self.__window.btn_executa_rpa

        self.__tabela_empresas.setColumnWidth(2,344)
        self.__tabela_empresas.setColumnWidth(3,200)

        self.__tabela_empresas.clicked.connect(self.seleciona_registro)
        self.__btn_adiciona_empresa.clicked.connect(self.adiciona_empresa)
        self.__btn_obtem_dados_esocial.clicked.connect(self.acessa_portal_esocial)
        self.__btn_relaciona_empresas_dominio.clicked.connect(self.relaciona_empresa_dominio)
        self.__btn_relacionar_rubricas.clicked.connect(self.relacionar_rubricas)
        self.__btn_executa_rpa.clicked.connect(self.executar_rpa)

        self.__btn_obtem_dados_esocial.setEnabled(False)
        self.__btn_relaciona_empresas_dominio.setEnabled(False)
        self.__btn_relacionar_rubricas.setEnabled(False)
        self.__btn_executa_rpa.setEnabled(False)

        self.atualiza_tabela_empresas()
        self.show()

    def carrega_empresas(self):
        try:
            f = open(f"{self.__esocial.DIRETORIO_RAIZ}\\empresas.json","r")
            empresas_texto = f.readline()
            f.close
            empresas = json.loads(empresas_texto)
            
            empresas_em_uso = []

            for i in empresas:
                empresas_em_uso.append(empresas[i]["inscricao"])

            return empresas, empresas_em_uso
        except:
            return {}, []

    def salva_empresas(self):
        f = open(f"{self.__esocial.DIRETORIO_RAIZ}\\empresas.json","w")
        f.write(json.dumps(self.__empresas))
        f.close

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
                    case "e-Social":
                        status = "Dados carregados do e-Social"
                    case "Dominio":
                        status = "Dados carregados do Domínio"
                    case "Rubricas":
                        status = "Planilha de rubricas geradas"
                    case "RPA":
                        status = "Processo concluído"

                self.__tabela_empresas.setItem(linha, 3, QtWidgets.QTableWidgetItem(status))

                linha = linha + 1
    
    def adiciona_empresa(self):
        proxima_linha = len(self.__empresas)
        inscricao = self.__edit_inscricao.text()

        if(inscricao==""):
            print("Preencha o campo inscrição.")
            return
        if(inscricao in self.__empresas_em_uso):
            print("Empresa já cadastrada.")
            return

        self.__empresas[str(proxima_linha)] = {
            "inscricao": inscricao,
            "codi_emp": "",
            "nome_emp": "",
            "status": "",
            "configuracoes":{
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
        }

        self.__empresas_em_uso.append(inscricao)
        
        self.__edit_inscricao.setText("")
        self.salva_empresas()
        self.atualiza_tabela_empresas()

    def seleciona_registro(self):
        indice = self.__tabela_empresas.selectedItems()[0].row()
        status = self.__empresas[str(indice)]["status"]

        match status:
            case "":
                self.__btn_obtem_dados_esocial.setEnabled(True)
                self.__btn_relaciona_empresas_dominio.setEnabled(False)
                self.__btn_relacionar_rubricas.setEnabled(False)
                self.__btn_executa_rpa.setEnabled(False)
            case "e-Social":
                self.__btn_obtem_dados_esocial.setEnabled(True)
                self.__btn_relaciona_empresas_dominio.setEnabled(True)
                self.__btn_relacionar_rubricas.setEnabled(False)
                self.__btn_executa_rpa.setEnabled(False)
                self.__tabela_empresas.selectedItems()[3].setText("Dados carregados do e-Social")
            case "Dominio":
                self.__btn_obtem_dados_esocial.setEnabled(True)
                self.__btn_relaciona_empresas_dominio.setEnabled(True)
                self.__btn_relacionar_rubricas.setEnabled(True)
                self.__btn_executa_rpa.setEnabled(False)
                self.__tabela_empresas.selectedItems()[3].setText("Dados carregados do Domínio")
            case "Rubricas":
                self.__btn_obtem_dados_esocial.setEnabled(True)
                self.__btn_relaciona_empresas_dominio.setEnabled(True)
                self.__btn_relacionar_rubricas.setEnabled(True)
                self.__btn_executa_rpa.setEnabled(False)
                self.__tabela_empresas.selectedItems()[3].setText("Planilha de rubricas geradas")
            case "RPA":
                self.__btn_obtem_dados_esocial.setEnabled(True)
                self.__btn_relaciona_empresas_dominio.setEnabled(True)
                self.__btn_relacionar_rubricas.setEnabled(True)
                self.__btn_executa_rpa.setEnabled(True)
                self.__tabela_empresas.selectedItems()[3].setText("Processo concluído")

    def atualiza_status(self, status):
        self.__tabela_empresas.selectedItems()[3].setText(status)
    
    def acessa_portal_esocial(self):
        self.atualiza_status("Buscando dados do e-Social...")
        self.__esocial.configura_conexao_esocial("usuario","senha","certificado")
        self.__esocial.baixar_dados_esocial()
        
        self.atualiza_status("Lendo informações...")
        self.__esocial.extrair_arquivos_xml()
        self.__esocial.carregar_informacoes_xml()

        self.atualiza_status("Dados carregados do e-Social")
        indice = self.__tabela_empresas.selectedItems()[0].row()
        self.__empresas[str(indice)]["status"] = "e-Social"
        self.salva_empresas()
        self.seleciona_registro()

    def relaciona_empresa_dominio(self):
        self.atualiza_status("Consultando banco de dados Domínio...")
        self.__esocial.configura_conexao_dominio("movto_esocial","EXTERNO","123456")
        empresas = self.__esocial.relaciona_empresas(str(self.__tabela_empresas.selectedItems()[0].text()))
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

        self.atualiza_status("Dados carregados do Domínio")
        self.__empresas[str(indice)]["status"] = "Dominio"
        self.salva_empresas()

    def relacionar_rubricas(self):
        indice = self.__tabela_empresas.selectedItems()[0].row()
        self.atualiza_status("Gerando planilha de relações de rubricas...")
        self.__esocial.carregar_informacoes_xml()
        self.__esocial.gera_excel_relacao(self.__tabela_empresas.selectedItems()[0].text())
        self.atualiza_status("Planilha de rubricas geradas")
        self.__empresas[str(indice)]["status"] = "Rubricas"
        self.salva_empresas()

    def executar_rpa(self):
        self.atualiza_status("Função RPA não configurada")

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = eSocial()
    window.init_gui()
    app.exec()

'''os.system("cls")
esocial = eSocialXML("xml")
esocial.carregar_informacoes_xml()

relacao_empresas = esocial.relaciona_empresas()
relacao_empregados = esocial.relaciona_empregados()

esocial.gera_excel_relacao(relacao_empresas)

esocial.gerar_afastamentos_importacao()
esocial.gerar_ferias_importacao()

f = open("s1010.json","w")
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