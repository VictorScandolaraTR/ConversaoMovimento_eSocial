from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QTableWidgetItem, QMessageBox
from PySide6.QtCore import Signal, QThread, Qt
from PySide6 import QtGui
from sqlalchemy import create_engine, Table, update
import src.utils.components as components
import pandas as pd
import os, json, sys

from src.ui.esocial_unico import Ui_MainWindow as Interface
from src.ui.dialog_configuaracoes import Ui_dialog_configuracioes as DialogConfiguracoes
from src.classes.RPAConfiguracoes import RPAConfiguracoes

from src.esocial import eSocialXML
from src.esocial import get_codi_emp
from src.rpa.rpa import RPA
import src.ui.components_ui as components_ui


class eSocial(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__window = Interface()
        self.__engine = self.criar_banco_operacao()
        self.__parametros = self.carrega_parametros()
        self.__diretorio_trabalho = self.__parametros["diretorio_trabalho"]
        self.__empresas, self.__empresas_em_uso = self.carrega_empresas()

    def init_gui(self):
        """
        Declarar componentes que serão utilizados da interface
        """
        self.__window.setupUi(self)
        self.__widget = self.__window.centralwidget
        self.setWindowTitle('Conversão de Movimentos - e-Social')

        self.__tabela_empresas = self.__window.tableWidget
        self.__edit_inscricao = self.__window.edit_inscricao
        self.__btn_adiciona_empresa = self.__window.btn_adiciona_empresa
        self.__btn_conexoes = self.__window.btn_conexoes
        self.__btn_obtem_dados_esocial = self.__window.btn_obtem_dados_esocial
        self.__btn_obtem_dados_esocial_xml = self.__window.btn_obtem_dados_esocial_xml
        self.__btn_relaciona_empresas_dominio = self.__window.btn_relaciona_empresas_dominio
        self.__btn_relacionar_rubricas = self.__window.btn_relacionar_rubricas
        self.__btn_executa_rpa = self.__window.btn_executa_rpa
        self.__btn_excluir = self.__window.btn_excluir

        self.__tabela_empresas.setColumnWidth(2, 344)
        self.__tabela_empresas.setColumnWidth(3, 200)

        self.__tabela_empresas.clicked.connect(self.seleciona_registro)
        self.__btn_adiciona_empresa.clicked.connect(self.adiciona_empresa)
        self.__btn_conexoes.clicked.connect(self.configura_conexoes)
        self.__btn_obtem_dados_esocial.clicked.connect(self.acessa_portal_esocial)
        self.__btn_obtem_dados_esocial_xml.clicked.connect(self.extrai_dados_esocial)
        self.__btn_relaciona_empresas_dominio.clicked.connect(self.relaciona_empresa_dominio)
        self.__btn_relacionar_rubricas.clicked.connect(self.relacionar_rubricas)
        self.__btn_executa_rpa.clicked.connect(self.executar_rpa)
        self.__btn_excluir.clicked.connect(self.exclui_empresa)

        self.__btn_obtem_dados_esocial.setEnabled(False)
        self.__btn_obtem_dados_esocial_xml.setEnabled(False)
        self.__btn_relaciona_empresas_dominio.setEnabled(False)
        self.__btn_relacionar_rubricas.setEnabled(False)
        self.__btn_executa_rpa.setEnabled(False)
        self.__btn_excluir.setEnabled(False)

        self.atualiza_tabela_empresas()
        self.show()

        if self.__parametros["diretorio_trabalho"]=="":
            self.configura_conexoes()

    def carrega_parametros(self):
        df = pd.read_sql("SELECT * FROM PARAMETROS", con=self.__engine)

        parametros = {}
        for i in range(len(df)):
            parametros = {
                "diretorio_trabalho": df.loc[i, "diretorio_trabalho"],
                "base_dominio": df.loc[i, "base_dominio"],
                "usuario_dominio": df.loc[i, "usuario_dominio"],
                "senha_dominio": df.loc[i, "senha_dominio"],
                "usuario_sgd": df.loc[i, "usuario_sgd"],
                "senha_sgd": df.loc[i, "senha_sgd"],
                "empresa_padrao_rubricas": df.loc[i, "empresa_padrao_rubricas"]
            }

        return parametros

    def criar_banco_operacao(self):
        if os.path.exists(f"src/database/operacao.db"):
            engine = create_engine(f"sqlite:///src/database/operacao.db")
        else:
            engine = create_engine(f"sqlite:///src/database/operacao.db")

            sql_empresas = "CREATE TABLE EMPRESAS( "\
                            "id INTEGER, "\
                            "inscricao VARCHAR, "\
                            "codi_emp INTEGER, "\
                            "nome_emp VARCHAR, "\
                            "status VARCHAR, "\
                            "base_dominio VARCHAR, "\
                            "usuario_dominio VARCHAR, "\
                            "senha_dominio VARCHAR, "\
                            "empresa_padrao_rubricas INTEGER, "\
                            "usuario_esocial VARCHAR, "\
                            "senha_esocial VARCHAR, "\
                            "certificado_esocial VARCHAR, "\
                            "tipo_certificado_esocial VARCHAR(2), "\
                            "usuario_sgd VARCHAR, "\
                            "senha_sgd VARCHAR, "\
                            "ano_conversao VARCHAR)"

            sql_periodos = "CREATE TABLE PERIODOS( "\
                            "inscricao VARCHAR, "\
                            "solicitacao VARCHAR, "\
                            "data_inicial VARCHAR, "\
                            "data_final VARCHAR, "\
                            "status VARCHAR, "\
                            "indice INTEGER)"

            sql_parametros = "CREATE TABLE PARAMETROS( "\
                            "diretorio_trabalho VARCHAR, "\
                            "base_dominio VARCHAR, "\
                            "usuario_dominio VARCHAR, "\
                            "senha_dominio VARCHAR, "\
                            "usuario_sgd VARCHAR, "\
                            "senha_sgd VARCHAR, "\
                            "empresa_padrao_rubricas INTEGER)"
            
            sql_dados_parametros = "INSERT INTO PARAMETROS VALUES ('','','','','','',9999)"
            
            conexao = engine.connect()
            conexao.execute(sql_empresas)
            conexao.execute(sql_periodos)
            conexao.execute(sql_parametros)
            conexao.execute(sql_dados_parametros)

        return engine

    def carrega_empresas(self):
        df = pd.read_sql("SELECT * FROM EMPRESAS ORDER BY id", con=self.__engine)

        empresas = {}

        for i in range(len(df)):
            codi_emp = df.loc[i, "codi_emp"]

            try:
                codi_emp = int(codi_emp)
            except:
                codi_emp = ""
            
            empresas[str(i)] = {
                "inscricao": df.loc[i, "inscricao"],
                "codi_emp": codi_emp,
                "nome_emp": df.loc[i, "nome_emp"],
                "status": df.loc[i, "status"],
                "base_dominio": df.loc[i, "base_dominio"],
                "usuario_dominio": df.loc[i, "usuario_dominio"],
                "senha_dominio": df.loc[i, "senha_dominio"],
                "empresa_padrao_rubricas": df.loc[i, "empresa_padrao_rubricas"],
                "usuario_esocial": df.loc[i, "usuario_esocial"],
                "senha_esocial": df.loc[i, "senha_esocial"],
                "certificado_esocial": df.loc[i, "certificado_esocial"],
                "tipo_certificado_esocial": df.loc[i, "tipo_certificado_esocial"],
                "usuario_sgd": df.loc[i, "usuario_sgd"],
                "senha_sgd": df.loc[i, "senha_sgd"]
            }

        empresas_em_uso = []

        for i in empresas:
            empresas_em_uso.append(empresas[i]["inscricao"])

        return empresas, empresas_em_uso

    def atualiza_tabela_empresas(self):
        quantidade_empresas = len(self.__empresas)

        if (quantidade_empresas == 0):
            return
        else:
            self.__tabela_empresas.setRowCount(quantidade_empresas)

            linha = 0
            while linha < quantidade_empresas:
                self.__tabela_empresas.setItem(linha, 0, QTableWidgetItem(self.__empresas.get(str(linha)).get("inscricao")))
                self.__tabela_empresas.setItem(linha, 1, QTableWidgetItem(str(self.__empresas.get(str(linha)).get("codi_emp"))))
                self.__tabela_empresas.setItem(linha, 2, QTableWidgetItem(self.__empresas.get(str(linha)).get("nome_emp")))

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

                self.__tabela_empresas.setItem(linha, 3, QTableWidgetItem(status))

                linha = linha + 1

    def alerta(self, mensagem, titulo = "Atenção"):
        msg = QMessageBox()
        msg.setWindowTitle(titulo)
        msg.setText(mensagem)
        msg.exec()

    def adiciona_empresa(self):
        os.system(f"mkdir {self.__diretorio_trabalho}")
        proxima_linha = len(self.__empresas)
        id = proxima_linha + 1
        inscricao = self.__edit_inscricao.text()

        if (inscricao == ""):
            self.alerta("Preencha o campo inscrição.","Erro ao adicionar")
            return
        if (inscricao in self.__empresas_em_uso):
            self.alerta("Empresa já cadastrada.", "Erro ao adicionar")
            self.__edit_inscricao.clear()
            return

        os.system(f"mkdir \"{self.__diretorio_trabalho}/{inscricao}\"")
        os.system(f"mkdir \"{self.__diretorio_trabalho}/{inscricao}/downloads\"")
        os.system(f"mkdir \"{self.__diretorio_trabalho}/{inscricao}/eventos\"")
        os.system(f"mkdir \"{self.__diretorio_trabalho}/{inscricao}/importar\"")

        conexao = self.__engine.connect()
        conexao.execute(f"INSERT INTO EMPRESAS (id, inscricao) VALUES ({id},'{inscricao}')")
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

        os.system(f"del /q \"{self.__diretorio_trabalho}/{inscricao}/downloads\"")
        os.system(f"del /q \"{self.__diretorio_trabalho}/{inscricao}/eventos\"")
        os.system(f"del /q \"{self.__diretorio_trabalho}/{inscricao}/importar\"")
        os.system(f"del /q \"{self.__diretorio_trabalho}/{inscricao}\"")
        os.system(f"rmdir \"{self.__diretorio_trabalho}/{inscricao}/downloads\"")
        os.system(f"rmdir \"{self.__diretorio_trabalho}/{inscricao}/eventos\"")
        os.system(f"rmdir \"{self.__diretorio_trabalho}/{inscricao}/importar\"")
        os.system(f"rmdir \"{self.__diretorio_trabalho}/{inscricao}\"")

        self.__empresas, self.__empresas_em_uso = self.carrega_empresas()
        self.atualiza_tabela_empresas()

    def configura_conexoes(self):
        configuracoes = {
            "diretorio_trabalho": self.__parametros["diretorio_trabalho"],
            "base_dominio": self.__parametros["base_dominio"],
            "usuario_dominio": self.__parametros["usuario_dominio"],
            "senha_dominio": self.__parametros["senha_dominio"],
            "empresa_padrao_rubricas": self.__parametros["empresa_padrao_rubricas"],
            "usuario_sgd": self.__parametros["usuario_sgd"],
            "senha_sgd": self.__parametros["senha_sgd"]
        }

        self.__dialog = eSocialConfiguracoes()
        self.__dialog.init_gui(configuracoes)
        self.__dialog.config_run.connect(self.atualiza_configuracoes)

    def atualiza_configuracoes(self, dados):
        diretorio_trabalho = dados["diretorio_trabalho"]
        base_dominio = dados["base_dominio"]
        usuario_dominio = dados["usuario_dominio"]
        senha_dominio = dados["senha_dominio"]
        empresa_padrao_rubricas = dados["empresa_padrao_rubricas"]
        usuario_sgd = dados["usuario_sgd"]
        senha_sgd = dados["senha_sgd"]

        sql = "UPDATE PARAMETROS SET diretorio_trabalho = '{diretorio_trabalho}', "\
                "base_dominio = '{base_dominio}', "\
                "usuario_dominio = '{usuario_dominio}',"\
                "senha_dominio = '{senha_dominio}', "\
                "empresa_padrao_rubricas = '{empresa_padrao_rubricas}', "\
                "usuario_sgd = '{usuario_sgd}', "\
                "senha_sgd = '{senha_sgd}'"

        conexao = self.__engine.connect()
        conexao.execute(sql.format(
            diretorio_trabalho = diretorio_trabalho,
            base_dominio = base_dominio,
            usuario_dominio = usuario_dominio,
            senha_dominio = senha_dominio,
            empresa_padrao_rubricas = empresa_padrao_rubricas,
            usuario_sgd = usuario_sgd,
            senha_sgd = senha_sgd
        ))

        self.__parametros = self.carrega_parametros()
        self.__diretorio_trabalho = self.__parametros["diretorio_trabalho"]

    def seleciona_registro(self):
        if self.__diretorio_trabalho=="":
            self.alerta("Configure os parâmetros de conexão antes de avançar.")
            self.configura_conexoes()
            return
        indice = self.__tabela_empresas.selectedItems()[0].row()
        status = self.__empresas[str(indice)]["status"]

        match status:
            case "" | None:
                self.__btn_obtem_dados_esocial.setEnabled(True)
                self.__btn_obtem_dados_esocial_xml.setEnabled(True)
                self.__btn_relaciona_empresas_dominio.setEnabled(True)
                self.__btn_relacionar_rubricas.setEnabled(False)
                self.__btn_executa_rpa.setEnabled(False)
                self.__btn_excluir.setEnabled(True)
            case "E":
                self.__btn_obtem_dados_esocial.setEnabled(True)
                self.__btn_obtem_dados_esocial_xml.setEnabled(True)
                self.__btn_relaciona_empresas_dominio.setEnabled(True)
                self.__btn_relacionar_rubricas.setEnabled(False)
                self.__btn_executa_rpa.setEnabled(False)
                self.__btn_excluir.setEnabled(True)
                self.__tabela_empresas.selectedItems()[3].setText("Dados carregados do e-Social")
            case "D":
                self.__btn_obtem_dados_esocial.setEnabled(True)
                self.__btn_obtem_dados_esocial_xml.setEnabled(True)
                self.__btn_relaciona_empresas_dominio.setEnabled(True)
                self.__btn_relacionar_rubricas.setEnabled(True)
                self.__btn_executa_rpa.setEnabled(False)
                self.__btn_excluir.setEnabled(True)
                self.__tabela_empresas.selectedItems()[3].setText("Dados carregados do Domínio")
            case "P":
                self.__btn_obtem_dados_esocial.setEnabled(True)
                self.__btn_obtem_dados_esocial_xml.setEnabled(True)
                self.__btn_relaciona_empresas_dominio.setEnabled(True)
                self.__btn_relacionar_rubricas.setEnabled(True)
                self.__btn_executa_rpa.setEnabled(True)
                self.__btn_excluir.setEnabled(True)
                self.__tabela_empresas.selectedItems()[3].setText("Planilha de rubricas geradas")
            case "R":
                self.__btn_obtem_dados_esocial.setEnabled(True)
                self.__btn_obtem_dados_esocial_xml.setEnabled(True)
                self.__btn_relaciona_empresas_dominio.setEnabled(True)
                self.__btn_relacionar_rubricas.setEnabled(True)
                self.__btn_executa_rpa.setEnabled(True)
                self.__btn_excluir.setEnabled(True)
                self.__tabela_empresas.selectedItems()[3].setText("Processo concluído")

    def atualiza_status(self, status, status_bd=""):
        self.__tabela_empresas.selectedItems()[3].setText(status)
        inscricao = self.__tabela_empresas.selectedItems()[0].text()
        indice = self.__tabela_empresas.selectedItems()[0].row()

        if(status_bd!=""):
            self.__empresas[str(indice)]["status"] = status_bd
            conexao = self.__engine.connect()
            conexao.execute(f"UPDATE EMPRESAS SET status = '{status_bd}' WHERE inscricao = '{inscricao}'")

    def extrai_dados_esocial(self):
        inscricao = self.__tabela_empresas.selectedItems()[0].text()
        esocial = eSocialXML(self.__diretorio_trabalho, inscricao, self.__parametros)
        esocial.completar_inscricao()
        
        mensagem_alerta = "Você selecionou a conversão dos dados através de arquivos XML fornecidos por você mesmo ao invés de realizar o download do Portal e-Social."\
            " Certifique-se de atender os seguintes requisitos:\n\n"\
            "1- Copie todos os arquivos XML para um diretório\n"\
            "2- Certifique-se de que nesta pasta estejam apenas os arquivos XML\n\n"\
            "Será aberta uma janela para solicitar que você informe a localização da pasta dos eventos."
        self.alerta(mensagem_alerta)
        caminho = components.ask_directory(self.__widget, "Selecione a pasta com os arquivos XML")

        os.system(f"del /q \"{esocial.DIRETORIO_XML}\"")
        os.system(f"copy  \"{caminho}\" \"{esocial.DIRETORIO_XML}\"")
        
        self.atualiza_status("Lendo informações...")
        esocial.carregar_informacoes_xml()

        self.atualiza_status("Dados carregados do e-Social","E")
        self.seleciona_registro()

    def acessa_portal_esocial(self):
        indice = str(self.__tabela_empresas.selectedItems()[0].row())
        inscricao = self.__tabela_empresas.selectedItems()[0].text()
        esocial = eSocialXML(self.__diretorio_trabalho, inscricao, self.__parametros)
        esocial.completar_inscricao()
        self.atualiza_status("Buscando dados do e-Social...")
        mensagem_alerta = "IMPORTANTE!\n"\
            "Será aberto um navegador no portal e-Social para que você selecione o certificado da empresa correta para autenticação.\n"\
            "Após a autenticação, o navegador será minimizado e será encerrado automaticamente após o fim do processo."
        self.alerta(mensagem_alerta)

        lotes, periodos_consultados = esocial.baixar_dados_esocial()

        if(lotes["status"]):
            conexao = self.__engine.connect()
            conexao.execute(f"DELETE FROM PERIODOS WHERE inscricao = '{inscricao}'")

            for solicitacao in periodos_consultados:
                data_inicial = periodos_consultados[solicitacao]["data_inicial"]
                data_final = periodos_consultados[solicitacao]["data_final"]
                status = periodos_consultados[solicitacao]["status"]
                indice = periodos_consultados[solicitacao]["indice"]

                conexao.execute(f"INSERT INTO PERIODOS (inscricao, solicitacao, data_inicial, data_final, status, indice) "\
                                f"VALUES ('{inscricao}','{solicitacao}','{data_inicial}','{data_final}','{status}',{indice})")

            lotes_erro = lotes["Erro"]
            lotes_vazios = lotes ["Nenhum evento encontrado"]
            lotes_baixados = lotes["Disponível para Baixar"]
            total_lotes = lotes_erro + lotes_vazios + lotes_baixados
            print(
                f"Acesso ao portal encerrado.\n"\
                f"Consultas realizadas: {total_lotes}\n"\
                f"Consultas com resultado: {lotes_baixados}\n"\
                f"Consultas sem resultado: {lotes_vazios}\n"\
                f"Consultas com erro: {lotes_erro}\n"\
            )
        
            self.atualiza_status("Lendo informações...")
            #esocial.extrair_arquivos_xml()
            esocial.carregar_informacoes_xml()

            self.atualiza_status("Dados carregados do e-Social","E")
            self.seleciona_registro()
        else:
            mensagem_alerta = f"Estamos enfrentando dificuldade em acessar o portal e-Social.\nFavor tentar novamente mais tarde."
            titulo = "Erro ao consultar informações do portal e-Social"
            self.alerta(mensagem_alerta,titulo)

            self.atualiza_status("Erro ao baixar dados do e-Social")


    def relaciona_empresa_dominio(self):
        self.atualiza_status("Consultando banco de dados Domínio...")
        indice = str(self.__tabela_empresas.selectedItems()[0].row())
        inscricao = self.__tabela_empresas.selectedItems()[0].text()
        
        esocial = eSocialXML(self.__diretorio_trabalho, inscricao, self.__parametros)

        empresas = esocial.relaciona_empresas(str(self.__tabela_empresas.selectedItems()[0].text()))
        indice = self.__tabela_empresas.selectedItems()[0].row()

        if (len(empresas) == 1):
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

        conexao = self.__engine.connect()
        conexao.execute("UPDATE EMPRESAS SET codi_emp = {codi_emp}, nome_emp = '{nome_emp}' "\
                        "WHERE inscricao = '{inscricao}'".format(
                            codi_emp = empresas[0]["codigo"],
                            nome_emp = empresas[0]["nome"],
                            inscricao = inscricao
                        ))
        self.atualiza_status("Dados carregados do Domínio","D")
        self.seleciona_registro()

    def relacionar_rubricas(self):
        self.atualiza_status("Gerando planilha de relações de rubricas...")

        inscricao = self.__tabela_empresas.selectedItems()[0].text()
        esocial = eSocialXML(self.__diretorio_trabalho, inscricao, self.__parametros)
        esocial.carregar_informacoes_xml()
        esocial.gera_excel_relacao(self.__tabela_empresas.selectedItems()[0].text())
        self.atualiza_status("Planilha de rubricas geradas", "P")
        self.seleciona_registro()

    def executar_rpa(self):
        inscricao = self.__tabela_empresas.selectedItems()[0].text()

        esocial = eSocialXML(self.__diretorio_trabalho, inscricao, self.__parametros)
        codi_emp = str(get_codi_emp(self.__engine, inscricao))

        relacao_empregados = esocial.relaciona_empregados()

        # gerar arquivos cadastrais
        esocial.carregar_informacoes_xml()
        esocial.gerar_afastamentos_importacao(inscricao, codi_emp, relacao_empregados)
        esocial.gerar_ferias_importacao(inscricao, codi_emp, relacao_empregados)

        # gerar arquivos para importação de lançamentos
        data_vacation = esocial.gerar_arquivos_saida(inscricao, codi_emp, relacao_empregados)

        # gerar férias e rescisões que irão ser calculadas pelo RPA
        esocial.save_rescission(inscricao, codi_emp, relacao_empregados)
        esocial.save_vacation(data_vacation)

        # Iniciar RPA
        self.__dialog = RPAConfiguracoes()
        self.__dialog.init_gui()
        self.__dialog.config_run.connect(self.iniciar_rpa)

    def iniciar_rpa(self, local, machines):
        def finish_process(success, message):
            print(success, 'ERROR:    ', message)
            if success:
                components_ui.message_sucess(self.__widget, 'Processo finalizado!')
                self.set_progress('Processo completo...', 100)
            else:
                components_ui.message_error(self.__widget, message)
                self.set_progress('Erro ao executar RPA...', 0)

        def update_progress(progress):
            self.set_progress(progress[0], progress[1])

        inscricao = self.__tabela_empresas.selectedItems()[0].text()
        indice = str(self.__tabela_empresas.selectedItems()[0].row())

        esocial = eSocialXML(self.__diretorio_trabalho, inscricao, self.__parametros)

        codi_emp = str(get_codi_emp(self.__engine, inscricao))
        base_dominio = self.__parametros["base_dominio"]
        usuario_dominio = self.__parametros["usuario_dominio"]
        senha_dominio = self.__parametros["senha_dominio"]
        usuario_sgd = self.__parametros["usuario_sgd"]
        senha_sgd = self.__parametros["senha_sgd"]
        year = esocial.get_year_conversion()
        init_competence = f'01/{year}'
        end_competence = f'12/{year}'

        # Iniciar o RPA em uma Thread separada para não travar a interface
        self.thread2 = QThread()
        self.rpa = RPA()
        self.rpa.init(f"{self.__diretorio_trabalho}\\{inscricao}\\rpa", base_dominio, usuario_dominio, senha_dominio, usuario_sgd, senha_sgd)

        self.rpa.moveToThread(self.thread2)

        # validar se nenhum ponto cadastral pode interferir nos cálculos
        if self.rpa.invalid_cadastral_conversion():
            print('parte cadastral inválida')
            return False

        self.rpa.prepare(codi_emp, init_competence, end_competence)
        self.rpa.prepare_machines_for_calc(local, machines)

        self.thread2.started.connect(self.rpa.start)
        self.rpa.finished.connect(self.thread2.quit)
        self.thread2.finished.connect(self.thread2.deleteLater)
        self.thread2.start()

        # vai recebendo sinais conforme avança o processamento
        self.rpa.progress.connect(update_progress)
        self.rpa.success.connect(finish_process)

    def set_progress(self, text, percent):
        print(f'ATUALIZACAO: {percent}%, {text}')

class eSocialConfiguracoes(QMainWindow):
    config_run = Signal(dict)

    def __init__(self):
        super().__init__()
        self.__window = DialogConfiguracoes()

    def init_gui(self, configuracao):
        """
        Declarar componentes que serão utilizados da interface
        """
        self.__window.setupUi(self)
        self.setWindowTitle('Configuração de credenciais')

        self.__btn_diretorio_trabalho = self.__window.btn_diretorio_trabalho
        self.__btn_cancelar = self.__window.btn_concertar_configuracoes
        self.__btn_confirmar_configuracoes = self.__window.btn_confirmar_configuracoes

        self.__edit_diretorio_trabalho = self.__window.edit_diretorio_trabalho
        self.__edit_banco_dominio = self.__window.edit_banco_dominio
        self.__edit_usuario_dominio = self.__window.edit_usuario_dominio
        self.__edit_senha_dominio = self.__window.edit_senha_dominio
        self.__edit_empresa_rubricas_dominio = self.__window.edit_empresa_rubricas_dominio
        
        self.__edit_usuario_sgd = self.__window.edit_usuario_sgd
        self.__edit_senha_sgd = self.__window.edit_senha_sgd

        self.__btn_diretorio_trabalho.clicked.connect(self.busca_diretorio)
        self.__btn_cancelar.clicked.connect(self.close)
        self.__btn_confirmar_configuracoes.clicked.connect(self.salvar)

        self.__edit_diretorio_trabalho.setText(configuracao["diretorio_trabalho"])
        self.__edit_banco_dominio.setText(configuracao["base_dominio"])
        self.__edit_usuario_dominio.setText(configuracao["usuario_dominio"])
        self.__edit_senha_dominio.setText(configuracao["senha_dominio"])
        self.__edit_empresa_rubricas_dominio.setText(str(configuracao["empresa_padrao_rubricas"]))
        self.__edit_usuario_sgd.setText(configuracao["usuario_sgd"])
        self.__edit_senha_sgd.setText(configuracao["senha_sgd"])

        self.show()

    def busca_diretorio(self):
        path = components.ask_directory(self.window(), 'Selecione o diretório de trabalho.')
        self.__edit_diretorio_trabalho.setText(path)

    def alerta(self, mensagem, titulo = "Atenção"):
        msg = QMessageBox()
        msg.setWindowTitle(titulo)
        msg.setText(mensagem)
        msg.exec()

    def salvar(self):
        if self.__edit_diretorio_trabalho.text()=="":
            self.alerta("Preencha o diretório de trabalho.","Atenção")
            self.busca_diretorio()

        dados = {
            "diretorio_trabalho": self.__edit_diretorio_trabalho.text(),
            "base_dominio": self.__edit_banco_dominio.text(),
            "usuario_dominio": self.__edit_usuario_dominio.text(),
            "senha_dominio": self.__edit_senha_dominio.text(),
            "empresa_padrao_rubricas": self.__edit_empresa_rubricas_dominio.text(),
            "usuario_sgd": self.__edit_usuario_sgd.text(),
            "senha_sgd": self.__edit_senha_sgd.text()
        }
        
        self.config_run.emit(dados)
        self.close()


if __name__ == '__main__':
    app = QApplication([])
    window = eSocial()
    window.init_gui()
    app.exec()
