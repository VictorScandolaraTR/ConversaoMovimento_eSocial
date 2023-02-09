from os.path import split, isdir
from sys import exc_info
import socket
from shutil import unpack_archive, rmtree
import autoit
from os import mkdir
from pathlib import Path
import tkinter as tk
from threading import Thread
import logging
import json

from src.database.Sybase import Sybase
from src.classes.Table import Table
from src.classes.StorageData import StorageData
from src.rpa.check_functions_rpa import check_companies_calc
from src.database.SQLite_tables import (
    DominioFerias,
    DominioRescisao
)
from src.utils.functions import *
from src.rpa.rpa_utils import *


ignore_employees = {}
debug = False


class Agent:
    DEFAULT_PORT = 1112
    SIZE_BUFFER_PACKETS = 10240
    DEFAULT_USER = 'GERENTE'
    DEFAULT_PASSWORD = 'gerente'
    BASE_NAME_USER = 'Conversao'
    DEFAULT_PASSWORD_CREATED = '123456'
    path_def = '.\\def_tables.db'

    def config_log(self):
        """
        Configura o log do RPA dos clientes
        """
        # Configurando o LOG
        log_format = '%(asctime)s:%(levelname)s:%(filename)s:%(message)s'
        logging.basicConfig(filename='logRPA.log',
                            # w -> sobrescreve o arquivo a cada log
                            # a -> não sobrescreve o arquivo
                            filemode='w',
                            level=logging.DEBUG,
                            format=log_format)
        self.logger = logging.getLogger('root')

    def print_log(self, type, message):
        if type == 'critical':
            self.logger.critical(message)
        elif type == 'error':
            self.logger.error(message)
        elif type == 'warning':
            self.logger.warning(message)
        else:
            self.logger.info(message)

    def await_data(self):
        """
        Função que fica em stand-by até que os dados sejam enviados pelo host
        e retorna o IP do host
        """
        self.config_log()
        # abrir um socket de rede para o conversor "saber" que essa é uma máquina que pode ser utilizada
        self.print_log("info", "Aguardando dados")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', self.DEFAULT_PORT))
        sock.listen(5)
        conn, address = sock.accept()
        conn.close()
        sock.close()

        # abrir um socket para esperar um sinal de quando será enviado os dados
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', self.DEFAULT_PORT))
        sock.listen(5)
        conn, address = sock.accept()
        ip_address = address[0]
        conn.close()
        sock.close()

        # abrir conexão com o host para envio dos dados
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip_address, self.DEFAULT_PORT))
        self.create_folder('.\\data')
        with open('.\\data\\recebido.zip', 'wb') as file_receive:
            while True:
                data = sock.recv(self.SIZE_BUFFER_PACKETS)
                if not data:
                    break

                file_receive.write(data)

        sock.close()
        return ip_address

    def extract_data_send(self):
        self.print_log("info", "Extraindo dados para a pasta data_calc")
        """
        Extrai os dados enviados para uma pasta com nome "data_calc"
        """
        try:
            unpack_archive('.\\data\\recebido.zip', '.\\data\\conversao')
            return True
        except:
            return False

    def start(self, ip_host, path_run, calculate):
        """
        Função que faz todo os cálculos e mantém conexão com o host
        """
        try:
            self.config_log()
            sleep(2)
            self.socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_connection.connect((ip_host, self.DEFAULT_PORT))

            self.__path_run = path_run

            # carrega o arquivo de configuração
            conf_file = json.load(open(f'{self.__path_run}\\run.conf'))
            self.__init_competence = datetime.strptime(conf_file['init_competence'], '%d/%m/%Y')
            self.__end_competence = datetime.strptime(conf_file['end_competence'], '%d/%m/%Y')
            self.__database = conf_file['database']
            self.__username = conf_file['username']
            self.__password = conf_file['password']
            self.__sgd_username = conf_file['sgd_username']
            self.__sgd_password = conf_file['sgd_password']
            self.__ip_host = ip_host
            self.__system_user = ''

            competences = self.read_lancamentos()

            # criar um caminho temporário que será utilizado posteriormente
            self.create_folder(f'{self.__path_run}\\Temp')

            while True:
                if debug:
                    print('esperando dados')

                # recebe os dados enviados do host para a estação
                request = self.socket_connection.recv(self.SIZE_BUFFER_PACKETS).decode('utf-8')

                if not request:
                    break

                # os dados vem do host como se fosse um JSON
                data = json.loads(request)

                # variáveis para ditar qual ação deve ser executada
                import_events = False
                import_removals = False
                import_vacation = False
                calc_data = False
                open_dominio = False
                create_users = False
                finish_process = False
                self.__company = 0

                if 'create_users' in data['action']:
                    open_dominio = True
                    create_users = True
                    number_users = data['number_users']
                elif 'open_dominio' in data['action']:
                    open_dominio = True
                    user = data['user']
                    password = data['password']
                elif 'import_events' in data['action']:
                    import_events = True
                elif 'import_removals' in data['action']:
                    import_removals = True
                elif 'import_vacation' in data['action']:
                    import_vacation = True
                elif 'finish_process' in data['action']:
                    finish_process = True
                elif 'calc' in data['action']:
                    self.__company = int(data['current_company'])
                    calc_data = True
                elif 'quit' in data['action']:
                    self.close_dominio()
                    break

                self.__companies_calc = data['companies_calc']

                if open_dominio:
                    if create_users:
                        if not debug:
                            self.__system_user = str(self.DEFAULT_USER)
                            self.open_dominio(self.DEFAULT_USER, self.DEFAULT_PASSWORD)
                        else:
                            print(f'abrir com usuário {self.DEFAULT_USER} e senha {self.DEFAULT_PASSWORD}')
                            sleep(5)

                        if not debug:
                            self.create_users(number_users)
                        else:
                            print('criar usuários')
                            sleep(5)
                    else:
                        if not debug:
                            self.__system_user = str(user)
                            self.open_dominio(user, password)
                        else:
                            print(f'abrir com usuário {user} e senha {password}')
                            sleep(5)

                # importação de rubricas e lançamentos
                if import_events:
                    if not debug:
                        self.open_importacao_sistemas_concorrentes(self.__sgd_username, self.__sgd_password)
                        autoit.send('{ESC}')
                        sleep(1)

                        self.open_importacao_sistemas_concorrentes(self.__sgd_username, self.__sgd_password)
                        autoit.send('{ESC}')
                        sleep(1)

                        self.execute_sql(f'{self.__path_run}\\SQLs\\importacao_lancamentos.sql')

                    self.send_status(self.__company, 'progress', message=f"Início da importação de lançamentos",
                                     only_log=True)

                    if not debug:
                        self.importation_data(self.__sgd_username, self.__sgd_password, f'{self.__path_run}\\Importar')
                    else:
                        print('importar lançamentos de eventos')
                        sleep(10)

                    self.send_status(self.__company, 'progress', message=f"Fim da importação de lançamentos",
                                     only_log=True)

                # preparar dados de férias e afastamentos
                if import_vacation or import_removals or finish_process:
                    if not debug:
                        self.__data_vacation = Table('FOFERIAS_GOZO', file=f'{self.__path_run}\\prontos\\FOFERIAS_GOZO.txt', path_def=self.path_def).items()
                        self.__data_removals = Table('FOAFASTAMENTOS_IMPORTACAO', file=f'{self.__path_run}\\prontos\\FOAFASTAMENTOS_IMPORTACAO.txt', path_def=self.path_def).items()

                        vacation_import, removals_import = self.remove_entries(self.__data_vacation, self.__data_removals)
                        removals_import_last = self.separate_data_removals(self.__data_removals)

                # importar afastamentos
                if import_removals:
                    if not debug:
                        print_to_import(f'{self.__path_run}\\Temp\\FOAFASTAMENTOS_IMPORTACAO.txt', removals_import)
                        self.execute_sql(f'{self.__path_run}\\SQLs\\importacao_afastamentos.sql')

                    self.send_status(self.__company, 'progress', message=f"Início da importação de afastamentos",
                                     only_log=True)

                    if not debug:
                        self.importation_data(self.__sgd_username, self.__sgd_password, f'{self.__path_run}\\Temp',
                                              layout='Importacao afastamentos')
                    else:
                        print('importar afastamentos')
                        sleep(10)

                    self.send_status(self.__company, 'progress', message=f"Fim da importação de afastamentos",
                                     only_log=True)

                # importar gozos de férias anteriores as competencias que vão ser calculadas
                if import_vacation:
                    if not debug:
                        self.open_importacao_sistemas_concorrentes(self.__sgd_username, self.__sgd_password)
                        autoit.send('{ESC}')
                        sleep(1)

                        self.open_importacao_sistemas_concorrentes(self.__sgd_username, self.__sgd_password)
                        autoit.send('{ESC}')
                        sleep(1)

                        print_to_import(f'{self.__path_run}\\Temp\\FOFERIAS_GOZO.txt', vacation_import)
                        self.execute_sql(f'{self.__path_run}\\SQLs\\importacao_gozo.sql')

                    self.send_status(self.__company, 'progress', message=f"Início da importação de gozo de férias",
                                     only_log=True)

                    if not debug:
                        self.importation_data(self.__sgd_username, self.__sgd_password, f'{self.__path_run}\\Temp')
                    else:
                        print('importar gozo de férias')
                        sleep(10)

                    self.send_status(self.__company, 'progress', message=f"Fim da importação de gozo de férias",
                                     only_log=True)

                if not debug:
                    sybase = Sybase(self.__database, self.__username, self.__password)
                    connection = sybase.connect()

                    if not connection:
                        self.send_status(self.__company, 'error', message='Erro de conexão com banco de dados Domínio')

                    sybase.close_connection(connection)

                if calc_data:
                    self.send_status(self.__company, 'progress',
                                     message=f"Início dos cálculos da empresa {self.__company}", only_log=True)
                    if int(self.__company) in competences.keys():

                        if not debug:
                            self.active_company(self.__company)
                            self.open_calc_screen()

                        ordered_competences = order_dates(competences[int(self.__company)].keys())
                        for date_competence in ordered_competences:
                            competence = date_competence.strftime('%d/%m/%Y')

                            if self.competence_is_valid(competence, self.__init_competence, self.__end_competence):
                                if not debug:
                                    imported_events = False
                                    first_calc = True
                                    calc_rescision = False
                                    calc_additional_rescission = False

                                    while True:
                                        if first_calc:
                                            data = competences[int(self.__company)][competence]

                                            # salvar dados para calcular rescisões posteriormente
                                            data_rescission = competences[int(self.__company)][competence]
                                            data_additional_rescission = competences[int(self.__company)][competence]
                                        else:
                                            if not imported_events:
                                                item_entries = self.generate_item_entries(competence,
                                                                                          int(self.__company))
                                                if item_entries:
                                                    self.open_importacao_sistemas_concorrentes(self.__sgd_username,
                                                                                               self.__sgd_password)
                                                    autoit.send('{ESC}')
                                                    sleep(1)

                                                    self.open_importacao_sistemas_concorrentes(self.__sgd_username,
                                                                                               self.__sgd_password)
                                                    autoit.send('{ESC}')
                                                    sleep(1)

                                                    self.execute_sql(
                                                        f'{self.__path_run}\\SQLs\\importacao_lancamentos_ferias.sql')
                                                    print_to_import(
                                                        f'{self.__path_run}\\Temp\\FOFERIAS_LANCAMENTOS.TXT',
                                                        item_entries)
                                                    self.importation_data(self.__sgd_username, self.__sgd_password,
                                                                          f'{self.__path_run}\\Temp')
                                                    imported_events = True

                                            sybase = Sybase(self.__database, self.__username, self.__password)
                                            connection = sybase.connect()

                                            if not connection:
                                                self.send_status(self.__company, 'error',
                                                                 message='Erro de conexão com banco de dados Domínio')

                                            generated_rubrics = sybase.select_rubrics_generated(connection,
                                                                                                int(self.__company),
                                                                                                competence)
                                            data = generated_rubrics
                                            sybase.close_connection(connection)

                                            if generated_rubrics:
                                                self.execute_sql(f'{self.__path_run}\\SQLs\\ajuste_rubricas.sql')
                                            else:
                                                if not calc_rescision:
                                                    calc_rescision = True
                                                    data = data_rescission
                                                else:
                                                    if not calc_additional_rescission:
                                                        calc_additional_rescission = True
                                                        data = data_additional_rescission
                                                    else:
                                                        break

                                        if calc_rescision and not calc_additional_rescission:
                                            if 100 in data and 100 in calculate:
                                                self.calculate_rescission(data[100], company=self.__company)

                                        elif calc_rescision and calc_additional_rescission:
                                            if 42 in data and 42 in calculate:
                                                self.calculate_additional_rescission(data[42], company=self.__company)
                                        else:
                                            if 51 in data and 51 in calculate:
                                                for date_payment in data[51]:
                                                    employees = []
                                                    for employee in data[51][date_payment]:
                                                        if str(self.__company) in ignore_employees.keys():
                                                            if str(employee) in ignore_employees[str(self.__company)]:
                                                                continue
                                                        employees.append(str(employee))

                                                    employees_paste = ', '.join(employees)
                                                    self.calculate_competence(competence, 51, date_payment,
                                                                              employees_paste, first_calc)

                                            if 41 in data and 41 in calculate:
                                                for date_payment in data[41]:
                                                    employees = []
                                                    for employee in data[41][date_payment]:
                                                        if str(self.__company) in ignore_employees.keys():
                                                            if str(employee) in ignore_employees[str(self.__company)]:
                                                                continue

                                                        employees.append(str(employee))

                                                    employees_paste = ', '.join(employees)
                                                    self.calculate_competence(competence, 41, date_payment,
                                                                              employees_paste, first_calc)

                                            if 60 in data and 60 in calculate:
                                                self.calculate_vacation(data[60], recalculate=imported_events,
                                                                        company=int(self.__company),
                                                                        competence=competence)

                                            if 52 in data and 52 in calculate:
                                                for date_payment in data[52]:
                                                    employees = []
                                                    for employee in data[52][date_payment]:
                                                        if str(self.__company) in ignore_employees.keys():
                                                            if str(employee) in ignore_employees[str(self.__company)]:
                                                                continue

                                                        employees.append(str(employee))

                                                    employees_paste = ', '.join(employees)
                                                    self.calculate_competence(competence, 52, date_payment,
                                                                              employees_paste, first_calc)

                                            if 11 in data and 11 in calculate:
                                                for date_payment in data[11]:
                                                    employees = []
                                                    for employee in data[11][date_payment]:
                                                        if str(self.__company) in ignore_employees.keys():
                                                            if str(employee) in ignore_employees[str(self.__company)]:
                                                                continue

                                                        employees.append(str(employee))

                                                    employees_paste = ', '.join(employees)
                                                    self.calculate_competence(competence, 11, date_payment,
                                                                              employees_paste, first_calc)

                                            if 70 in data and 70 in calculate:
                                                for date_payment in data[70]:
                                                    employees = []
                                                    for employee in data[70][date_payment]:
                                                        if str(self.__company) in ignore_employees.keys():
                                                            if str(employee) in ignore_employees[str(self.__company)]:
                                                                continue

                                                        employees.append(str(employee))

                                                    employees_paste = ', '.join(employees)
                                                    self.calculate_competence(competence, 70, date_payment,
                                                                              employees_paste, first_calc)

                                        first_calc = False
                                else:
                                    data = competences[int(self.__company)][competence]
                                    print(data)
                                    sleep(5)

                                self.send_status(self.__company, 'progress',
                                                 message=f"Cálculo da competência {competence} da empresa {self.__company} finalizado")

                        if not debug:
                            sleep(1)
                            autoit.send('{ESC}')
                            self.execute_sql(f'{self.__path_run}\\SQLs\\ajuste_rubricas.sql')

                # importar gozos de férias restantes e rodar SQL final
                if finish_process:
                    if not debug:
                        print_to_import(f'{self.__path_run}\\Temp\\FOAFASTAMENTOS_IMPORTACAO.txt', removals_import_last)
                        self.execute_sql(f'{self.__path_run}\\SQLs\\importacao_afastamentos.sql')

                    self.send_status(self.__company, 'progress',
                                     message=f"Início da importação de afastamentos parte 02")

                    if not debug:
                        self.importation_data(self.__sgd_username, self.__sgd_password, f'{self.__path_run}\\Temp',
                                              layout='Importacao afastamentos')
                    else:
                        print('importação afastamentos parte 02')
                        sleep(10)

                    self.send_status(self.__company, 'progress', message=f"Fim da importação de afastamentos parte 02")

                    self.send_status(self.__company, 'progress', message=f"Início da execução do SQL final")

                    if not debug:
                        self.execute_sql(f'{self.__path_run}\\SQLs\\ajusta_demitidos.sql')
                    else:
                        sleep(3)

                    self.send_status(self.__company, 'progress', message=f"Fim da execução do SQL final")
                    sleep(3)

                    self.send_status(self.__company, 'progress', message=f"Início da inativação de usuários")

                    if not debug:
                        self.disable_users()
                    else:
                        sleep(3)

                    self.send_status(self.__company, 'progress', message=f"Fim da inativação de usuários")
                    sleep(3)

                    self.close_dominio()

                sleep(5)
                self.send_status(self.__company, 'finish', import_events=import_events, import_removals=import_removals,
                                 import_vacation=import_vacation, finish_process=finish_process, only_log=True)
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: main - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)

    def reconnect_host(self):
        """
        Refaz a conexão com o host
        """
        self.print_log("warning", "Refazendo a conexão com o HOST")
        try:
            sleep(2)
            self.socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_connection.connect((self.__ip_host, self.DEFAULT_PORT))
        except Exception as e:
            self.print_log("critical", f"Erro refazendo a conexão com o Host {e}")

    def open_dominio(self, user, password):
        """
        Abrir sistema Domínio
        """
        self.print_log("info", f"Abrindo sistema usuário: {user} senha: {password} conexão: {self.__database}")
        try:
            autoit.send('{LWIN}')
            sleep(1)
            self.write('FOLHA')
            sleep(1)
            autoit.send('{ENTER}')

            self.print_log("info", f"Aguardando tela de login contábil")
            await_screen('[CLASS:FNWNS3190]', '')

            self.print_log("info", f"")
            sleep(1)
            self.print_log("info", f"Preenchendo usuário: {user}")
            self.write(user, edit='Edit1')
            sleep(1)
            self.print_log("info", f"Preenchendo senha: {password}")
            self.write(password, edit='Edit2')
            sleep(1)
            self.print_log("info", f"Preenchendo conexão: {self.__database}")
            self.write(self.__database, edit='Edit3')
            sleep(1)
            autoit.send('{TAB}{ENTER}')

            self.print_log("info", f"Aguardando abertura do contábil")
            await_screen('[CLASS:FNWND3190]', '')

            self.print_log("info", f"Verificando Avisos")
            while True:
                try:
                    if autoit.win_exists('Aviso'):
                        self.print_log("info", f"Fechando mensagem Aviso")
                        sleep(1)
                        message = autoit.win_get_text('Aviso')
                        if 'cadastramento inicial' in message:
                            autoit.control_click('', '[CLASSNN:Button2]')
                        else:
                            autoit.send('{ESC}')
                    elif autoit.win_exists('Atenção'):
                        self.print_log("info", f"Fechando mensagem de Atenção")
                        sleep(1)
                        message = autoit.win_get_text('Atenção')
                        if 'regime de enquadramento' in message:
                            autoit.control_click('', '[CLASSNN:Button2]')
                        else:
                            autoit.send('{ESC}')
                    elif autoit.win_active('[CLASS:#32770]'):
                        sleep(1)
                        autoit.control_click('', '[CLASSNN:Button2]')

                    title = autoit.win_get_title('[CLASS:FNWND3190]')
                    if 'Domínio Folha' in title:
                        break
                except:
                    pass

            while True:
                sleep(5)
                if autoit.win_exists('Aviso'):
                    self.print_log("info", f"Fechando mensagem Aviso")
                    sleep(1)
                    if 'cadastramento inicial' in message:
                        autoit.control_click('', '[CLASSNN:Button2]')
                    else:
                        autoit.send('{ESC}')
                elif autoit.win_exists('Atenção'):
                    self.print_log("info", f"Fechando mensagem de Atenção")
                    sleep(1)
                    message = autoit.win_get_text('Atenção')
                    if 'regime de enquadramento' in message:
                        autoit.control_click('', '[CLASSNN:Button2]')
                    else:
                        autoit.send('{ESC}')
                elif autoit.win_active('[CLASS:#32770]'):
                    sleep(1)
                    autoit.control_click('', '[CLASSNN:Button2]')
                else:
                    break

            sleep(3)
            # fechar todas as janelas

            for _ in range(10):
                self.print_log("info", f"Verificando e fechando janelas com 'ESC', contador {_}")
                autoit.send('{ESC}')
                sleep(1)

            autoit.win_activate('[CLASS:FNWND3190]')
            sleep(5)
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: open_dominio - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)
            self.print_log("critical", function_error)

    def open_calc_screen(self):

        self.print_log("info", f"Abrindo Janela de Cálculo")
        """
        Abrir tela de cálculo
        """
        try:
            autoit.win_activate('[CLASS:FNWND3190]')
            sleep(3)
            autoit.send("{ALT}PC")
            sleep(1)
            self.print_log("info", f"Aguardando tela de Cálculo")
            await_screen('', 'Cálculo')

            sleep(1)
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: open_calc_screen - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)
            self.print_log("critical", function_error)
            return

    def read_lancamentos(self):
        """
        Ler os dados que precisam ser calculados(férias, rescisões e demais folhas)
        """
        self.print_log("info", "Lendo os dados que precisam ser calculados(férias, rescisões e demais folhas)")
        try:
            result = {}
            ignore_companies = check_companies_calc(self.__database, self.__username, self.__password)

            # dados de holerites
            data = Table('FOLANCAMENTOS_EVENTOS', file=f'{self.__path_run}\\Importar\\FOLANCAMENTOS_EVENTOS.txt', path_def=self.path_def)
            for item in data.items():
                codi_emp = int(item.get_value('CODI_EMP'))
                i_empregados = item.get_value('I_EMPREGADOS')
                competencia = item.get_value('COMPETENCIA_INICIAL')
                tipo_processo = int(item.get_value('TIPO_PROCESSO'))
                data_pagamento = item.get_value('DATA_PAGAMENTO_ALTERA_CALCULO')

                if codi_emp not in ignore_companies:
                    if codi_emp not in result.keys():
                        result[codi_emp] = {}

                    if competencia not in result[codi_emp].keys():
                        result[codi_emp][competencia] = {}

                    if tipo_processo not in result[codi_emp][competencia].keys():
                        result[codi_emp][competencia][tipo_processo] = {}

                    if tipo_processo != 42:
                        if data_pagamento not in result[codi_emp][competencia][tipo_processo].keys():
                            result[codi_emp][competencia][tipo_processo][data_pagamento] = []

                        if int(i_empregados) not in result[codi_emp][competencia][tipo_processo][data_pagamento]:
                            result[codi_emp][competencia][tipo_processo][data_pagamento].append(int(i_empregados))
                    else:
                        if item['I_EMPREGADOS'] not in result[codi_emp][competencia][42].keys():
                            result[codi_emp][competencia][42][i_empregados] = {
                                'data_pagamento': data_pagamento
                            }

            # dados de rescisões
            sqlite_rescisao = DominioRescisao()
            sqlite_rescisao.connect(f'{self.__path_run}\\query.db')
            data_rescisao = sqlite_rescisao.select().dicts()

            # organizar os dados
            for row in data_rescisao:
                if int(row['codi_emp']) not in ignore_companies:
                    if int(row['codi_emp']) not in result.keys():
                        result[int(row['codi_emp'])] = {}

                    if row['competencia'] not in result[int(row['codi_emp'])].keys():
                        result[int(row['codi_emp'])][row['competencia']] = {}

                    # escolhido tipo 100 para representar as folhas de rescisão
                    if 100 not in result[int(row['codi_emp'])][row['competencia']].keys():
                        result[int(row['codi_emp'])][row['competencia']][100] = {}

                    if int(row['i_empregados']) not in result[int(row['codi_emp'])][row['competencia']][100].keys():
                        result[int(row['codi_emp'])][row['competencia']][100][int(row['i_empregados'])] = {
                            'data_demissao': row['data_demissao'],
                            'motivo': row['motivo'],
                            'data_pagamento': row['data_pagamento'],
                            'aviso_previo': row['aviso_previo'],
                            'data_aviso': row['data_aviso'],
                            'dias_projecao_aviso': row['dias_projecao_aviso']
                        }

            # dados de férias
            sqlite_ferias = DominioFerias()
            sqlite_ferias.connect(f'{self.__path_run}\\query.db')
            data_vacation_calc = sqlite_ferias.select().dicts()
            check_data_vacation = StorageData()

            for row in data_vacation_calc:
                competence = row['competencia']

                if int(row['codi_emp']) not in ignore_companies:
                    if int(row['codi_emp']) not in result.keys():
                        result[int(row['codi_emp'])] = {}

                    if competence not in result[int(row['codi_emp'])].keys():
                        result[int(row['codi_emp'])][competence] = {}

                    # tipo 60 pois é o tipo de folha para férias
                    if 60 not in result[int(row['codi_emp'])][competence].keys():
                        result[int(row['codi_emp'])][competence][60] = {}

                    if int(row['i_empregados']) not in result[int(row['codi_emp'])][competence][60].keys():
                        result[int(row['codi_emp'])][competence][60][int(row['i_empregados'])] = []

                    data = {
                        'fim_aquisitivo': row['fim_aquisitivo'],
                        'inicio_gozo': row['inicio_gozo'],
                        'fim_gozo': row['fim_gozo'],
                        'abono_paga': row['abono_paga'],
                        'inicio_abono': row['inicio_abono'],
                        'fim_abono': row['fim_abono'],
                        'data_pagamento': row['data_pagamento']
                    }
                    if not check_data_vacation.exist(
                            [int(row['codi_emp']), int(row['i_empregados']), competence, row['inicio_gozo']]):
                        result[int(row['codi_emp'])][competence][60][int(row['i_empregados'])].append(data)
                        check_data_vacation.add(row['fim_aquisitivo'],
                                                [int(row['codi_emp']), int(row['i_empregados']), competence,
                                                 row['inicio_gozo']])

            return result
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: read_lancamentos - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)
            self.print_log("critical", function_error)

    def competence_is_valid(self, competence, init_competence, end_competence):
        """
        Checa se a competência está dentro do range que vai ser calculado
        """
        try:
            convert_competence = datetime.strptime(competence, '%d/%m/%Y')
            if convert_competence.year < init_competence.year or convert_competence.year > end_competence.year:
                return False
            elif convert_competence.year == init_competence.year and convert_competence.year == end_competence.year:
                if convert_competence.month >= init_competence.month and convert_competence.month <= end_competence.month:
                    return True
            else:
                return True
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: competence_is_valid - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)

    def calculate_competence(self, competence, leaf_type, day_payment, employees, first_calc, count=0):
        """
        Calcula a competência de um empregado, recebendo como parâmetro a competência, tipo de folha, data de pagamento
        empregados, contribuintes e estagiários a serem calculados e se é calculo ou recalculo
        """
        self.print_log("info",
                       f"Iniciando calculos competência {competence} tipo folha {leaf_type} data pagamento {day_payment} empregados {employees} tipo de calculo {first_calc}")
        try:
            self.open_calc_screen()

            if first_calc:
                aux = datetime.strptime(day_payment, '%d/%m/%Y')
            else:
                aux = datetime.strptime(day_payment, '%Y-%m-%d')

            converted_day_payment = datetime.strftime(aux, '%d/%m/%Y')
            self.print_log("info", f"Preenchendo competência {competence[2:]}")
            # preencher competência
            autoit.send("{HOME}")
            sleep(1)
            self.write(competence[2:])
            sleep(1)
            autoit.send('{TAB}')
            sleep(1)

            self.print_log("info", f"Escolhendo tipo de folha {leaf_type}")
            # Escolher tipo de folha
            if leaf_type == 11:
                self.write('F')
                sleep(1)
            elif leaf_type == 41:
                self.write('A')
                sleep(1)
            elif leaf_type == 51:
                self.write('F')
                sleep(1)
                self.write('1')
                sleep(1)
            elif leaf_type == 52:
                self.write('F')
                sleep(1)
                self.write('11')
                sleep(1)
            elif leaf_type == 70:
                self.write('P')
                sleep(1)

            # Selecionar os empregados
            if not autoit.win_exists(text='Cálculo', title='[CLASS:FNWND3190]') and count <= 2:
                self.print_log("info",
                               f"Tela de Cálculo não existe, retornando ao inicio da função tentatica{count + 1}")
                self.calculate_competence(competence, leaf_type, day_payment, employees, first_calc, count=count + 1)
            elif not autoit.win_exists(text='Cálculo', title='[CLASS:FNWND3190]') and count > 2:
                self.print_log("critical", "Não foi possível prosseguir com o cálculo")

            if not autoit.win_activate(text='Cálculo', title='[CLASS:FNWND3190]'):
                self.print_log("info", "Ativando tela de Cálculo")
                autoit.win_activate(text='Cálculo', title='[CLASS:FNWND3190]')
            self.print_log("info", "Abrindo a tela de seleção de empregados")
            autoit.control_click('', '[CLASSNN:Button18]')
            sleep(2)

            # Seleciona o botão colaboradores

            self.print_log("info", f"Selecionando colaboradores {employees}")
            autoit.control_click(title='', text='Colaboradores:', control='[CLASSNN:Button9]')
            sleep(1)
            autoit.control_click(title='', text='Colaboradores:', control='[CLASSNN:Button9]')
            sleep(1)

            if employees:
                autoit.control_click(title='', text='Colaboradores:', control='[CLASSNN:Button9]')
                sleep(1)
                autoit.control_click(title='', text='Colaboradores:', control='[CLASSNN:Button9]')
                sleep(1)
                self.write(employees)
                sleep(5)

            self.print_log("info", "Confirmando seleção de colaboradores")
            count = 0
            while autoit.win_exists(text='Seleção de Empregados', title='[CLASS:FNWND3190]') and count < 5:
                sleep(2)
                autoit.control_click(title='', text='&OK', control='[CLASSNN:Button53]')

                sleep(3)
                count = count + 1
            if count >= 5:
                function_error = f'arquivo: agent.py - funcao: calculate_competence - não conseguiu clicar no botão 53 (ok da tela de seleção)'
                self.send_status(-1, 'error', message=function_error)

            # Preecher data de pagamento
            self.print_log("info", "Preenchendo data de pagamento")
            if not autoit.win_activate(text='Cálculo', title='[CLASS:FNWND3190]'):
                self.print_log("info", "Ativando tela de Cálculo")
                autoit.win_activate(text='Cálculo', title='[CLASS:FNWND3190]')

            self.print_log("info", f"Data de pagamento {converted_day_payment}")
            autoit.control_click(title='', text='&Data de pagamento', control='[CLASSNN:Button27]')
            sleep(2)
            self.write(converted_day_payment)
            sleep(1)
            autoit.send('{TAB}')
            self.print_log("info", f"TAB 1")
            sleep(1)
            self.write(converted_day_payment)
            sleep(1)
            autoit.send('{TAB}')
            self.print_log("info", f"TAB 2")
            sleep(1)
            self.write(converted_day_payment)
            sleep(1)
            autoit.send('{TAB}')
            sleep(1)
            self.print_log("info", f"TAB 3")
            if autoit.win_exists('Atenção'):
                if not autoit.win_activate('Atenção'):
                    self.print_log("info", f"Ativando tela de atenção")
                    autoit.win_activate('Atenção')
                self.print_log("info", f"Fechando mensagem de Atenção na tela de data de pagamento")
                autoit.control_click('', '[CLASSNN:Button1]')
                sleep(1)
            autoit.send('{TAB}')
            self.print_log("info", f"TAB 4")
            if autoit.win_exists('Atenção'):
                if not autoit.win_activate('Atenção'):
                    self.print_log("info", f"Ativando tela de atenção")
                    autoit.win_activate('Atenção')
                self.print_log("info", f"Fechando mensagem de Atenção na tela de data de pagamento")
                autoit.control_click('', '[CLASSNN:Button1]')
                sleep(1)
            sleep(1)
            autoit.send('{ENTER}')
            self.print_log("info", f"ENTER")
            if autoit.win_exists('Atenção'):
                if not autoit.win_activate('Atenção'):
                    self.print_log("info", f"Ativando tela de atenção")
                    autoit.win_activate('Atenção')
                self.print_log("info", f"Fechando mensagem de Atenção na tela de data de pagamento")
                autoit.control_click('', '[CLASSNN:Button1]')
                sleep(1)
            sleep(2)

            if not autoit.win_activate(text='Cálculo', title='[CLASS:FNWND3190]'):
                self.print_log("info", "Ativando tela de Cálculo")
                autoit.win_activate(text='Cálculo', title='[CLASS:FNWND3190]')

            # prenche o percentual de adiantamento quando necessário
            if leaf_type == 41 or leaf_type == 51:
                self.print_log("info", "Preenchendo percentual de adiantamento 40%")
                autoit.control_click('', '[CLASSNN:PBEDIT1901]')
                self.write('40', edit='PBEDIT1901')

            # Começar o cálculo

            self.print_log("info", "Iniciando Cálculo")
            while True:
                if not autoit.win_exists('Cálculo da folha'):
                    autoit.control_click('', '[CLASSNN:Button22]')
                    break
            self.print_log("info", "Cálculo Iniciado")

            sleep(1)
            self.await_calc()
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: calculate_competence - linha: {exc_tb.tb_lineno} - erro: {e}'
            if count <= 2:
                self.print_log("info",
                               f"Tela de Cálculo não existe, retornando ao inicio da função tentatica {count + 1}")
                self.calculate_competence(competence, leaf_type, day_payment, employees, first_calc, count=count + 1)
            else:
                self.send_status(-1, 'error', message=function_error)
                self.print_log("critical", function_error)

    def calculate_vacation(self, data, recalculate=False, company=0, competence=''):
        """
        Calcular férias dos empregados de uma determinada competência,
        recebe como parametro os dados a calcular, se é um recalculo ou não e
        o codigo da empresa
        """
        self.print_log("info", "Inicio do cálculo de férias")
        try:
            for employee in data:
                self.print_log("info", f"percorrendo empregado {employee}")
                for data_vacation in data[employee]:
                    if str(company) in ignore_employees.keys():
                        if str(employee) in ignore_employees[str(company)]:
                            continue

                    if not recalculate:
                        # checar se o próximo periodo aquisitivo em aberto é o período que precisar ser calculado
                        self.print_log("info", f"checando aquisitivos")
                        self.check_acquisition_period(company, employee, data_vacation['fim_aquisitivo'])

                    if str(company) in ignore_employees.keys():
                        if str(employee) in ignore_employees[str(company)]:
                            continue

                    # abre a tela de calculo de férias
                    autoit.send("{ALT}PFI")
                    await_screen('[CLASS:FNWND3190]', 'Férias')

                    self.print_log("info", "Informando empregado")
                    autoit.control_click('', '[CLASSNN:PBEDIT1905]')
                    sleep(1)
                    self.write(str(employee))
                    sleep(1)

                    if not recalculate:
                        autoit.send('{TAB}{ENTER}')
                        self.print_log("info", "Ativando tela 'Nova Férias'")
                        await_screen('[CLASS:FNWND3190]', 'Nova Férias')

                        # preenche os dados de inicio e fim de gozo
                        self.print_log("info", f"Informando inicio do Gozo {str(data_vacation['inicio_gozo'])}")
                        self.write(str(data_vacation['inicio_gozo']))
                        sleep(1)
                        autoit.send('{TAB}{TAB}')
                        sleep(1)
                        self.print_log("info", f"Informando fim do Gozo {str(data_vacation['fim_gozo'])}")
                        self.write(str(data_vacation['fim_gozo']))
                        sleep(1)
                        autoit.send('{TAB}')
                        sleep(1)

                        # checa se precisa preencher os dados de abono
                        if str(data_vacation['abono_paga']).upper() == 'S':
                            autoit.send('{SPACE}')
                            autoit.send('{TAB}')

                            sleep(1)
                            self.write(str(data_vacation['inicio_abono']))

                            sleep(1)
                            autoit.send('{TAB}{TAB}')
                            self.write(str(data_vacation['fim_abono']))

                            sleep(1)
                            autoit.send('{TAB}')
                        else:
                            autoit.send('{TAB}')

                        sleep(1)

                        if data_vacation['data_pagamento']:
                            self.print_log("info",
                                           f"Informando data de pagamento {str(data_vacation['data_pagamento'])}")
                            self.write(str(data_vacation['data_pagamento']))
                            sleep(1)

                        self.print_log("info", "Ativando tela de 'Nova Férias'")
                        try:
                            autoit.win_activate('[CLASS:FNWND3190]', text='Nova Férias')
                            self.print_log("info", "Tela de 'Nova Férias' ativada")
                        except:
                            self.print_log("info", "Não foi possível ativar a tela de 'Nova Férias'")
                            pass

                        self.print_log("info", "Cliando no botão cálcular '[CLASSNN:Button6]'")
                        autoit.control_click('', '[CLASSNN:Button6]')
                        sleep(1)

                    else:
                        autoit.send('{TAB}')
                        sleep(1)

                        # fica em loop enquanto não for o período que queremos recalcular

                        self.print_log("info", "Selecionando periodo aquisitivo")
                        while True:
                            autoit.control_click('', '[CLASSNN:Button9]')
                            sleep(1)
                            autoit.win_activate('[CLASS:FNWND3190]', text='Nova Férias')
                            inicio_gozo = autoit.control_get_text('', '[CLASSNN:PBEDIT1909]')
                            self.print_log("info",
                                           f"Buscando aquisitivo {inicio_gozo} aquisitivo selecionado {inicio_gozo}")
                            sleep(1)
                            if inicio_gozo == data_vacation['inicio_gozo']:
                                self.print_log("info", "Aquisitivo encontrado")
                                autoit.control_click('', '[CLASSNN:Button6]')
                                sleep(1)
                                if autoit.win_exists('Recalcular férias'):
                                    autoit.control_click('', '[CLASSNN:Button1]')
                                    sleep(1)
                                break
                            else:
                                autoit.send('{ESC}')
                                sleep(1)
                                autoit.send('{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}')
                                sleep(1)
                                autoit.send('{UP}')
                                sleep(1)

                    if not recalculate:
                        self.await_calc(vacation=True, company=company, employee=employee,
                                        end_acquisition=data_vacation['fim_aquisitivo'], competence=competence)
                    else:
                        self.await_calc(vacation=True)
                    sleep(1)
                    autoit.send('{ESC}')
                    sleep(1)
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: calculate_vacation - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)

    def calculate_rescission(self, data, company=0):
        """
        Calcular rescisões dos empregados de uma determinada competência
        """
        self.print_log("info", "Inicio do cálculo de rescisão")
        try:
            for employee in data:
                if str(company) in ignore_employees.keys():
                    if str(employee) in ignore_employees[str(company)]:
                        continue

                autoit.send('{ALT}PRI')
                self.print_log("info", "Ativando tela de rescisão individual")
                await_screen('', 'Rescisão Individual')

                sleep(1)
                self.print_log("info", f"Informando colaborador {str(employee)}")
                self.write(str(employee))
                sleep(1)
                autoit.send('{TAB}')
                sleep(2)
                if autoit.win_active('Atenção'):
                    self.print_log("info", "Fechando tela de atenção")
                    autoit.control_click('', '[CLASSNN:Button1]')
                sleep(4)

                # se for um dict quer dizer que é o calculo da rescisão
                # e situações de recalculo "data" é do tipo "list"
                if type(data) == dict:

                    self.print_log("info", f"Preenchendo data de demissão {str(data[employee]['data_demissao'])}")
                    self.write(str(data[employee]['data_demissao']))
                    sleep(1)
                    autoit.send('{TAB}')
                    sleep(3)
                    if autoit.win_active('Atenção'):
                        self.print_log("info", "Fechando tela de atenção")
                        autoit.control_click('', '[CLASSNN:Button1]')
                        sleep(1)

                    # selecionar motivo
                    first_iteration = True
                    motivo_old = ''
                    empregador = False

                    self.print_log("info", f"procurando Motivo da demissão: {str(data[employee]['motivo'])}")
                    self.print_log("info", "Selecionando motivo")
                    while True:
                        autoit.send('{DOWN}')
                        sleep(3)
                        if autoit.win_exists('Atenção'):
                            self.print_log("info", "Fechando tela de atenção")
                            autoit.control_click('Atenção', '[CLASSNN:Button1]')
                            sleep(2)

                        if autoit.win_exists('', text='Rescisão Individual'):
                            autoit.win_active('', text='Rescisão Individual')
                        motivo = autoit.control_get_text('', '[CLASSNN:pbdwst1908]')
                        self.print_log("info", f"Motivo em tela: {motivo}")
                        if not first_iteration and motivo_old == motivo:
                            empregador = True
                            break

                        if str(data[employee]['motivo']) in motivo:
                            autoit.send('{TAB}')
                            sleep(3)
                            break

                        first_iteration = False
                        motivo_old = motivo

                    if not empregador:
                        if int(data[employee]['aviso_previo']) == 1:
                            self.print_log("info",
                                           f"Preenchendo aviso previo {str(data[employee]['data_aviso'])} {str(data[employee]['dias_projecao_aviso'])[0:2]}")
                            autoit.send('{TAB}')
                            sleep(1)
                            self.write(str(data[employee]['data_aviso']))
                            sleep(1)
                            autoit.send('{TAB}')
                            sleep(1)
                            autoit.send('{TAB}')
                            sleep(1)
                            self.write(str(data[employee]['dias_projecao_aviso'])[0:2])
                            sleep(1)
                        else:
                            self.print_log("info", "Sem aviso previo")
                            autoit.send('{TAB}')
                            sleep(1)
                            autoit.send('{TAB}')
                            sleep(1)
                            autoit.send('{TAB}')
                            sleep(1)

                    sleep(3)
                    autoit.control_click('', '[CLASSNN:PBEDIT1902]')

                    if data[employee]['data_pagamento'] is not None:
                        self.print_log("info", f"Preenchendo data de pagamento {str(data[employee]['data_pagamento'])}")
                        self.write(str(data[employee]['data_pagamento']), edit='PBEDIT1902')
                        sleep(1)

                sleep(1)
                self.print_log("info", f"Clicando no botão para cálcular '[CLASSNN:Button22]'")
                autoit.control_click('', '[CLASSNN:Button22]')
                sleep(1)
                self.await_calc(vacation=True)
                sleep(2)
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: calculate_rescission - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)
            self.print_log("critical", function_error)

    def calculate_additional_rescission(self, data, company=0):
        """
        Calcular rescisões complementares dos empregados de uma determinada competência
        """
        try:
            for employee in data:
                if str(company) in ignore_employees.keys():
                    if str(employee) in ignore_employees[str(company)]:
                        continue

                autoit.send('{ALT}PRC')
                await_screen('', 'Rescisões Complementares')

                self.write(str(employee))
                sleep(1)
                autoit.send('{TAB}')
                sleep(5)

                if autoit.win_exists('Erro', text='Colaborador não está demitido!'):
                    sleep(1)
                    autoit.send('{ESC}')
                    sleep(1)
                    autoit.send('{ESC}')
                    self.send_status(company, 'error',
                                     message=f'calculate_additional_rescission -não foi possível calcular a rescisão complementar do empregado {employee} da empresa {company} pois o empregado não está demitido!')
                    continue

                # se for um dict quer dizer que é o calculo da rescisão
                # e situações de recalculo "data" é do tipo "list"
                if type(data) == dict:
                    autoit.send('{ENTER}')
                else:
                    autoit.send('{TAB}')
                    sleep(1)
                    autoit.send('{ENTER}')

                sleep(1)
                while True:
                    if autoit.win_active('', text='Rescisões Complementares'):
                        sleep(15)
                        break

                    if autoit.win_active('Atenção'):
                        autoit.control_click('', '[CLASSNN:Button1]')
                        sleep(5)

                if type(data) == dict:
                    if data[employee]['data_pagamento'] is not None:
                        self.write(str(data[employee]['data_pagamento']))

                    sleep(5)
                    if autoit.win_active('Erro'):
                        message = autoit.win_get_text('Erro')
                        if str(company) not in ignore_employees.keys():
                            ignore_employees[str(company)] = [str(employee)]
                        else:
                            ignore_employees[str(company)].append(str(employee))

                        self.send_status(company, 'error',
                                         message=f"""Não foi possível calcular a rescisão complementar do empregado {employee} da empresa {company}, messagem do sistema: '{message}'""",
                                         only_log=True)
                        autoit.send('{ESC}')
                        sleep(1)
                        autoit.send('{ESC}')
                        sleep(3)
                        if autoit.win_active('Atenção'):
                            autoit.control_click('Atenção', '[CLASSNN:Button1]')
                            sleep(4)

                        autoit.send('{ESC}')
                        sleep(1)
                        continue

                    autoit.send('{TAB}')
                    sleep(1)
                    autoit.send('{TAB}')
                    sleep(1)
                    self.write('CONVERSÃO')
                    sleep(1)
                    autoit.send('{TAB 6}')
                    sleep(1)

                try:
                    autoit.control_click('', '[CLASSNN:Button20]')
                    sleep(1)
                    self.await_calc(vacation=True, company=company, employee=employee)
                    sleep(2)
                    autoit.send('{ESC}')
                    sleep(1)
                except:
                    message = autoit.win_get_text('Erro')
                    if str(company) not in ignore_employees.keys():
                        ignore_employees[str(company)] = [str(employee)]
                    else:
                        ignore_employees[str(company)].append(str(employee))

                    self.send_status(company, 'error',
                                     message=f"""Não foi possível calcular a rescisão complementar do empregado {employee} da empresa {company}, messagem do sistema: '{message}'""",
                                     only_log=True)
                    autoit.send('{ESC}')
                    sleep(1)
                    autoit.send('{ESC}')
                    sleep(3)
                    if autoit.win_active('Atenção'):
                        autoit.control_click('Atenção', '[CLASSNN:Button1]')
                        sleep(4)

                    autoit.send('{ESC}')
                    sleep(1)
                    continue
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: calculate_additional_rescission - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)

    def await_calc(self, vacation=False, company=0, employee=0, end_acquisition=0, ignore_finish_messages=False,
                   competence=''):
        """
        Aguarda até que o calculo seja finalizado
        """
        self.print_log("info", "Aguardando termino do cálculo")
        try:
            self.print_log("info", "Ativando tela de cálculo")
            while True:
                if not autoit.win_active('Cálculo da folha'):
                    break
            self.print_log("info", "Tela de cálculo ativa")
            sleep(1)
            if vacation and not ignore_finish_messages:
                self.print_log("info", "Cálculo do tipo férias")
                while True:

                    if autoit.win_exists('Erro'):
                        autoit.win_activate('Erro')

                    if autoit.win_exists('Atenção'):
                        autoit.win_activate('Atenção')

                    if autoit.win_exists('Aviso'):
                        autoit.win_activate('Aviso')

                    if autoit.win_exists('Erro'):
                        self.print_log("info", f"Fechando mensagem de erro no cálculo da tela de rescisão")
                        autoit.control_click('', '[CLASSNN:Button1]')
                        sleep(1)
                    if autoit.win_active('Atenção'):
                        self.print_log("info", "Fechando mensagem de Atenção")
                        sleep(1)
                        message = autoit.win_get_text('Atenção')
                        if 'posterior a data de transferência' in message:
                            if str(company) not in ignore_employees.keys():
                                ignore_employees[str(company)] = [str(employee)]
                            else:
                                ignore_employees[str(company)].append(str(employee))

                            self.send_status(company, 'error',
                                             message=f"""Não foi possível calcular as férias do empregado {employee} da empresa {company} na competência {competence}, messagem do sistema: '{message}'""",
                                             only_log=True)
                            autoit.control_click('Atenção', '[CLASSNN:Button1]')
                            autoit.send('{ESC}')
                            ignore_finish_messages = True
                            sleep(1)
                            break
                        elif 'vinculado a um serviço que não possui o código de terceiros desmembrado' in message:
                            if str(company) not in ignore_employees.keys():
                                ignore_employees[str(company)] = [str(employee)]
                            else:
                                ignore_employees[str(company)].append(str(employee))

                            self.send_status(company, 'error',
                                             message=f"""Não foi possível calcular o empregado {employee} da empresa {company} na competência {competence}, messagem do sistema: '{message}'""",
                                             only_log=True)
                            autoit.control_click('Atenção', '[CLASSNN:Button1]')
                            autoit.send('{ESC}')
                            sleep(2)
                            autoit.control_click('Atenção', '[CLASSNN:Button1]')
                            ignore_finish_messages = True
                            sleep(1)
                            break

                        autoit.control_click('', '[CLASSNN:Button1]')

                    if autoit.win_exists('Aviso', text='Cálculo'):
                        self.print_log("info", "Fechando mensagem de Aviso")
                        sleep(1)
                        autoit.send('{ESC}')
                        sleep(1)

                    # quando o dá erro de períodos aquisitivos, o próprio sistema Domínio gera os períodos faltantes,
                    # então o rpa vai até os períodos gerados, marca como gozado e retorna para calcular as férias
                    if autoit.win_exists('Aviso', text='Aquisição final inválida'):
                        self.print_log("info",
                                       "Foram gerados períodos aquisitivos de forma automatica pelo Contábil, marcando-os como gozados")
                        sleep(1)
                        autoit.control_click('Aviso', '[CLASSNN:Button1]')
                        sleep(1)
                        self.check_acquisition_period(company, employee, end_acquisition)
                        autoit.control_click('', '[CLASSNN:Button6]')
                        self.await_calc(vacation=True, ignore_finish_messages=True)
                        self.print_log("info", "Finalizado")
                        break

                    if autoit.win_exists('Aviso'):
                        sleep(1)

                        # checa se não é aviso referente aos períodos aquisitivos
                        # se for, não calcula mais a movimentação desse empregado
                        message = autoit.win_get_text('Aviso')
                        ignore_employee = False

                        if 'dias de gozo superior aos dias de direito' in message:
                            autoit.control_click('Aviso', '[CLASSNN:Button2]')
                            ignore_employee = True
                        if 'Já existe um afastamento dentro do período de gozo' in message:
                            autoit.control_click('Aviso', '[CLASSNN:Button1]')
                            ignore_employee = True

                        if ignore_employee:
                            self.print_log("error",
                                           f"""Não foi possível calcular as férias do empregado {employee} da empresa {company} na competência {competence}, messagem do sistema: '{message}'""")
                            if str(company) not in ignore_employees.keys():
                                ignore_employees[str(company)] = [str(employee)]
                            else:
                                ignore_employees[str(company)].append(str(employee))

                            self.send_status(company, 'error',
                                             message=f"""Não foi possível calcular as férias do empregado {employee} da empresa {company} na competência {competence}, messagem do sistema: '{message}'""",
                                             only_log=True)

                            autoit.send('{ESC}')
                            ignore_finish_messages = True
                            sleep(1)
                            break

                        autoit.control_click('Aviso', '[CLASSNN:Button1]')
                        sleep(1)

                    if autoit.win_active('[CLASS:FNWND3190]', text='Avisos do Cálculo'):
                        self.print_log("info", "Tela Avisos do Cálculo")
                        sleep(1)
                        break

                    try:
                        if autoit.win_activate('[CLASS:FNWND3190]') and autoit.win_get_title(
                                '[CLASS:FNWND3190]') == 'Transferência':
                            sleep(1)
                            self.print_log("info", "Empregado Transferido")

                            self.print_log("info", "Marcando a opção de transferencia para outro banco de dados")
                            autoit.send('{SPACE}')
                            sleep(1)
                            autoit.send('{TAB}')
                            sleep(1)
                            autoit.send('{TAB}')
                            self.print_log("info", "Preenchendo o CNPJ com zeros")
                            self.write('00000000000000')
                            sleep(1)
                            self.print_log("info", "CLicando no botão Button2")
                            autoit.control_click('', '[CLASSNN:Button2]')
                    except:
                        pass

                    if autoit.win_exists('Fim do cálculo'):
                        autoit.win_activate('Fim do cálculo')

                    if autoit.win_active('Fim do cálculo'):
                        self.print_log("info", "Fim do cálculo")
                        sleep(1)
                        break
                    sleep(0.5)
            else:
                self.print_log("info", "Não é calculo de férias")
                while True:
                    if autoit.win_exists('Erro'):
                        autoit.win_activate('Erro')
                        autoit.control_click('', '[CLASSNN:Button1]')
                        sleep(1)

                    if autoit.win_exists('[CLASS:#32770]', text='Deseja ver os dados calculados?'):
                        autoit.win_activate('[CLASS:#32770]', text='Deseja ver os dados calculados?')
                        sleep(1)
                        break
                    if autoit.win_exists('[CLASS:FNWND3190]', text='Avisos do Cálculo'):
                        autoit.win_activate('[CLASS:FNWND3190]', text='Avisos do Cálculo')
                        sleep(1)
                        if autoit.win_active('[CLASS:FNWND3190]', text='Avisos do Cálculo'):
                            self.print_log("info", "Ativando tela 'Avisos do Cálculo'")
                            sleep(1)
                            self.print_log("info", "Fechando tela de aviso de cálculo")
                            autoit.control_click('', '[CLASSNN:Button4]')
                            sleep(1)
                    sleep(1)

            if not ignore_finish_messages:
                if autoit.win_active('[CLASS:FNWND3190]', text='Avisos do Cálculo'):
                    self.print_log("info", "Ativando tela 'Avisos do Cálculo' if not ignore_finish_messages")
                    sleep(1)
                    autoit.control_click('', '[CLASSNN:Button4]')
                    sleep(1)

                sleep(1)

                self.print_log("info", "Fechando tela final do cálculo")
                autoit.control_click('', '[CLASSNN:Button2]')
                sleep(1)
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: await_calc - linha: {exc_tb.tb_lineno} - erro: {e}'
            print(f'arquivo: {fname} - funcao: await_calc - linha: {exc_tb.tb_lineno} - erro: {e}')
            self.send_status(-1, 'error', message=function_error)
            self.print_log("critical", function_error)

    def await_importation(self):
        """
        Aguarda até que a importação seja finalizada
        """
        self.print_log("info", "Aguarda até que a importação seja finalizada")
        try:
            while True:
                if autoit.win_exists('Importação de Tabelas'):
                    message = autoit.win_get_text('Importação de Tabelas')
                    self.print_log("info", f"Mensagem da tela de importação {message}")
                    try:
                        self.print_log("info", "Fechando mensagem")
                        autoit.control_click('', '[CLASSNN:Button1]', text='OK')
                        break
                    except:
                        self.print_log("info", "Erro ao fechar mensagem")
                        pass
            self.print_log("info", "Importação seja finalizada")
            sleep(1)
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: await_importation - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)
            self.print_log("error", "Erro realizando importação")
            self.print_log("critical", function_error)

    def execute_sql(self, sql_path):
        """
        Executa um comando SQL no sistema
        """
        self.print_log("info", f"Executando SQL {sql_path}")

        try:
            self.print_log("info", "Abrindo tela de empresas")
            autoit.send("{ALT}CE")
            sleep(1)

            await_screen('[CLASS:FNWND3190]', '')
            sleep(1)

            self.print_log("info", "Abrindo tela de execução de SQL")
            autoit.send("{CTRLDOWN}{SHIFTDOWN}S{CTRLUP}{SHIFTUP}")

            await_screen('[CLASS:FNWND3190]', 'Comandos SQL')
            sleep(1)

            self.print_log("info", f"Informando caminho do SQL {sql_path}")
            self.write(sql_path)
            sleep(3)
            autoit.control_click('', '[CLASSNN:Button7]')
            sleep(3)
            autoit.send("{ENTER}")
            self.print_log("info", "Executando SQL")

            await_screen('Comandos SQL', '')
            self.print_log("info", "Fim da execução do SQL")
            sleep(1)

            autoit.send("{ENTER}{ESC}{ESC}")
            sleep(1)
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: execute_sql - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)
            self.print_log("info", function_error)

    def generate_item_entries(self, competence, company):
        """
        Checa se depois de realizado o calculo o sistema gerou alguma rubrica que não foi lançada,
        para deixar o recibo exatamente igual ao do concorrente
        """
        try:
            sqlite_ferias = DominioFerias()
            sqlite_ferias.connect(f'{self.__path_run}\\query.db')
            data_vacation = sqlite_ferias.select().dicts().where(DominioFerias.competencia == competence,
                                                                 DominioFerias.codi_emp == company)

            # exportar gozos de férias Domínio
            sybase = Sybase(self.__database, self.__username, self.__password)
            connection = sybase.connect()
            data_gozo_ferias = sybase.select_gozo_ferias(connection)
            sybase.close_connection(connection)

            vacation_importation = []

            for line in data_vacation:
                if str(company) in ignore_employees.keys():
                    if str(line['i_empregados']) in ignore_employees[str(company)]:
                        continue

                importation = True
                table = Table('FOFERIAS_LANCAMENTOS', path_def=self.path_def)
                table.set_value('CODI_EMP', int(line['codi_emp']))
                table.set_value('I_EMPREGADOS', int(line['i_empregados']))
                table.set_value('I_EVENTOS', line['rubrica'])
                table.set_value('VALOR_INFORMADO', format(float(line['valor_informado']), '.2f'))
                table.set_value('VALOR_CALCULADO', format(float(line['valor_calculado']), '.2f'))
                table.set_value('ORIGEM_REG', '1')

                if table.get_value('CODI_EMP') not in data_gozo_ferias.keys(): continue
                if table.get_value('I_EMPREGADOS') not in data_gozo_ferias[table.get_value('CODI_EMP')].keys(): continue
                if line['inicio_gozo'] not in data_gozo_ferias[table.get_value('CODI_EMP')][
                    table.get_value('I_EMPREGADOS')].keys(): continue

                init_aqui = \
                data_gozo_ferias[table.get_value('CODI_EMP')][table.get_value('I_EMPREGADOS')][line['inicio_gozo']][
                    'inicio_aquisitivo']

                # quando o gozo que está no banco domínio não está dentro do período aquisitivo correto, cria um log e ignora os calculos do empregado
                if init_aqui != line['inicio_aquisitivo']:
                    if str(company) not in ignore_employees.keys():
                        ignore_employees[str(company)] = [str(line['i_empregados'])]
                    else:
                        ignore_employees[str(company)].append(str(line['i_empregados']))

                    self.send_status(company, 'error',
                                     message=f"""Não foi possível continuar com o calculo das férias do empregado {str(line['i_empregados'])} da empresa {company} na competência {competence} pois os períodos aquisitivos estão incorretos.""")
                    continue

                table.set_value('I_FERIAS_GOZO',
                                data_gozo_ferias[table.get_value('CODI_EMP')][table.get_value('I_EMPREGADOS')][
                                    line['inicio_gozo']]['i_ferias_gozo'])

                for index, item in enumerate(vacation_importation):
                    if item['CODI_EMP'] == table.get_value('CODI_EMP'):
                        if item['I_EMPREGADOS'] == table.get_value('I_EMPREGADOS'):
                            if item['I_FERIAS_GOZO'] == table.get_value('I_FERIAS_GOZO'):
                                if item['I_EVENTOS'] == table.get_value('I_EVENTOS'):
                                    valor = float(item['VALOR_CALCULADO']) + float(table.get_value('VALOR_CALCULADO'))
                                    table.set_value('VALOR_CALCULADO', format(float(valor), '.2f'))
                                    vacation_importation.remove(item)
                if importation:
                    vacation_importation.append(table.do_output())

            return vacation_importation
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: generate_item_entries - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)

    def open_importacao_sistemas_concorrentes(self, username, password):
        """
        Abre a tela de importação de sistemas concorrentes
        """
        self.print_log("info", "Abrindo tela de importação de sistemas concorrentes")
        try:
            if self.__system_user == 'GERENTE':
                # Menu correto quando é o usuário GERENTE
                autoit.send('{ALT}UI')
                autoit.send('{RIGHT}{DOWN}{RIGHT}')
                autoit.send('{UP 3}{ENTER}')
            else:
                # Menu correto quando é um usuário diferente do GERENTE
                autoit.send('{ALT}UI')
                autoit.send('{DOWN}{RIGHT}')
                autoit.send('{UP 3}{ENTER}')

            await_screen('', 'Importação de Tabelas de Sistemas Concorrentes')

            self.print_log("info", f"Informando usuário e senha do SGD, usuário {username}")
            autoit.send('{TAB}')
            self.write(username)
            sleep(1)
            autoit.send('{TAB}')
            self.write(password)
            sleep(1)
            autoit.send('{TAB}{ENTER}')

            autentication = 0
            if autoit.win_exists('', text='Importação de Tabelas de Sistemas Concorrentes'):
                while True:
                    # Se der erro de autenticação, espera 1 minuto e tenta novamente, fazendo até 10 tentativas
                    if autoit.win_exists('Aviso'):
                        autentication += 1
                        self.print_log("info",
                                       f"Erro de autenticação, realizando tentativa {autentication} de 10 {username} {password}")
                        if autentication <= 10:
                            sleep(1)
                            autoit.send('{ENTER}{ESC}')
                            sleep(60)
                            self.open_importacao_sistemas_concorrentes(username, password)
                        else:
                            return
                    try:
                        if autoit.control_get_text('', '[CLASSNN:Edit2]') != username:
                            break
                    except:
                        try:
                            autoit.control_click('', '[CLASSNN:Button11]')
                            break
                        except:
                            pass
                    sleep(0.5)

            self.print_log("info", "Tela aberta")
            sleep(10)
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: open_importacao_sistemas_concorrentes - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)
            self.print_log("critical", function_error)

    def open_importacao_tabelas(self, layout):
        """
        Abrir importação de tabelas
        """
        self.print_log("info", "Abrindo tela de importação de tabelas")
        try:
            autoit.send('{ALT}U')
            autoit.send('{UP 16}')
            autoit.send('{RIGHT}{DOWN}{RIGHT}')
            autoit.send('{DOWN 3}{ENTER}')

            while True:
                if autoit.win_exists('Informações Técnicas'):
                    autoit.send('{ESC}')
                    sleep(2)
                    autoit.send('{ALT}U')
                    autoit.send('{UP 12}')
                    autoit.send('{RIGHT}{DOWN}{RIGHT}')
                    autoit.send('{DOWN 3}{ENTER}')
                    sleep(2)

                if autoit.win_exists('', text='Importação de Tabelas'):
                    break
                sleep(0.5)

            sleep(2)
            autoit.control_click('', '[CLASSNN:ComboBox3]')
            sleep(1)

            # percorrer os layouts até achar o correto
            selected_layout = ''
            action = '{DOWN}'
            while True:
                if layout in autoit.control_get_text('', '[CLASSNN:ComboBox3]'):
                    autoit.send('{ENTER}')
                    break
                else:
                    if selected_layout == autoit.control_get_text('', '[CLASSNN:ComboBox3]'):
                        action = '{UP}'
                        autoit.send(action)
                        sleep(20)
                    else:
                        selected_layout = autoit.control_get_text('', '[CLASSNN:ComboBox3]')
                        autoit.send(action)
                        sleep(20)
                sleep(0.5)

            self.print_log("info", "Tela aberta")
            sleep(5)
            autoit.control_click('', '[CLASSNN:Edit9]')
            sleep(1)
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: open_importacao_tabelas - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)
            self.print_log("critical", function_error)

    def importation_data(self, username, password, path_data, layout=False):
        """
        Faz a importação de dados, recebe como parametro usuario e senha do SGD
        e o caminho até os dados a serem importados.
        Por padrão utiliza a importação de sistemas concorrentes, e caso seja passado
        um layout, acessa a importação de tabelas e utiliza o layout especificado
        """
        self.print_log("info", f"Iniciando importação de dados {path_data}")
        try:
            if not layout:
                self.open_importacao_sistemas_concorrentes(username, password)
            else:
                self.open_importacao_tabelas(layout)

            # colocar duas barras que aí não ocorre erro se por ventura alguma pasta começar com n
            path_data = str(path_data).replace('\\', '//')

            # colar caminho até os dados
            self.print_log("info", f"Informando caminho de importação")
            autoit.send('{END}')
            sleep(1)
            autoit.send('{SHIFTDOWN}{HOME}{SHIFTUP}')
            sleep(1)
            self.write(path_data)
            sleep(1)
            autoit.control_click('', '[CLASSNN:Button3]')
            sleep(1)
            autoit.control_click('', '[CLASSNN:Button12]')
            sleep(1)

            if not layout:
                autoit.win_wait_active('Importação de Tabelas de Sistemas Concorrentes')
            else:
                autoit.win_wait_active('Importação de Tabelas')

            autoit.control_click('', '[CLASSNN:Button1]')
            sleep(1)
            self.await_importation()
            autoit.send('{ESC}')
            sleep(1)
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: importation_data - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)
            self.print_log("critical", function_error)

    def active_company(self, company):
        """
        Ativar uma empresa no sistema Domínio
        """
        self.print_log("info", f"Ativando empresa {company}")
        try:
            sleep(3)

            # fechar todas as janelas
            for _ in range(10):
                autoit.send('{ESC}')
                sleep(1)

            autoit.send('{F8}')
            self.print_log("info", "Abrindo tela de troca de empresas")
            while True:
                if autoit.win_active('', text='Troca de empresas'):
                    break
                else:
                    autoit.send('{F8}')
                    sleep(1)

            sleep(1)
            autoit.control_click('', '[CLASSNN:Button6]')
            sleep(1)
            self.write(str(company))
            sleep(1)
            autoit.send('{ENTER}')
            sleep(1)
            self.print_log("info", f"fechando mensagens")
            while True:
                sleep(5)

                if autoit.win_exists('Aviso'):
                    sleep(1)
                    message = autoit.win_get_text('Aviso')
                    if 'cadastramento inicial' in message:
                        autoit.control_click('', '[CLASSNN:Button2]')
                    else:
                        autoit.send('{ESC}')
                elif autoit.win_exists('Atenção'):
                    sleep(1)
                    message = autoit.win_get_text('Atenção')
                    if 'regime de enquadramento' in message:
                        autoit.control_click('', '[CLASSNN:Button2]')
                    else:
                        autoit.send('{ESC}')
                elif autoit.win_exists('Erro'):
                    sleep(1)
                    autoit.control_click('', '[CLASSNN:Button1]')
                    sleep(1)
                elif not autoit.win_active('', text='Troca de empresas'):
                    break
            self.print_log("info", f"Empresa {company} Ativa")
            sleep(1)
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: active_company - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)
            self.print_log("critical", function_error)
            return

    def write(self, text, edit=False):
        self.print_log("info", f"Escrevendo texto {text}")
        try:
            if not edit:
                for character in text:
                    autoit.send(character)
            else:
                autoit.control_click('', f'[CLASSNN:{edit}]')
                sleep(1)
                autoit.send('{END}')
                sleep(1)
                autoit.send('{SHIFTDOWN}{HOME}{SHIFTUP}')
                sleep(1)
                self.write(text)
                sleep(1)
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: write - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)
            self.print_log("error", f"Erro escrevendo o texto {text}")

    def remove_entries(self, data_vacation, data_removals):
        """
        Recebe os dados referentes a gozo de férias e afastamentos e retira os
        registros que estão dentro das competências que serão calculadas
        """
        try:
            new_data_vacation = []
            new_data_removals = []

            for line in data_vacation:
                if int(line.get_value('CODI_EMP')) in self.__companies_calc:
                    try:
                        init_date_vacation = datetime.strptime(line.get_value('GOZO_INICIO'), '%d/%m/%Y')
                    except:
                        continue

                    if init_date_vacation < self.__init_competence:
                        new_data_vacation.append(line.do_output())
                else:
                    new_data_vacation.append(line.do_output())

            for line in data_removals:
                if int(line.get_value('CODI_EMP')) in self.__companies_calc:
                    try:
                        init_date_removal = datetime.strptime(line.get_value('DATA_REAL'), '%d/%m/%Y')
                    except:
                        continue

                    if init_date_removal < self.__init_competence:
                        new_data_removals.append(line.do_output())
                else:
                    new_data_removals.append(line.do_output())

            return new_data_vacation, new_data_removals
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: remove_entries - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)

    def check_acquisition_period(self, company, employee, end_acquisition):
        """
        Checa qual o ultimo periodo aquisitivo em aberto para determinado empregado,
        e se não for o período que deseja calcular, vai marcando como gozado até que o período esteja correto.
        """
        try:
            sybase = Sybase(self.__database, self.__username, self.__password)
            connection = sybase.connect()

            acquisition = sybase.select_acquisition_data(connection, company, employee)
            sybase.close_connection(connection)

            # se o periodo a ser calculado não é o ultimo em aberto, marca como gozado até chegar a ele
            if acquisition:
                if acquisition != end_acquisition:
                    # abrir tela de períodos aquisitivos do empregado
                    autoit.send("{ALT}PF{UP}{UP}{ENTER}")
                    sleep(2)
                    autoit.send(str(employee))
                    sleep(1)
                    autoit.send('{ENTER}')
                    sleep(1)

                    # seleciona o primeiro período da lista
                    autoit.send('{UP}{SPACE}')
                    options = 0
                    options_marked = 0
                    repeat = 0
                    old_date = ''

                    # enquanto não for o período que queremos calcular, vai marcando como gozado
                    while True:
                        sybase = Sybase(self.__database, self.__username, self.__password)
                        connection = sybase.connect()

                        acquisition = sybase.select_acquisition_data(connection, company, employee)
                        sybase.close_connection(connection)

                        # se o periodo a ser calculado é o ultimo em aberto, sai do loop
                        if acquisition:
                            if acquisition == end_acquisition:
                                autoit.send('{ESC}')
                                sleep(1)
                                break

                            # variável "repeat" marca quantos vezes passou pelo mesmo período aquisitivo
                            # se for mais que 30 vezes, pausa o processo e ignora o empregado, pois possivelmente
                            # entrou em loop
                            if repeat > 30:
                                autoit.send('{ESC}')
                                self.send_status(company, 'error',
                                                 message=f"""Não foi possível calcular as férias do empregado {employee} da empresa {company} com fim em {end_acquisition}, RPA entrou em loop no cálculo de férias""",
                                                 only_log=True)
                                sleep(1)

                                # adiciona na lista de empregados a serem ignorados
                                if str(company) not in ignore_employees.keys():
                                    ignore_employees[str(company)] = [str(employee)]
                                else:
                                    ignore_employees[str(company)].append(str(employee))

                                break

                            autoit.send('{TAB}{ENTER}')
                            sleep(1)

                            await_screen('[CLASS:FNWND3190]', 'Período Aquisitivo')
                            autoit.send('G{TAB}')
                            sleep(1)
                            date = autoit.control_get_text('', '[CLASSNN:PBEDIT1902]')
                            if old_date == date:
                                repeat += 1

                            old_date = date

                            sleep(1)
                            if date == end_acquisition:
                                autoit.send('{ESC}{ESC}')
                                sleep(1)
                                break
                            elif date == '00/00/0000':
                                autoit.send('{ESC}')
                                sleep(1)

                                if options_marked == 0:
                                    autoit.send('{TAB}')
                                else:
                                    autoit.send('{TAB}{TAB}{TAB}')

                                sleep(1)
                                autoit.send('{DOWN}{SPACE}')
                                options += 1
                                sleep(1)

                            else:
                                autoit.control_click('', '[CLASSNN:Button3]')
                                sleep(2)

                                # quando não é possível fechar o período aquisitivo
                                message = str(autoit.win_get_text('Atenção')).replace('\n', '')
                                if 'Alteração não permitida' in message:
                                    self.send_status(company, 'error',
                                                     message=f"""Não foi possível calcular as férias do empregado {employee} da empresa {company} com fim em {end_acquisition}, messagem do sistema: '{message}'""",
                                                     only_log=True)

                                    sleep(1)

                                    # adiciona na lista de empregados a serem ignorados
                                    if str(company) not in ignore_employees.keys():
                                        ignore_employees[str(company)] = [str(employee)]
                                    else:
                                        ignore_employees[str(company)].append(str(employee))

                                    autoit.send('{ENTER}')
                                    sleep(1)
                                    autoit.send('{ESC}{ESC}')
                                    sleep(1)
                                    break

                                options_marked += 1
                                autoit.send('{TAB}{TAB}{TAB}')
                                sleep(1)
                                autoit.send('{UP}{SPACE}')
                                sleep(1)
                                for _ in range(options_marked):
                                    autoit.send('{DOWN}{SPACE}')
                                    sleep(1)

                                for _ in range(options):
                                    autoit.send('{DOWN}{SPACE}')
                                    sleep(1)
                        else:
                            # se não retornar nenhum período quer dizer que todos estão gozados
                            # então adiciona no log e ignora o empregado
                            self.send_status(company, 'error',
                                             message=f"""Não foi possível calcular as férias do empregado {employee} da empresa {company} com fim em {end_acquisition}, todos os períodos aquisitivos já estão gozados!""",
                                             only_log=True)
                            sleep(1)

                            # adiciona na lista de empregados a serem ignorados
                            if str(company) not in ignore_employees.keys():
                                ignore_employees[str(company)] = [str(employee)]
                            else:
                                ignore_employees[str(company)].append(str(employee))

                            autoit.send('{ESC}')
                            sleep(1)
                            break
            else:
                # se não retornar nenhum período quer dizer que todos estão gozados
                # então adiciona no log e ignora o empregado
                self.send_status(company, 'error',
                                 message=f"""Não foi possível calcular as férias do empregado {employee} da empresa {company} com fim em {end_acquisition}, todos os períodos aquisitivos já estão gozados!""",
                                 only_log=True)

                sleep(1)

                # adiciona na lista de empregados a serem ignorados
                if str(company) not in ignore_employees.keys():
                    ignore_employees[str(company)] = [str(employee)]
                else:
                    ignore_employees[str(company)].append(str(employee))
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: check_acquisition_period - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)

    def check_bank_in_use(self, data_vacation):
        """
        Gera um novo sequencial para os registros da tabela FOFERIAS_GOZO
        """
        try:
            sybase = Sybase(self.__database, self.__username, self.__password)
            connection = sybase.connect()

            if not connection:
                return False

            dominio_vacation = sybase.select_data_vacation(connection)
            result = []
            for line in data_vacation:
                if str(line['CODI_EMP']) in dominio_vacation.keys():
                    if str(line['I_EMPREGADOS']) in dominio_vacation[str(line['CODI_EMP'])].keys():

                        dominio_vacation[str(line['CODI_EMP'])][str(line['I_EMPREGADOS'])] += 1
                        last_code = dominio_vacation[str(line['CODI_EMP'])][str(line['I_EMPREGADOS'])]

                        new_line = line
                        new_line['I_FERIAS_GOZO'] = last_code

                        result.append(new_line)
                    else:
                        result.append(line)
                else:
                    result.append(line)

            return result
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: check_bank_in_use - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)

    def separate_data_removals(self, data_removals):
        """
        Recebe os dados de afastamentos e retorna os afastamentos
        que não forem demissões e que estão dentro do período de
        competências calculadas
        """
        try:
            new_data_removals = []

            for line in data_removals:
                if int(line.get_value('CODI_EMP')) in self.__companies_calc:
                    try:
                        init_date_removal = datetime.strptime(line.get_value('DATA_REAL'), '%d/%m/%Y')
                    except:
                        continue
                    if init_date_removal >= self.__init_competence:
                        if int(line.get_value('I_AFASTAMENTOS')) != 8:
                            new_data_removals.append(line.do_output())

            return new_data_removals
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: separate_data_removals - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)

    def send_status(self, company, status, message='null', import_events=False, import_removals=False,
                    import_vacation=False, finish_process=False, only_log=False):
        """
        Retorna para o host uma atualização do progresso de cálculo
        """
        self.print_log("info", f"Enviando mensagem para o Host {message}")
        try:
            send_status = {
                'status': status,
                'message': message,
                'company': int(company),
                'import_events': import_events,
                'import_removals': import_removals,
                'import_vacation': import_vacation,
                'finish_process': finish_process,
                'only_log': only_log
            }
            serialized_dict = json.dumps(send_status)
            try:
                self.socket_connection.send(str.encode(serialized_dict))
            except Exception as e:
                self.print_log("warning", "Falha ao enviar mensagem")
                self.reconnect_host()
                try:
                    self.print_log("info", "Tentando enviar novamente a mensagem")
                    self.socket_connection.send(str.encode(serialized_dict))
                    self.print_log("info", "Mensagem enviada com sucesso")
                except:
                    self.print_log("critical", "Falha ao enviar mensagem")
            return
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: send_status - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.print_log("critical", function_error)
            return

    def create_folder(self, name_folder):
        """
        Cria um diretório no caminho especificado
        """
        try:
            if isdir(name_folder):
                rmtree(name_folder)
            mkdir(name_folder)
        except:
            return

    def create_users(self, number_users):
        """
        Criar usuários para o cálculo
        """
        self.print_log("info", f"Criando {number_users} usuário(s)")
        try:
            self.print_log("info", f"Abrindo tela de cadastro de usuários")
            sleep(3)
            autoit.win_activate('[CLASS:FNWND3190]')
            sleep(3)
            autoit.send('{ALT}C{UP}{UP}{RIGHT}{ENTER}')

            await_screen('[CLASS:FNWND3190]', 'Cadastro de Usuários')
            sleep(2)
            autoit.control_click('', '[CLASSNN:Button47]')
            sleep(2)
            for i in range(number_users):
                self.print_log("info", f"Cadastrando usuário {i + 1}")
                name_user = f'{self.BASE_NAME_USER}_{i + 1}'
                autoit.send('{TAB}')
                sleep(1)

                self.write(name_user)
                sleep(1)
                autoit.send('{TAB 2}')
                sleep(1)
                self.write(name_user)
                sleep(1)
                autoit.send('{TAB}')
                sleep(1)
                self.write(self.DEFAULT_PASSWORD_CREATED)
                sleep(1)
                autoit.send('{TAB}')
                sleep(1)
                self.write(self.DEFAULT_PASSWORD_CREATED)
                sleep(1)

                self.print_log("info", "Configurando acessos do usuários")
                # marcar acesso a todos os módulos
                autoit.control_click('', '[CLASSNN:Button7]')
                sleep(1)
                autoit.control_click('', '[CLASSNN:Button9]')
                sleep(1)
                autoit.control_click('', '[CLASSNN:Button16]')
                sleep(1)
                autoit.control_click('', '[CLASSNN:Button17]')
                sleep(1)
                autoit.control_click('', '[CLASSNN:Button18]')
                sleep(1)
                autoit.control_click('', '[CLASSNN:Button19]')
                sleep(1)
                autoit.control_click('', '[CLASSNN:Button20]')
                sleep(1)
                autoit.control_click('', '[CLASSNN:Button21]')
                sleep(1)
                autoit.control_click('', '[CLASSNN:Button22]')
                sleep(2)
                autoit.control_click('', '[CLASSNN:Button23]')
                sleep(1)
                autoit.control_click('', '[CLASSNN:Button28]')
                sleep(1)
                autoit.control_click('', '[CLASSNN:Button30]')
                sleep(1)

                # marcar acesso a importação de tabelas
                autoit.control_click('', '[CLASSNN:Edit3]')
                sleep(1)
                autoit.send('{TAB 9}')
                sleep(1)
                self.print_log("info", "Gravando usuário")
                autoit.send('{SPACE}')
                sleep(2)
                autoit.control_click('', '[CLASSNN:Button49]')

                while True:
                    try:
                        if autoit.control_get_text('', '[CLASSNN:Edit16]') == '':
                            break
                    except:
                        pass

                sleep(5)
                self.send_status(0, 'progress', message=name_user, only_log=True)

            autoit.send('{ESC}')
            sleep(2)
        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: create_users - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)
            self.print_log("critical", function_error)

    def disable_users(self):
        """
        Desativar usuários utilizados no cálculo
        """
        try:
            # consulta o banco para coletar os códigos de usuários que precisam ser desativados
            sybase = Sybase(self.__database, self.__username, self.__password)
            connection = sybase.connect()

            if not connection:
                self.send_status(self.__company, 'error', message='Erro de conexão com banco de dados Domínio')

            disable_users = sybase.select_users(connection, self.BASE_NAME_USER)
            sybase.close_connection(connection)

            sleep(3)
            if len(disable_users) > 0:
                autoit.send('{ALT}C{UP}{UP}{RIGHT}{ENTER}')

                await_screen('[CLASS:FNWND3190]', 'Cadastro de Usuários')
                sleep(2)
                for i in disable_users:
                    autoit.control_click('', '[CLASSNN:Button48]')
                    sleep(1)
                    self.write(str(i))
                    sleep(1)
                    autoit.send('{TAB}')
                    sleep(1)
                    autoit.send('{TAB 6}')
                    sleep(1)
                    autoit.send('I')
                    sleep(2)
                    autoit.control_click('', '[CLASSNN:Button49]')

                    while True:
                        try:
                            if autoit.control_get_text('', '[CLASSNN:Edit16]') == '':
                                break
                        except:
                            pass

                    sleep(3)

        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: disable_users - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)

    def close_dominio(self):
        """
        Fechar sistema Domínio
        """
        try:
            autoit.send('{ALT}C{UP}{ENTER}')
            sleep(5)

            while True:
                if autoit.win_active('Backup'):
                    sleep(1)
                    autoit.control_click('', '[CLASSNN:Button2]')
                    sleep(1)

                if autoit.win_active('Sair'):
                    sleep(1)
                    autoit.control_click('', '[CLASSNN:Button1]')
                    sleep(1)

                if not autoit.win_exists('[CLASS:FNWND3190]', text=''):
                    break

        except Exception as e:
            # dados para achar mais facilmente o erro
            _, _, exc_tb = exc_info()
            fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
            function_error = f'arquivo: {fname} - funcao: close_dominio - linha: {exc_tb.tb_lineno} - erro: {e}'
            self.send_status(-1, 'error', message=function_error)


def show_ip():
    gui = tk.Tk()
    gui.geometry('350x200')
    gui.title('Conversor de Movimento Thomson Reuters')

    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    message = tk.Label(gui, text=f'IP DO AGENTE: {ip_address}')
    message.place(relx=0.5, rely=0.5, anchor='center')
    gui.mainloop()


if __name__ == '__main__':
    download_def_db()
    rpa = Agent()

    Thread(target=show_ip).start()

    ip_host = rpa.await_data()
    rpa.extract_data_send()
    rpa.start(ip_host, f'{Path().absolute()}\\data\\conversao', [51, 41, 60, 52, 11, 70, 100, 42])