from datetime import datetime
from PySide6.QtCore import QObject, Signal
import logging
from os import remove, mkdir
from os.path import isfile, isdir
from shutil import copy, make_archive, move, rmtree, copytree
import json
import socket
from threading import Thread
import multiprocessing
from rpa.agent import Agent
from time import sleep

from extractors.Sybase import Sybase
from database.def_tables.def_tables import Table
from utils.check_functions_rpa import check_companies_calc
from utils.convert_log import ConvertLogHTML
from database.temp.rpa import (
    DominioFerias,
    DominioRescisoes
)


class RPA(QObject):
    finished = Signal()
    success = Signal(bool, str)
    progress = Signal(list)

    DEFAULT_PORT = 1112
    SIZE_BUFFER_PACKETS = 1024
    DEFAULT_USER = 'GERENTE'
    DEFAULT_PASSWORD = 'gerente'
    DEFAULT_PASSWORD_CREATED = '123456'

    def prepare(self, path_prontos, path_converion, init_competence, end_competence, companies_cal, database, username,
                password, sgd_username, sgd_password, local, machines):
        self.__conversion_path = str(path_converion).replace('.\\', "")
        self.__path_prontos = path_prontos
        self.__init_competence = datetime.strptime(f'01/{init_competence}', '%d/%m/%Y')
        self.__end_competence = datetime.strptime(f'01/{end_competence}', '%d/%m/%Y')
        self.__database = database
        self.__username = username
        self.__password = password
        self.__companies_calc = list(companies_cal)
        self.__sgd_username = sgd_username
        self.__sgd_password = sgd_password
        self.__machines = machines
        self.__local = local
        self.__current_company = -1

        logging.basicConfig(filename=f'{self.__conversion_path}\\Temp\\messages.log', encoding='utf-8',
                            level=logging.INFO, filemode='w')
        self.prepare_data_calc()
        self.save_companies_to_calc()

        if self.__machines:
            self.compact_data_calc()
            self.send_data(self.__machines)

    def create_folder(self, name_folder):
        """
        Cria um diretório no caminho especificado
        """
        if isdir(name_folder):
            rmtree(name_folder)
        mkdir(name_folder)

    def prepare_data_calc(self):
        """
        Gera na pasta "temp" da conversão, um arquivo zip com os dados necessários para calculos
        """
        self.create_folder(f'{self.__conversion_path}\\temp\\data_calc')
        self.create_folder(f'{self.__conversion_path}\\temp\\data_calc\\prontos')

        # cria um arquivo de configuração para o RPA
        config_data = {
            'init_competence': self.__init_competence.strftime('%d/%m/%Y'),
            'end_competence': self.__end_competence.strftime('%d/%m/%Y'),
            'database': self.__database,
            'username': self.__username,
            'password': self.__password,
            'sgd_username': self.__sgd_username,
            'sgd_password': self.__sgd_password
        }

        with open(f'{self.__conversion_path}\\temp\\data_calc\\run.conf', 'w') as outfile:
            json.dump(config_data, outfile)

        copy(f'{self.__path_prontos}\\2-Arquivos importacao\\FOAFASTAMENTOS_IMPORTACAO.txt',
             f'{self.__conversion_path}\\temp\\data_calc\\prontos')
        copy(f'{self.__path_prontos}\\2-Arquivos importacao\\FOFERIAS_GOZO.txt',
             f'{self.__conversion_path}\\temp\\data_calc\\prontos')
        copytree(f'{self.__conversion_path}\\Importar', f'{self.__conversion_path}\\temp\\data_calc\\Importar')
        copytree(f'{self.__conversion_path}\\SQLs', f'{self.__conversion_path}\\temp\\data_calc\\SQLs')
        copy(f'{self.__path_prontos}\\3-Comandos pos-importacao\\comando_ajusta_demitidos_importacao_ferias.sql',
             f'{self.__conversion_path}\\temp\\data_calc\\SQLs\\ajusta_demitidos.sql')
        copy(f'{self.__conversion_path}\\Temp\\temp.db', f'{self.__conversion_path}\\temp\\data_calc\\query.db')

    def compact_data_calc(self):
        """
        Compacta os dados necessários no calculo para serem enviados para as máquinas na rede
        """
        make_archive('send_data', 'zip', f'{self.__conversion_path}\\temp\\data_calc')
        if isfile(f'{self.__conversion_path}\\Temp\\send_data.zip'):
            remove(f'{self.__conversion_path}\\Temp\\send_data.zip')

        move('send_data.zip', f'{self.__conversion_path}\\Temp')

    def send_data(self, machines):
        """
        Manda os dados compactados via rede
        """
        for machine in machines:
            # abrir conexão com o agente para avisar que os dados começarão a ser enviados
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((machine, self.DEFAULT_PORT))
            sock.close()

            # criar um servidor socket para o agente e conectar
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('', self.DEFAULT_PORT))
            sock.listen(5)
            conn, _ = sock.accept()

            # enviar arquivo compactado
            with open(f'{self.__conversion_path}\\Temp\\send_data.zip', 'rb') as send_file:
                while True:
                    packet = send_file.read(self.SIZE_BUFFER_PACKETS)
                    if not packet:
                        break
                    conn.send(packet)

            conn.close()
            sock.close()

    def save_companies_to_calc(self):
        """
        Salva quais empresas e competências precisam ser calculadas,
        além de salvar quais importações precisam ser feitas
        """
        pass

    def get_dependents(self):
        """
        Coleta do banco de dados quais dependentes não tem data de
        nascimento, e imprime no log
        """
        sybase = Sybase(self.__database, self.__username, self.__password)
        connection = sybase.connect()

        result = sybase.select_dependents(connection)
        if result:
            self.invalid_records = True
            for line in result:
                message = f"Empresa {line['CODI_EMP']}, empregado {line['I_EMPREGADOS']}, o dependente {line['I_FILHOS']} com nome {line['NOME']} está sem data de nascimento!"
                self.print_in_log(info=message, cadastro=True)

    def get_service(self, remove_company):
        """
        Coleta do banco de dados quais serviços não tem o código
        FPAS preenchido
        """
        sybase = Sybase(self.__database, self.__username, self.__password)
        connection = sybase.connect()

        result = sybase.select_services(connection)
        if result:
            self.invalid_records = True
            for line in result:
                codi_emp = int(line.get('CODI_EMP'))
                if remove_company: self.remove_company_calc(codi_emp)

                message = f"Empresa {codi_emp}, a vigência {line['VIGENCIA']} do serviço {line['I_SERVICOS']}(inscrição {line['CGC']}) está sem o código FPAS preenchido!"
                self.print_in_log(info=message, cadastro=True)

    def get_resp_leval(self, remove_company):
        """
        Coleta do banco de dados quais empresas do tipo CPF
        não possuem dados de responsável legal
        """
        sybase = Sybase(self.__database, self.__username, self.__password)
        connection = sybase.connect()

        result = sybase.select_invalid_resp_leval(connection)
        if result:
            self.invalid_records = True
            for line in result:
                codi_emp = int(line.get('CODI_EMP'))
                if remove_company: self.remove_company_calc(codi_emp)

                message = f"Empresa {codi_emp} precisa ter os dados de responsável legal preenchidos!"
                self.print_in_log(info=message, cadastro=True)

    def remove_company_calc(self, codi_emp):
        """
        Remove uma empresa do cálculo
        """
        if int(codi_emp) in self.__companies_calc:
            self.__companies_calc.remove(int(codi_emp))

    def check_cadastral_conversion(self, remove_company=False):
        """
        Checa alguns pontos da parte cadastral que impactam no
        cálculo dos empregados
        """
        self.get_dependents()
        self.get_service(remove_company)
        self.get_resp_leval(remove_company)

    def init_local_agent(self):
        """
        Iniciar agente de execução na maquina host
        """
        try:
            process = multiprocessing.Pool()
            rpa = Agent()
            process.apply_async(rpa.start, args=(
            'localhost', f'{self.__conversion_path}\\Temp\\data_calc', [51, 41, 60, 52, 11, 70, 100, 42]))
            process.close()
            process.join()
        except Exception as e:
            self.print_in_log(error=str(e))
            return False

    def init_server_communication(self):
        """
        Inicia um servidor socket onde todas as estações irão se conectar
        """
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(('', self.DEFAULT_PORT))
            self.server.listen(5)
            self.__init_server = True
            return True
        except socket.error as e:
            self.print_in_log(error=str(e))
            return False

    def read_competences(self):
        """
        Ler os dados que precisam ser calculados(férias, rescisões e demais folhas)
        """
        try:
            result = {}
            ignore_companies = check_companies_calc(self.__database, self.__username, self.__password)
            total_competences = 0

            # dados de holerites
            data = Table('FOLANCAMENTOS_EVENTOS', file=f'{self.__conversion_path}\\Importar\\FOLANCAMENTOS_EVENTOS.txt')
            for item in data.items():
                if int(item['CODI_EMP']) not in ignore_companies and int(item['CODI_EMP']) in self.__companies_calc:
                    if int(item['CODI_EMP']) not in result.keys():
                        result[int(item['CODI_EMP'])] = {}

                    if item['COMPETENCIA_INICIAL'] not in result[int(item['CODI_EMP'])].keys():
                        result[int(item['CODI_EMP'])][item['COMPETENCIA_INICIAL']] = 1
                        total_competences += 1

            # dados de rescisões
            sqlite_rescisao = DominioRescisoes()
            sqlite_rescisao.connect(f'{self.__conversion_path}\\Temp\\temp.db')
            data_rescisao = sqlite_rescisao.select().dicts()

            # organizar os dados
            for row in data_rescisao:
                if int(row['codi_emp']) not in ignore_companies and int(row['codi_emp']) in self.__companies_calc:
                    if int(row['codi_emp']) not in result.keys():
                        result[int(row['codi_emp'])] = {}

                    if row['competencia'] not in result[int(row['codi_emp'])].keys():
                        result[int(row['codi_emp'])][row['competencia']] = 1
                        total_competences += 1

            # dados de férias
            sqlite_ferias = DominioFerias()
            sqlite_ferias.connect(f'{self.__conversion_path}\\Temp\\temp.db')
            data_vacation_calc = sqlite_ferias.select().dicts()

            for row in data_vacation_calc:
                competence_converted = row['competencia']

                if int(row['codi_emp']) not in ignore_companies and int(row['codi_emp']) in self.__companies_calc:
                    if int(row['codi_emp']) not in result.keys():
                        result[int(row['codi_emp'])] = {}

                    if competence_converted not in result[int(row['codi_emp'])].keys():
                        result[int(row['codi_emp'])][competence_converted] = 1
                        total_competences += 1

            return total_competences
        except Exception as e:
            self.print_in_log(error=str(e))

    def await_connections(self):
        """
        Espera as estações se conectarem ao servidor
        e abre uma thread para cada execução.
        """
        total_stations = len(self.__machines)
        if self.__local:
            total_stations += 1

        # o processo de calculo equivale a 65% da barra de progresso
        # e aqui dividimos os 65% pelo numero de competências a serem calculadas
        self.current_percent = 25
        total_competences = self.read_competences()

        self.sum_percent = (65 / total_competences)

        # etapas de importação
        self.__init_create_users = False
        self.__users_to_create = total_stations
        self.__end_create_users = False
        self.__init_import_events = False
        self.__end_import_events = False
        self.__init_import_removals = False
        self.__end_import_removals = False
        self.__init_import_vacation = False
        self.__end_import_vacation = False
        self.__init_calc = False
        self.__companies_calc_finished = []
        self.__init_finish_process = False
        self.__end_finish_process = False

        self.__user_connection = {}
        connections = 0
        try:
            while connections < total_stations:
                if self.__init_server:
                    try:
                        client, address = self.server.accept()
                        self.__user_connection[address[0]] = False
                        connections += 1
                        Thread(target=self.handle_client, args=(client, address[0])).start()
                    except Exception as e:
                        print(e)
                        self.print_in_log(error=str(e))

        except Exception as e:
            self.print_in_log(error=str(e))
            return False

    def await_new_connections(self):
        """
        Aguarda novas conexões dos clientes caso ocorra algum problema com a conexão primaria
        e abre uma thread para cada execução.
        """
        try:
            while True:
                if self.__init_server:
                    try:
                        client, address = self.server.accept()
                        Thread(target=self.handle_client, args=(client, address[0])).start()
                    except Exception as e:
                        print(e)
                        self.print_in_log(error=str(e))

        except Exception as e:
            self.print_in_log(error=str(e))
            return False

    def send_action(self, action, company, connection, user='', password='', number_users=0):
        """
        Retorna para a estação a ação que ela precisa executar
        """
        if user == '':
            user = self.DEFAULT_USER

        if password == '':
            password = self.DEFAULT_PASSWORD

        send_action = {
            'action': action,
            'current_company': company,
            'companies_calc': self.__companies_calc,
            'number_users': number_users,
            'user': user,
            'password': password
        }
        serialized_dict = json.dumps(send_action)
        connection.send(str.encode(serialized_dict))

    def handle_client(self, client, ip_client):
        """
        Função que distribui criação de usuários, importações e empresas entre as estações
        """
        try:
            first_company = False
            while True:
                sleep(2)

                # se tiver terminado o processo, envia um sinal para a estação encerrar
                if self.__end_finish_process:
                    self.send_action('quit', 0, client)
                    break

                # criar usuários para o cálculo
                if not self.__end_create_users:
                    if not self.__init_create_users:

                        # checa em quantas estações será executado o cálculo
                        # pois se for somente uma, utiliza só o usuário padrão
                        if self.__users_to_create > 1:
                            self.__init_create_users = ip_client
                            self.__user_connection[ip_client] = 'GERENTE'
                            self.send_action('create_users', 0, client, number_users=(self.__users_to_create - 1))
                        else:
                            self.__user_connection[ip_client] = 'GERENTE'
                            self.send_action('open_dominio', 0, client)
                            sleep(5)

                            request = client.recv(self.SIZE_BUFFER_PACKETS).decode('utf8')
                            data = json.loads(request)

                            if data['status'] == 'finish':
                                self.__end_create_users = True

                            if data['status'] == 'error':
                                error = data['message']
                                company = int(data['company'])

                                if company == -1:
                                    self.print_in_log(
                                        error=f"Erro durante execução da maquina {ip_client} exceção: '{error}'")
                                    self.send_action('quit', 0, client)
                                    break
                                else:
                                    self.print_in_log(
                                        error=f"Erro de cálculo na máquina {ip_client} exceção: '{error}'")
                    else:
                        # para a estação que está criando os usuários
                        # fica checando o progresso, pois a cada sinal de
                        # progresso é enviado o usuário que foi criado
                        if ip_client == self.__init_create_users:
                            if self.__users_to_create != 0:
                                request = client.recv(self.SIZE_BUFFER_PACKETS).decode('utf8')
                                data = json.loads(request)

                                if data['status'] == 'finish':
                                    self.__users_to_create -= 1

                                if data['status'] == 'progress':
                                    user = data['message']
                                    self.print_in_log(info=f'criado usuário {user}')
                                    self.__users_to_create -= 1
                                    for ip in self.__user_connection:
                                        if not self.__user_connection[ip]:
                                            self.__user_connection[ip] = user
                                            break

                                if data['status'] == 'error':
                                    error = data['message']
                                    company = int(data['company'])

                                    if company == -1:
                                        self.print_in_log(
                                            error=f"Erro durante execução da maquina {ip_client} exceção: '{error}'")
                                        self.send_action('quit', 0, client)
                                        break
                                    else:
                                        self.print_in_log(
                                            error=f"Erro de cálculo na máquina {ip_client} exceção: '{error}'")

                        else:
                            # estações ficam esperando até que seja disponibilizado um usuário para acesso
                            if ip_client in self.__user_connection.keys():
                                if not self.__user_connection[ip_client]:
                                    send_user = False
                                    while not send_user:
                                        if self.__user_connection[ip_client]:
                                            self.send_action('open_dominio', 0, client,
                                                             user=self.__user_connection[ip_client],
                                                             password=self.DEFAULT_PASSWORD_CREATED)
                                            send_user = True

                                    request = client.recv(self.SIZE_BUFFER_PACKETS).decode('utf8')
                                    data = json.loads(request)

                                    if data['status'] == 'finish':
                                        if self.__users_to_create == 0:
                                            self.__end_create_users = True

                                    if data['status'] == 'error':
                                        error = data['message']
                                        company = int(data['company'])

                                        if company == -1:
                                            self.print_in_log(
                                                error=f"Erro durante execução da maquina {ip_client} exceção: '{error}'")
                                            self.send_action('quit', 0, client)
                                            break
                                        else:
                                            self.print_in_log(
                                                error=f"Erro de cálculo na máquina {ip_client} exceção: '{error}'")

                # quando termina a criação de usuários avança para as importação e cálculos
                if self.__end_create_users:
                    if not self.__init_calc:

                        self.progress.emit([f'Importando dados...', 20])

                        check_result = False
                        if ip_client == self.__init_import_events and not self.__end_import_events:
                            request = client.recv(self.SIZE_BUFFER_PACKETS).decode('utf8')
                            data = json.loads(request)
                            check_result = True

                        if ip_client == self.__init_import_removals and not self.__end_import_removals:
                            request = client.recv(self.SIZE_BUFFER_PACKETS).decode('utf8')
                            data = json.loads(request)
                            check_result = True

                        if ip_client == self.__init_import_vacation and not self.__end_import_vacation:
                            request = client.recv(self.SIZE_BUFFER_PACKETS).decode('utf8')
                            data = json.loads(request)
                            check_result = True

                        if check_result:
                            if data['status'] == 'progress':
                                company = data['company']
                                message = data['message']
                                self.print_in_log(info=message)

                            if data['status'] == 'finish':
                                if data['import_events']:
                                    self.__end_import_events = True

                                if data['import_removals']:
                                    self.__end_import_removals = True

                                if data['import_vacation']:
                                    self.__end_import_vacation = True

                            if data['status'] == 'error':
                                error = data['message']
                                company = int(data['company'])

                                if company == -1:
                                    self.print_in_log(
                                        error=f"Erro durante execução da maquina {ip_client} exceção: '{error}'")
                                    self.send_action('quit', 0, client)
                                    break
                                else:
                                    self.print_in_log(
                                        error=f"Erro de cálculo na máquina {ip_client} exceção: '{error}'")

                    # inicia a importação de lançamentos
                    if not self.__init_import_events:
                        self.send_action('import_events', 0, client)
                        self.__init_import_events = ip_client

                    # inicia a importação de afastamentos em uma máquina diferente
                    # ou quando só houver uma maquina, espera a importação de lançamentos
                    if not self.__init_import_removals:
                        if ip_client != self.__init_import_events:
                            self.send_action('import_removals', 0, client)
                            self.__init_import_removals = ip_client
                        else:
                            if self.__end_import_events:
                                self.send_action('import_removals', 0, client)
                                self.__init_import_removals = ip_client

                    # inicia a importação de férias quando os lançamentos e
                    # afastamentos já tiverem sido importados
                    if not self.__init_import_vacation and self.__end_import_events and self.__end_import_removals:
                        self.send_action('import_vacation', 0, client)
                        self.__init_import_vacation = ip_client

                    if self.__end_import_events and self.__end_import_removals and self.__end_import_vacation and not self.__init_calc:
                        self.progress.emit(['Iniciando cálculos...', 25])
                        self.__init_calc = True

                        # se todas as empresas tiverem sido finalizadas, inicia o processo final
                    if len(self.__companies_calc) == len(self.__companies_calc_finished):
                        if not self.__init_finish_process:

                            # inicia o processo final na estação que tem o usuário GERENTE
                            if self.__user_connection[ip_client] == 'GERENTE':
                                self.__init_finish_process = ip_client
                                self.send_action('finish_process', 0, client)
                                self.progress.emit([f'Finalizando processo...', 95])
                                sleep(2)

                        if ip_client == self.__init_finish_process:
                            request = client.recv(self.SIZE_BUFFER_PACKETS).decode('utf8')
                            data = json.loads(request)

                            if data['status'] == 'progress':
                                message = data['message']
                                self.print_in_log(info=message)

                            if data['status'] == 'finish':
                                if data['finish_process']:
                                    self.__end_finish_process = True

                            if data['status'] == 'error':
                                error = data['message']
                                company = int(data['company'])

                                if company == -1:
                                    self.print_in_log(
                                        error=f"Erro durante execução da maquina {ip_client} exceção: '{error}'")
                                    self.send_action('quit', 0, client)
                                    break
                                else:
                                    self.print_in_log(
                                        error=f"Erro de cálculo na máquina {ip_client} exceção: '{error}'")
                        else:
                            self.send_action('quit', 0, client)
                            break

                    # fica checando o progresso das estações e
                    # atualizando a barra de progresso
                    if self.__init_calc and not self.__init_finish_process:
                        if not first_company:
                            self.__current_company += 1
                            self.send_action('calc', int(self.__companies_calc[self.__current_company]), client)
                            first_company = True

                        request = client.recv(self.SIZE_BUFFER_PACKETS).decode('utf8')
                        data = json.loads(request)

                        company = data['company']

                        if data['status'] == 'finish':
                            if len(self.__companies_calc) - 1 > self.__current_company:
                                self.__current_company += 1
                                self.send_action('calc', int(self.__companies_calc[self.__current_company]), client)
                                if int(company) != 0:
                                    self.progress.emit(
                                        [f'Cálculo da empresa {company} finalizado...', self.current_percent])
                                    self.print_in_log(info=f"Fim dos cálculos da empresa {company}")
                                    self.__companies_calc_finished.append(company)
                            else:
                                if int(company) != 0:
                                    self.print_in_log(info=f"Fim dos cálculos da empresa {company}")
                                    self.__companies_calc_finished.append(company)

                                    # se chegou na ultima empresa e não for a estação com usuário GERENTE, encerra a estação
                                    if self.__user_connection[ip_client] != 'GERENTE':
                                        self.send_action('quit', 0, client)
                                        break

                        elif data['status'] == 'progress':
                            message = data['message']
                            only_log = bool(data['only_log'])
                            if not only_log:
                                self.current_percent += self.sum_percent
                                self.progress.emit([f'Calculando empresa {company}...', self.current_percent])

                            self.print_in_log(info=message)
                        elif data['status'] == 'error':
                            error = data['message']
                            company = int(data['company'])

                            if company == -1:
                                self.print_in_log(
                                    error=f"Erro durante cálculo da empresa {company} na maquina {ip_client} exceção: '{error}'")
                                self.send_action('quit', 0, client)
                                break
                            else:
                                self.print_in_log(error=f"Erro de cálculo na máquina {ip_client} exceção: '{error}'")

            client.close()
        except Exception as e:
            self.print_in_log(error=e)
            self.print_in_log(end=True)
            self.success.emit(False, 'Erro ao executar cálculos!')
            self.finished.emit()

    def print_in_log(self, init=False, end=False, error=False, info=False, cadastro=False):
        """
        Função para gravar dados no arquivo de log
        """
        try:
            if init:
                logging.info(f"{datetime.today().strftime('%d/%m/%Y %H:%M:%S')}:Execução iniciada")

            if end:
                logging.info(f"{datetime.today().strftime('%d/%m/%Y %H:%M:%S')}:Execução finalizada")

            if error:
                while True:
                    if '\r' in error:
                        error = str(error).replace('\r', '')
                    if '\n' in error:
                        error = str(error).replace('\n', '')
                    else:
                        break

                if cadastro:
                    error = f'cadastro:{error}'
                else:
                    error = f'calculo:{error}'

                logging.error(f"{datetime.today().strftime('%d/%m/%Y %H:%M:%S')}:{error}")

            if info:
                while True:
                    if '\r' in info:
                        info = str(info).replace('\r', '')
                    if '\n' in info:
                        info = str(info).replace('\n', '')
                    else:
                        break

                if cadastro:
                    info = f'cadastro:{info}'
                else:
                    info = f'calculo:{info}'

                logging.info(f"{datetime.today().strftime('%d/%m/%Y %H:%M:%S')}:{info}")
        except Exception:
            print("Erro gravando dados no log")

    def invalid_cadastral_conversion(self):
        """
        Validar conversão cadastral
        """
        self.invalid_records = False

        self.check_cadastral_conversion()
        if self.invalid_records:
            ConvertLogHTML(f'{self.__conversion_path}\\Temp\\messages.log')

        return self.invalid_records

    def start(self):
        try:
            self.print_in_log(init=True)
            self.progress.emit(['Criando arquivo de log...', 5])

            self.check_cadastral_conversion(remove_company=True)

            self.progress.emit(['Preparando agentes de execução...', 10])
            self.__init_server = False
            Thread(target=self.init_server_communication).start()

            if self.__local:
                Thread(target=self.init_local_agent).start()

            self.progress.emit(['Distribuindo empresas entre os agentes...', 12])
            self.await_connections()

            self.progress.emit(['Configurando ambiente para cálculo...', 15])

            # Fica verificando novas conexões
            Thread(target=self.await_new_connections).start()
            # aguarda enquanto estiver agentes em execução
            while not self.__end_finish_process:
                sleep(3)

            self.print_in_log(end=True)
            ConvertLogHTML(f'{self.__conversion_path}\\Temp\\messages.log', ignore_firts_lines=True)
            self.success.emit(True, '')
            self.finished.emit()
        except Exception as e:
            self.print_in_log(error=e)
            self.print_in_log(end=True)
            self.success.emit(False, 'Erro ao executar cálculos!')
            self.finished.emit()