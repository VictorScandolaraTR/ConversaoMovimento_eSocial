import os, shutil, json, xmltodict, Levenshtein
from tqdm import tqdm
from sqlalchemy import create_engine
import xml.dom.minidom as xml
import pandas as pd

from src.classes.Table import Table
from src.classes.StorageData import StorageData
from src.classes.Sequencial import Sequencial
from src.database.Sybase import Sybase
from src.database.SQLite_tables import *
from src.utils.functions import *
from src.database.data_rubrics import *
from src.database.depara import *

class eSocialXML():
    def __init__(self, diretorio_xml):
        self.DIRETORIO_RAIZ = diretorio_xml
        self.DIRETORIO_XML = f"{diretorio_xml}\\eventos"
        self.DIRETORIO_DOWNLOADS = f"{diretorio_xml}\\downloads"
        self.DIRETORIO_SAIDA = f"{diretorio_xml}\\saida"
        self.DIRETORIO_RPA = f"{diretorio_xml}\\rpa"
        self.DIRETORIO_IMPORTAR = f"{diretorio_xml}\\rpa\\Importar"
        self.BANCO_SQLITE = f"{diretorio_xml}\\rpa\\query.db"
        self.INIT_COMPETENCE = '01/01/2022'
        self.END_COMPETENCE = '01/01/2023'

        self.dicionario_rubricas_dominio = {} # Rubricas Domínio
        self.dicionario_s1010 = {} # Rubricas
        self.dicionario_s1200 = {} # Remuneração Regime Previdenciário Geral
        self.dicionario_s1202 = {} # Remuneração Regime Previdenciário Próprio
        self.dicionario_s1210 = {} # Pagamentos de Rendimentos do Trabalho
        self.dicionario_s2230 = {} # Afastamentos temporários
        self.dicionario_s2299 = {} # Demissão
        self.dicionario_s2399 = {} # Demissão (contribuintes)

        # Parâmetros de operação
        try:
            self.carrega_parametros()
        except:
            self.base_dominio = "Contabil"
            self.usuario_dominio = "EXTERNO"
            self.senha_dominio = "123456"
            self.empresa_padrao_rubricas = "9999"
            self.usuario_esocial = ""
            self.senha_esocial = ""
            self.certificado_esocial = ""
            self.tipo_certificado_esocial = "A1"

        # cria as pastas necessárias
        create_folder(self.DIRETORIO_XML)
        create_folder(self.DIRETORIO_DOWNLOADS)
        create_folder(self.DIRETORIO_RPA)
        create_folder(self.DIRETORIO_IMPORTAR)

    def carrega_parametros(self):
        '''Carrega os parâmetros utilizados do arquivo parametros.json'''

        f = open(f"{self.DIRETORIO_RAIZ}\\parametros.json","r")
        parametros_texto = f.readline()
        f.close

        parametros = json.loads(parametros_texto)

        self.base_dominio = parametros["base_dominio"]
        self.usuario_dominio = parametros["usuario_dominio"]
        self.senha_dominio = parametros["senha_dominio"]
        self.empresa_padrao_rubricas = parametros["empresa_padrao_rubricas"]
        self.usuario_esocial = parametros["usuario_esocial"]
        self.senha_esocial = parametros["senha_dominio"]
        self.certificado_esocial = parametros["certificado_esocial"]
        self.tipo_certificado_esocial = parametros["tipo_certificado_esocial"]

    def salvar_parametros(self):
        '''Salva os parâmetros utilizados no arquivo parametros.json'''

        parametros = {
            "base_dominio": self.base_dominio,
            "usuario_dominio": self.usuario_dominio,
            "senha_dominio": self.senha_dominio,
            "empresa_padrao_rubricas": self.empresa_padrao_rubricas,
            "usuario_esocial": self.usuario_esocial,
            "senha_esocial": self.senha_esocial,
            "certificado_esocial": self.certificado_esocial,
            "tipo_certificado_esocial": self.tipo_certificado_esocial
        }

        f = open(f"{self.DIRETORIO_RAIZ}\\parametros.json","w")
        f.write(json.dumps(parametros))
        f.close
    
    def baixar_dados_esocial(self):
        '''Acessa o portal e-Social com as credenciais necessárias e faz download dos arquivos do período'''
        pass

    def configura_conexao_esocial(self,usuario,senha,certificado,tipo_certificado = "A1"):
        '''Configura conexão da classe com o portal e-Social'''
        self.usuario_esocial, self.senha_esocial, self.certificado_esocial, self.tipo_certificado_esocial = usuario, senha, certificado, tipo_certificado
        self.salvar_parametros()

    def configura_conexao_dominio(self,banco,usuario,senha,empresa_padrao = "9999"):
        '''Configura conexão da classe com o banco Domínio'''
        self.base_dominio, self.usuario_dominio, self.senha_dominio, self.empresa_padrao_rubricas = banco, usuario, senha, empresa_padrao
        self.salvar_parametros()

    def extrair_arquivos_xml(self):
        '''Extrai os arquivos .zip que foram baixados do Portal e-Social'''
        for root, dirs, files in os.walk(self.DIRETORIO_DOWNLOADS):
            arquivos = files.copy()

        print("Extraindo dados obtidos do portal")
        os.system("del /q "+self.DIRETORIO_XML)
        for arquivo in tqdm(arquivos):
            if str(arquivo[-3::]).upper()=="ZIP":
                shutil.unpack_archive(f"{self.DIRETORIO_DOWNLOADS}\\{arquivo}", self.DIRETORIO_XML)

    def carregar_informacoes_xml(self):
        '''Carrega as informações dos XMLs dos eventos do e-Social para os dicionários da classe'''

        self.dicionario_s1010["inclusao"] = {}
        self.dicionario_s1010["alteracao"] = {}

        eventos_nao_tratados = []

        for root, dirs, files in os.walk(self.DIRETORIO_XML):
            arquivos = files.copy()

        print("Carregando informações dos eventos")
        for arquivo in tqdm(arquivos):
            if (arquivo==".gitignore"): continue

            try:
                doc = xml.parse(self.DIRETORIO_XML+"\\"+arquivo)

                for eSocial in doc.getElementsByTagName("eSocial"):
                    xmlns = eSocial.getAttribute("xmlns")
                    if(xmlns==None): evento = ""
                    elif(xmlns==""): evento = ""
                    else: evento = xmlns.split('/')[-2]

                    match evento:
                        case "evtTabRubrica": # S-1010
                            s1010 = xmltodict.parse(eSocial.toxml())
                            s1010_sem_assinatura = s1010.get("eSocial").get("evtTabRubrica")
                            id_s1010 = s1010_sem_assinatura["@Id"]

                            if(s1010_sem_assinatura.get("infoRubrica").get("inclusao")):
                                self.dicionario_s1010["inclusao"][id_s1010] = s1010_sem_assinatura
                            else:
                                self.dicionario_s1010["alteracao"][id_s1010] = s1010_sem_assinatura

                        case "evtRemun": # S-1200
                            s1200 = xmltodict.parse(eSocial.toxml(),encoding="UTF-8")
                            s1200_sem_assinatura = s1200.get("eSocial").get("evtRemun")
                            id_s1200 = s1200_sem_assinatura["@Id"]

                            self.dicionario_s1200[id_s1200] = s1200_sem_assinatura

                        case "evtRmnRPPS": # S-1202
                            s1202 = xmltodict.parse(eSocial.toxml(),encoding="UTF-8")
                            s1202_sem_assinatura = s1202.get("eSocial").get("evtRmnRPPS")
                            id_s1202 = s1202_sem_assinatura["@Id"]

                            self.dicionario_s1202[id_s1202] = s1202_sem_assinatura

                        case "evtPgtos": # S-1210
                            s1210 = xmltodict.parse(eSocial.toxml(),encoding="UTF-8")
                            s1210_sem_assinatura = s1210.get("eSocial").get("evtPgtos")
                            id_s1210 = s1210_sem_assinatura["@Id"]

                            self.dicionario_s1210[id_s1210] = s1210_sem_assinatura

                        case "evtAfastTemp": # S-2230
                            s2230 = xmltodict.parse(eSocial.toxml(),encoding="UTF-8")
                            s2230_sem_assinatura = s2230.get("eSocial").get("evtAfastTemp")
                            id_s2230 = s2230_sem_assinatura["@Id"]

                            self.dicionario_s2230[id_s2230] = s2230_sem_assinatura

                        case "evtDeslig": # S-2299
                            s2299 = xmltodict.parse(eSocial.toxml(),encoding="UTF-8")
                            s2299_sem_assinatura = s2299.get("eSocial").get("evtDeslig")
                            id_s2299 = s2299_sem_assinatura["@Id"]

                            self.dicionario_s2299[id_s2299] = s2299_sem_assinatura

                        case "evtTSVTermino": # S-2399
                            s2399 = xmltodict.parse(eSocial.toxml(),encoding="UTF-8")
                            s2399_sem_assinatura = s2399.get("eSocial").get("evtTSVTermino")
                            id_s2399 = s2399_sem_assinatura["@Id"]

                            self.dicionario_s2399[id_s2399] = s2399_sem_assinatura

                        case _:
                            if evento not in eventos_nao_tratados:
                                eventos_nao_tratados.append(evento)

            except Exception as e:
                print(f"Erro:{arquivo}")
                print(e)

        self.dicionario_s1010 = self.processar_rubricas()

        f = open(f"{self.DIRETORIO_RAIZ}\\eventos_nao_tratados.json","w")
        f.write(json.dumps(eventos_nao_tratados))
        f.close()

    def processar_rubricas(self):
        dicionario_rubricas = self.dicionario_s1010.get("inclusao")
        dicionario_alteracoes = {}

        if(self.dicionario_s1010.get("alteracao")):
            for alteracao in self.dicionario_s1010["alteracao"]:
                inscricao = self.dicionario_s1010["alteracao"][alteracao].get("ideEmpregador").get("nrInsc")
                codigo_rubrica = self.dicionario_s1010["alteracao"][alteracao].get("infoRubrica").get("alteracao").get("ideRubrica").get("codRubr")
                tabela_rubrica = self.dicionario_s1010["alteracao"][alteracao].get("infoRubrica").get("alteracao").get("ideRubrica").get("ideTabRubr")
                dados_rubrica = self.dicionario_s1010["alteracao"][alteracao].get("infoRubrica").get("alteracao").get("dadosRubrica")

                dicionario_alteracoes[f"{inscricao}-{codigo_rubrica}-{tabela_rubrica}"] = {
                    "dscRubr": dados_rubrica.get("dscRubr"),
                    "natRubr": dados_rubrica.get("natRubr"),
                    "tpRubr": dados_rubrica.get("tpRubr"),
                    "codIncCP": dados_rubrica.get("codIncCP"),
                    "codIncIRRF": dados_rubrica.get("codIncIRRF"),
                    "codIncFGTS": dados_rubrica.get("codIncFGTS"),
                    "codIncSIND": dados_rubrica.get("codIncSIND")
                }
        
        if(dicionario_alteracoes):
            for inclusao in dicionario_rubricas:
                inscricao = dicionario_rubricas[inclusao].get("ideEmpregador").get("nrInsc")
                codigo_rubrica = dicionario_rubricas[inclusao].get("infoRubrica").get("inclusao").get("ideRubrica").get("codRubr")
                tabela_rubrica = dicionario_rubricas[inclusao].get("infoRubrica").get("inclusao").get("ideRubrica").get("ideTabRubr")
                
                if(dicionario_alteracoes.get(f"{inscricao}-{codigo_rubrica}-{tabela_rubrica}")):
                    alteracoes = dicionario_alteracoes.get(f"{inscricao}-{codigo_rubrica}-{tabela_rubrica}")

                    if(alteracoes.get("dscRubr")):
                        dicionario_rubricas[inclusao]["infoRubrica"]["inclusao"]["dadosRubrica"]["dscRubr"] = alteracoes.get("dscRubr")

                    if(alteracoes.get("natRubr")):
                        dicionario_rubricas[inclusao]["infoRubrica"]["inclusao"]["dadosRubrica"]["natRubr"] = alteracoes.get("natRubr")

                    if(alteracoes.get("tpRubr")):
                        dicionario_rubricas[inclusao]["infoRubrica"]["inclusao"]["dadosRubrica"]["tpRubr"] = alteracoes.get("tpRubr")
                    
                    if(alteracoes.get("codIncCP")):
                        dicionario_rubricas[inclusao]["infoRubrica"]["inclusao"]["dadosRubrica"]["codIncCP"] = alteracoes.get("codIncCP")

                    if(alteracoes.get("codIncIRRF")):
                        dicionario_rubricas[inclusao]["infoRubrica"]["inclusao"]["dadosRubrica"]["codIncIRRF"] = alteracoes.get("codIncIRRF")

                    if(alteracoes.get("codIncFGTS")):
                        dicionario_rubricas[inclusao]["infoRubrica"]["inclusao"]["dadosRubrica"]["codIncFGTS"] = alteracoes.get("codIncFGTS")

                    if(alteracoes.get("codIncSIND")):
                        dicionario_rubricas[inclusao]["infoRubrica"]["inclusao"]["dadosRubrica"]["codIncSIND"] = alteracoes.get("codIncSIND")

        return dicionario_rubricas

    def relaciona_empresas(self,inscricao):
        '''Gera listagem de empresas que tem rubricas sendo tratadas'''
        dicionario_empresas = {}
        inscricoes_originais = {}
        cgcs_rubricas = []

        engine = create_engine("sybase+pyodbc://{user}:{pw}@{dsn}".format(user=self.usuario_dominio, pw=self.senha_dominio, dsn=self.base_dominio))

        sql = "SELECT * FROM BETHADBA.GEEMPRE WHERE CGCE_EMP IN ('{cgc}','{cgc_comp}')".format(cgc=inscricao,cgc_comp=self.completar_cnpj(inscricao))
        df_empresas = pd.read_sql(sql,con=engine)

        for i in range(len(df_empresas)):
            inscricao = df_empresas.loc[i,"cgce_emp"]
            codigo = df_empresas.loc[i,"codi_emp"]
            nome = df_empresas.loc[i,"nome_emp"]

            dicionario_empresas[i] = {
                "codigo": codigo,
                "nome": nome,
                "cgc": inscricao
            }

        return dicionario_empresas

    def relaciona_empregados(self):
        """
        Gera um dicionário dos empregados que cada empresa possui, deixando como chave o
        CPF do empregado
        """
        data_employees = {}

        engine = create_engine("sybase+pyodbc://{user}:{pw}@{dsn}".format(user=self.usuario_dominio, pw=self.senha_dominio, dsn=self.base_dominio))

        sql = "SELECT CODI_EMP, I_EMPREGADOS, CPF FROM BETHADBA.FOEMPREGADOS"
        df_empregados = pd.read_sql(sql, con=engine)

        for index, line in df_empregados.iterrows():
            codi_emp = str(line.get('CODI_EMP'))
            i_empregados = str(line.get('I_EMPREGADOS'))
            cpf = str(line.get('CPF'))

            if codi_emp not in data_employees.keys():
                data_employees[codi_emp] = {}

            if cpf not in data_employees[codi_emp].keys():
                data_employees[codi_emp][cpf] = i_empregados

        return data_employees

    def relaciona_rubricas(self, rubrica):
        '''Recebe como parâmetro uma rúbrica do concorrente e faz uma série de validações para relacionar com uma correspondente na Domínio.'''
        result = []
        tipo = ""
        
        info_rubrica = rubrica.get('infoRubrica').get('inclusao').get('dadosRubrica')

        match int(info_rubrica.get('tpRubr')):
            case 1: tipo = "P"
            case 2: tipo = "D"
            case 3: tipo = "I"
            case 4: tipo = "ID"
        
        descricao = info_rubrica.get('dscRubr')
        rubesocial = info_rubrica.get('natRubr')
        tpbaseinss = info_rubrica.get('codIncCP')
        tpbaseirrf = info_rubrica.get('codIncIRRF')
        tpbasefgts = info_rubrica.get('codIncFGTS')
        tpbasesindical = info_rubrica.get('codIncSIND')

        for rubrica in self.dicionario_rubricas_dominio:
            if(tipo==self.dicionario_rubricas_dominio.get(rubrica).get("tipo")):
                if(rubesocial==self.dicionario_rubricas_dominio.get(rubrica).get("rubesocial")):
                    if(tpbaseinss==self.dicionario_rubricas_dominio.get(rubrica).get("tpbaseinss")):
                        if(tpbaseirrf==self.dicionario_rubricas_dominio.get(rubrica).get("tpbaseirrf")):
                            if(tpbasefgts==self.dicionario_rubricas_dominio.get(rubrica).get("tpbasefgts")):
                                if(tpbasesindical):
                                    if(tpbasesindical==self.dicionario_rubricas_dominio.get(rubrica).get("tpbasesindical")):
                                        result.append(str(self.dicionario_rubricas_dominio.get(rubrica).get("i_eventos")))
                                else:
                                    result.append(str(self.dicionario_rubricas_dominio.get(rubrica).get("i_eventos")))

        if(len(result)==0):
            # Comparação através do algoritmo de Levenshtein
            menor_distancia_levenshtein = 50
                    
            for rubrica in self.dicionario_rubricas_dominio:
                distancia_levenshtein = Levenshtein.distance(
                    descricao.upper(),
                    str(self.dicionario_rubricas_dominio.get(rubrica).get("nome"))
                )

                if (distancia_levenshtein < menor_distancia_levenshtein):
                    menor_distancia_levenshtein = distancia_levenshtein
                    lista_relacoes_levenshtein = []
                    if(menor_distancia_levenshtein<3):
                        lista_relacoes_levenshtein.append(str(self.dicionario_rubricas_dominio.get(rubrica).get("i_eventos")))
                elif (distancia_levenshtein==menor_distancia_levenshtein):
                    if(menor_distancia_levenshtein<3):
                        lista_relacoes_levenshtein.append(str(self.dicionario_rubricas_dominio.get(rubrica).get("i_eventos")))

            for relacao in lista_relacoes_levenshtein:
                result.append(str(relacao))

        return list(set(result))

    def completar_cnpj(self,cnpj):
        '''Completa a inscrição da empresa Adicionando final de empresa matriz'''

        cnpj = cnpj+'0001'
        # Pega apenas os 12 primeiros dígitos do CNPJ e gera os 2 dígitos que faltam
        inteiros = list(map(int, cnpj))
        novo = inteiros[:12]

        prod = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        while len(novo) < 14:
            r = sum([x*y for (x, y) in zip(novo, prod)]) % 11
            if r > 1:
                f = 11 - r
            else:
                f = 0
            novo.append(f)
            prod.insert(0, 6)
        
        cnpj = ''.join([str(item) for item in novo])
        return cnpj

    def carregar_rubricas_dominio(self):
        '''Carrega rubricas'''

        self.dicionario_rubricas_dominio = {}
        engine = create_engine("sybase+pyodbc://{user}:{pw}@{dsn}".format(user=self.usuario_dominio, pw=self.senha_dominio, dsn=self.base_dominio))
        
        sql = f"SELECT * FROM BETHADBA.FOEVENTOS WHERE CODI_EMP = {self.empresa_padrao_rubricas}"
        df_rubricas = pd.read_sql(sql,con=engine)

        for i in range(len(df_rubricas)):
            i_eventos = str(df_rubricas.loc[i,'i_eventos'])
            nome = df_rubricas.loc[i,"nome"]
            tipo = df_rubricas.loc[i,"prov_desc"]
            rubesocial = str(df_rubricas.loc[i,'NATUREZA_FOLHA_MENSAL'])
            tpbaseinss = str(df_rubricas.loc[i,'CODIGO_INCIDENCIA_INSS_ESOCIAL'])
            tpbaseirrf = str(df_rubricas.loc[i,'CODIGO_INCIDENCIA_IRRF_ESOCIAL'])
            tpbasefgts = str(df_rubricas.loc[i,'CODIGO_INCIDENCIA_FGTS_ESOCIAL'])
            tpbasesindical = str(df_rubricas.loc[i,'CODIGO_INCIDENCIA_SINDICAL_ESOCIAL'])

            rubrica = {
                "i_eventos": i_eventos,
                "nome": nome,
                "tipo": tipo,
                "rubesocial": rubesocial,
                "tpbaseinss": tpbaseinss,
                "tpbaseirrf": tpbaseirrf,
                "tpbasefgts": tpbasefgts,
                "tpbasesindical": tpbasesindical
            }

            self.dicionario_rubricas_dominio[i_eventos] = rubrica
    
    def gera_excel_relacao(self, empresa):
        '''Gera o excel com as rubricas para relacionar com as rubricas padrão do Domínio'''

        linhas_excel_alerta = set()
        linhas_excel_relacionado = set()
        linhas_excel_nao_relacionado = set()
        linhas_excel_multirelacionado = set()
        relacao_dominio_esocial = {}
        lista_rubricas = []

        self.carregar_rubricas_dominio()
        
        print("Relacionando rubricas")
        for s1010 in tqdm(self.dicionario_s1010):
            inscricao = self.dicionario_s1010.get(s1010).get('ideEmpregador').get('nrInsc')
            
            if(inscricao==empresa):
                codigo = self.dicionario_s1010.get(s1010).get('infoRubrica').get('inclusao').get('ideRubrica').get('codRubr')

                if (codigo not in lista_rubricas):
                    lista_rubricas.append(codigo)

                    info_rubrica = self.dicionario_s1010.get(s1010).get('infoRubrica').get('inclusao').get('dadosRubrica')

                    match int(info_rubrica.get('tpRubr')):
                        case 1: tipo = "P"
                        case 2: tipo = "D"
                        case 3: tipo = "I"
                        case 4: tipo = "ID"
                    
                    nome = info_rubrica.get('dscRubr')
                    rubesocial = info_rubrica.get('natRubr')
                    tpbaseinss = info_rubrica.get('codIncCP')
                    tpbaseirrf = info_rubrica.get('codIncIRRF')
                    tpbasefgts = info_rubrica.get('codIncFGTS')
                    tpbasesindical = info_rubrica.get('codIncSIND')

                    lista_relacoes = self.relaciona_rubricas(self.dicionario_s1010.get(s1010))

                    if(len(lista_relacoes)==0):
                        linhas_excel_nao_relacionado.add((
                            codigo,
                            nome,
                            tipo,
                            rubesocial,
                            tpbaseinss,
                            tpbaseirrf,
                            tpbasefgts,
                            tpbasesindical,
                            "N"
                        ))
                    elif(len(lista_relacoes)==1):
                        linhas_excel_relacionado.add((
                            codigo,
                            nome,
                            tipo,
                            rubesocial,
                            tpbaseinss,
                            tpbaseirrf,
                            tpbasefgts,
                            tpbasesindical,
                            lista_relacoes[0],
                            "X"
                        ))

                        if(relacao_dominio_esocial.get(lista_relacoes[0])==None): relacao_dominio_esocial[lista_relacoes[0]] = []
                        relacao_dominio_esocial[lista_relacoes[0]].append(s1010)
                        
                    elif(len(lista_relacoes)>1):
                        print("Multi-relações")
                        linha = [
                            codigo,
                            nome,
                            tipo,
                            rubesocial,
                            tpbaseinss,
                            tpbaseirrf,
                            tpbasefgts,
                            tpbasesindical,
                            ""
                        ]

                        relacionamento_atual = 0
                        
                        while relacionamento_atual < 10:
                            if(relacionamento_atual < len(lista_relacoes)):
                                if(self.dicionario_rubricas_esocial.get(int(lista_relacoes[relacionamento_atual]))!=None):
                                    linha.append(lista_relacoes[relacionamento_atual])
                                    linha.append(self.dicionario_s1010.get(lista_relacoes[relacionamento_atual]).get("nome"))

                                    if(relacao_dominio_esocial.get(lista_relacoes[0])==None):
                                        relacao_dominio_esocial[lista_relacoes[0]] = []
                                    
                                    if(s1010 not in relacao_dominio_esocial[lista_relacoes[0]]): 
                                        relacao_dominio_esocial[lista_relacoes[0]].append(s1010)
                            else:
                                linha.append("")
                                linha.append("")

                            relacionamento_atual = relacionamento_atual + 1
                        
                        linhas_excel_multirelacionado.add(tuple(linha))
                    
        print("Imprimindo planilha")
        for relacao in relacao_dominio_esocial:
            if(len(relacao_dominio_esocial[relacao])>1):
                for rubrica in relacao_dominio_esocial[relacao]:
                    codigo = self.dicionario_s1010[rubrica]['infoRubrica']['inclusao']['ideRubrica']['codRubr']
                    info_rubrica = self.dicionario_s1010.get(rubrica).get("infoRubrica").get("inclusao").get("dadosRubrica")

                    match int(info_rubrica['tpRubr']):
                        case 1: tipo = "P"
                        case 2: tipo = "D"
                        case 3: tipo = "I"
                        case 4: tipo = "ID"
                    
                    nome = info_rubrica.get("dscRubr")
                    rubesocial = info_rubrica.get("natRubr")
                    tpbaseinss = info_rubrica.get("codIncCP")
                    tpbaseirrf = info_rubrica.get("codIncIRRF")
                    tpbasefgts = info_rubrica.get("codIncFGTS")
                    tpbasesindical = info_rubrica.get("codIncSIND")

                    linhas_excel_alerta.add((
                        codigo,
                        nome,
                        tipo,
                        rubesocial,
                        tpbaseinss,
                        tpbaseirrf,
                        tpbasefgts,
                        tpbasesindical,
                        relacao,
                        "X"
                    ))

        cabecalho_padrao = ['Código','Descrição','Tipo','Natureza Tributaria Rubrica','Incidencia INSS eSocial','Incidencia IRRF eSocial','Incidencia FGTS eSocial','Incidencia Sindical eSocial']
        cabecalho_relacionado = cabecalho_padrao + ['Código Domínio','"X" para manter o relacionamento \nou \nInforme a rúbrica equivalente \nou \n"N" para cadastrar a rúbrica']
        cabecalho_multirelacionado = cabecalho_padrao + ['Informe a rúbrica equivalente \nou \n"N" para cadastrar a rúbrica','Opção 1','Descrição 1','Opção 2','Descrição 2','Opção 3','Descrição 3','Opção 4','Descrição 4','Opção 5','Descrição 5','Opção 6','Descrição 6','Opção 7','Descrição 7','Opção 8','Descrição 8','Opção 9','Descrição 9','Opção 10','Descrição 10']
        cabecalho_nao_relacionado =  cabecalho_padrao + ['Informe a rúbrica equivalente \nou \n"N" para cadastrar a rúbrica']
        cabecalho_alerta = cabecalho_padrao + ['Código Domínio', '"X" para somar as rúbricas \nou \n"D" para desconsiderar as rúbricas duplicadas \nou \nInforme a rúbrica equivalente \nou \n"N" para cadastrar a rúbrica']

        self.imprime_excel(
            f'{self.DIRETORIO_RAIZ}\\relacao_rubricas.xlsx', 
            linhas_excel_relacionado, 
            cabecalho_relacionado, 
            linhas_excel_multirelacionado, 
            cabecalho_multirelacionado, 
            linhas_excel_nao_relacionado, 
            cabecalho_nao_relacionado, 
            linhas_excel_alerta, 
            cabecalho_alerta
        )

    def imprime_excel(self, output_file, data1, header1, data2, header2, data3, header3, data4, header4):
        """
        Recebe com parâmetro o nome do arquivo de saída, 3 dicionários e 3 cabeçalhos,
        e cria uma planilha com 3 abas com o relacionamento das rúbricas.
        """
        writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
        workbook  = writer.book

        # formatação cabeçalhos
        header_format_concorrente = workbook.add_format()
        header_format_concorrente.set_bold()
        header_format_concorrente.set_border(1)
        header_format_concorrente.set_bg_color('#F4A460')
        header_format_concorrente.set_align('center')
        header_format_concorrente.set_align('vcenter')
        header_format_concorrente.set_text_wrap()
        
        header_format_action = workbook.add_format()
        header_format_action.set_bold()
        header_format_action.set_border(1)
        header_format_action.set_bg_color('#FF0000')
        header_format_action.set_align('center')
        header_format_action.set_align('vcenter')
        header_format_action.set_text_wrap()
        
        header_format_dominio = workbook.add_format()
        header_format_dominio.set_bold()
        header_format_dominio.set_border(1)
        header_format_dominio.set_bg_color('#1E90FF')
        header_format_dominio.set_align('center')
        header_format_dominio.set_align('vcenter')
        header_format_dominio.set_text_wrap()

        style_default = workbook.add_format()
        style_default.set_align('center')

        if(len(data1)>0):
            try:
                df1 = pd.DataFrame(data1)
                df1.columns = header1
                column_sort = header1[0]
                df1 = df1.sort_values(by=[column_sort])
                df1.to_excel(writer, sheet_name='Relacionado', startrow=1, header=False, index=False, na_rep='')

                worksheet = writer.sheets['Relacionado']
                worksheet.set_row(0, 80)
                worksheet.set_column('A:XFD', None, style_default)

                for col_num, value in enumerate(df1.columns.values):
                    if col_num < 7:
                        worksheet.write(0, col_num, value, header_format_concorrente)
                        column_len = df1[value].astype(str).str.len().max()
                        column_len = max(column_len, len(value)) + 3
                    elif col_num == 7:
                        worksheet.write(0, col_num, value, header_format_action)
                        column_len = 35
                    else:
                        worksheet.write(0, col_num, value, header_format_dominio)
                        column_len = df1[value].astype(str).str.len().max()
                        column_len = max(column_len, len(value)) + 3

                    worksheet.set_column(col_num, col_num, column_len)

            except Exception as e:
                print(f'Erro na aba "Relacionado": {str(e)}')
                pass
        
        if(len(data2)>0):
            try:
                df2 = pd.DataFrame(data2)
                df2.columns = header2
                column_sort = header2[0]
                df2 = df2.sort_values(by=[column_sort])
                df2.to_excel(writer, sheet_name='+ de 1 result.', index=False, na_rep='')

                worksheet = writer.sheets['+ de 1 result.']
                worksheet.set_row(0, 50)
                worksheet.set_column('A:XFD', None, style_default)

                for col_num, value in enumerate(df2.columns.values):
                    if col_num < 6:
                        worksheet.write(0, col_num, value, header_format_concorrente)
                        column_len = df2[value].astype(str).str.len().max()
                        column_len = max(column_len, len(value)) + 3
                    elif col_num == 6:
                        worksheet.write(0, col_num, value, header_format_action)
                        column_len = 35
                    else:
                        worksheet.write(0, col_num, value, header_format_dominio)
                        column_len = df2[value].astype(str).str.len().max()
                        column_len = max(column_len, len(value)) + 3

                    worksheet.set_column(col_num, col_num, column_len)
            except Exception as e:
                print(f'Erro na aba "+ de 1 result.": {str(e)}')
                pass
        
        if(len(data3)>0):
            try:
                df3 = pd.DataFrame(data3)
                df3.columns = header3
                column_sort = header3[0]
                df3 = df3.sort_values(by=[column_sort])
                df3.to_excel(writer, sheet_name='Sem result.', index=False, na_rep='')

                worksheet = writer.sheets['Sem result.']
                worksheet.set_row(0, 50)
                worksheet.set_column('A:XFD', None, style_default)

                for col_num, value in enumerate(df3.columns.values):
                    if col_num < 6:
                        worksheet.write(0, col_num, value, header_format_concorrente)
                        column_len = df3[value].astype(str).str.len().max()
                        column_len = max(column_len, len(value)) + 3
                    elif col_num == 6:
                        worksheet.write(0, col_num, value, header_format_action)
                        column_len = 35
                    else:
                        worksheet.write(0, col_num, value, header_format_dominio)
                        column_len = df3[value].astype(str).str.len().max()
                        column_len = max(column_len, len(value)) + 3

                    worksheet.set_column(col_num, col_num, column_len)
            except Exception as e:
                print(f'Erro na aba "Sem result.": {str(e)}')
                pass

        if(len(data4)>0):
            try:
                df4 = pd.DataFrame(data4)
                df4.columns = header4
                column_sort = header4[6]
                df4 = df4.sort_values(by=[column_sort])
                df4.to_excel(writer, sheet_name='Alerta', index=False, na_rep='')

                worksheet = writer.sheets['Alerta']
                worksheet.set_row(0, 110)
                worksheet.set_column('A:XFD', None, style_default)

                for col_num, value in enumerate(df4.columns.values):
                    if col_num < 7:
                        worksheet.write(0, col_num, value, header_format_concorrente)
                        column_len = df4[value].astype(str).str.len().max()
                        column_len = max(column_len, len(value)) + 3
                    elif col_num == 7:
                        worksheet.write(0, col_num, value, header_format_action)
                        column_len = 45
                    else:
                        worksheet.write(0, col_num, value, header_format_dominio)
                        column_len = df4[value].astype(str).str.len().max()
                        column_len = max(column_len, len(value)) + 3

                    worksheet.set_column(col_num, col_num, column_len)
            except Exception as e:
                print(f'Erro na aba "Alertas": {str(e)}')
                pass

        writer.close()

    def gerar_arquivos_saida(self, inscricao, codi_emp, relacao_empregados):
        """
        Gravar os arquivos de eventos, lançamentos e médias para importação.

        Retorna as rubricas que são de férias e que devem ser lançadas no cálculo
        de férias também.
        """
        sybase = Sybase(self.base_dominio, self.usuario_dominio, self.senha_dominio)
        connection = sybase.connect()

        rubrics_averages = sybase.select_rubrics_averages(connection, self.empresa_padrao_rubricas)
        uses_company_rubrics = sybase.select_companies_to_use_rubrics(connection)

        rubrics_relationship = StorageData()
        data_vacation = StorageData()
        general_rubrics_relationship, generate_rubrics, ignore_rubrics = read_rubric_relationship(f'{self.DIRETORIO_RAIZ}\\relacao_rubricas.xlsx')
        handle_lauch_rubrics = self.handle_lauch_rubrics()
        self.read_rescission_rubrics(handle_lauch_rubrics)

        rubrics_esocial = self.generate_rubricas_esocial(generate_rubrics)
        companies_rubrics = self.read_companies_rubrics(inscricao, codi_emp, handle_lauch_rubrics)
        rubrics_importation, rubrics_base_calc_importation, rubrics_formula = self.complete_data_rubrics(rubrics_esocial, companies_rubrics, rubrics_relationship, rubrics_averages)

        data_lancamentos_eventos = []
        data_lancto_medias = []

        # Completa o de/para de rúbricas de cada empresa, com os relacionamentos feitos na planilha
        load_rubrics_relatioship(companies_rubrics, rubrics_relationship, general_rubrics_relationship, uses_company_rubrics)

        # coletar datas de pagamento
        payment_data = self.load_date_payment()

        for line in handle_lauch_rubrics:
            cnpj_empregador = line.get('nrInsc')
            cpf_empregado = line.get('cpfTrab')
            i_empregados = relacao_empregados.get(codi_emp).get(cpf_empregado)

            if is_null(codi_emp) or is_null(i_empregados) or cnpj_empregador != inscricao:
                continue

            complete_competence = line.get('perApur')
            if len(complete_competence) == 4:
                # preenche o mês 12 e dia como 01
                complete_competence += '-12-01'
            else:
                # preenche o dia como 01
                complete_competence += '-01'

            competence = get_competence(complete_competence)

            codi_emp_eve = uses_company_rubrics.get(int(codi_emp))
            i_eventos = rubrics_relationship.get([str(codi_emp_eve), str(line.get('codRubr'))])
            valor_calculado = line.get('vrRubr')

            valor_informado = '1'
            if line.get('fatorRubr') is not None:
                valor_informado = line.get('fatorRubr')

            # Se estiver dentro da competência a ser calculada gera como lançamento
            # senão lança como média
            converted_init_competence = convert_date(self.INIT_COMPETENCE, '%d/%m/%Y')
            converted_end_competence = convert_date(self.END_COMPETENCE, '%d/%m/%Y')
            converted_competence = convert_date(complete_competence, '%Y-%m-%d')
            if converted_init_competence <= converted_competence <= converted_end_competence:

                # Separa o primeiro prefixo do campo, pois ele indica o tipo da folha
                dm_dev = str(line.get('ideDmDev')).replace('RESC', '').split('_')[0]

                # 11 é evento de folha mensal
                # 41 é evento de adiantamento
                # 51 é evento de adiantamento 13º
                # 52 é evento de 13º integral
                # 70 é evento de PLR
                # 42 é evento de folha complementar
                match dm_dev:
                    case 'FAD13':
                        tipo_processo = '51'
                    case 'F13':
                        tipo_processo = '52'
                    case 'FAD':
                        tipo_processo = '41'
                    case 'FER':
                        tipo_processo = '11'

                        # Para eventos de férias, precisamos guardar eles para serem
                        # lançados também ao calcular as férias do empregado
                        new_format_competence = transform_date(complete_competence, '%Y-%m-%d', '%d/%m/%Y')
                        data_vacation.add(valor_informado, [codi_emp, i_empregados, new_format_competence, i_eventos, 'VALOR_INFORMADO'])
                        data_vacation.add(valor_calculado, [codi_emp, i_empregados, new_format_competence, i_eventos, 'VALOR_CALCULADO'])
                    case _:
                        tipo_processo = '11'

                # se não encontrar a data de pagamento, vê o dia de pagamento da competência
                # anterior ou posterior
                data_pagto = payment_data.get([cnpj_empregador, cpf_empregado, competence])
                if is_null(data_pagto):
                    previus_competence = get_competence(add_month_to_date(complete_competence, -1, '%Y-%m-%d'))
                    next_competence = get_competence(add_month_to_date(complete_competence, 1, '%Y-%m-%d'))

                    if payment_data.exist([cnpj_empregador, cpf_empregado, previus_competence]):
                        previus_data_pagto = payment_data.get([cnpj_empregador, cpf_empregado, previus_competence])
                        data_pagto = add_month_to_date(previus_data_pagto, 1, '%Y-%m-%d')

                    if is_null(data_pagto):
                        if payment_data.exist([cnpj_empregador, cpf_empregado, next_competence]):
                            next_data_pagto = payment_data.get([cnpj_empregador, cpf_empregado, next_competence])
                            data_pagto = add_month_to_date(next_data_pagto, -1, '%Y-%m-%d')

                if is_null(data_pagto):
                    continue

                if is_null(i_eventos):
                    continue

                table = Table('FOLANCAMENTOS_EVENTOS')
                table.set_value('CODI_EMP', codi_emp)
                table.set_value('I_EMPREGADOS', i_empregados)
                table.set_value('TIPO_PROCESSO', tipo_processo)
                table.set_value('COMPETENCIA_INICIAL', transform_date(complete_competence, '%Y-%m-%d', '%d/%m/%Y'))
                table.set_value('DATA_PAGAMENTO_ALTERA_CALCULO', transform_date(data_pagto, '%Y-%m-%d', '%d/%m/%Y'))
                table.set_value('I_EVENTOS', i_eventos)
                table.set_value('VALOR_INFORMADO', valor_informado)
                table.set_value('VALOR_CALCULADO', valor_calculado)
                table.set_value('ORIGEM_REGISTRO', '3')

                data_lancamentos_eventos.append(table.do_output())
            else:
                # eventos que entrarão para médias
                if str(i_eventos) in rubrics_averages:
                    table = Table('FOLANCTOMEDIAS')
                    table.set_value('CODI_EMP', codi_emp)
                    table.set_value('I_EMPREGADOS', i_empregados)
                    table.set_value('COMPETENCIA', transform_date(complete_competence, '%Y-%m-%d', '%d/%m/%Y'))
                    table.set_value('I_EVENTOS', i_eventos)
                    table.set_value('VALOR', valor_calculado)

                    data_lancto_medias.append(table.do_output())

        print_to_import(f'{self.DIRETORIO_IMPORTAR}\\FOEVENTOS.txt', rubrics_importation)
        print_to_import(f'{self.DIRETORIO_IMPORTAR}\\FOEVENTOSBASES.txt', rubrics_base_calc_importation)
        print_to_import(f'{self.DIRETORIO_IMPORTAR}\\FOFORMULAS.txt', rubrics_formula)
        print_to_import(f'{self.DIRETORIO_IMPORTAR}\\FOLANCAMENTOS_EVENTOS.txt', data_lancamentos_eventos)
        print_to_import(f'{self.DIRETORIO_IMPORTAR}\\FOLANCTO_MEDIAS.txt', data_lancto_medias)
        return data_vacation

    def save_rescission(self, inscricao, codi_emp, relacao_empregados):
        """
        Salvar dados de rescisão que o RPA irá calcular
        """
        # apagar dados já salvos
        table = DominioRescisao()
        table.connect(self.BANCO_SQLITE)
        table.delete().execute()

        # Carregar dados de aviso prévio
        data_rescission = StorageData()
        for s2299 in self.dicionario_s2299:
            cnpj_empregador = self.dicionario_s2299[s2299].get("ideEmpregador").get("nrInsc")
            cpf_empregado = self.dicionario_s2299[s2299].get("ideVinculo").get("cpfTrab")
            i_empregados = relacao_empregados.get(codi_emp).get(cpf_empregado)

            if cnpj_empregador != inscricao:
                continue

            infos = self.dicionario_s2299[s2299].get('infoDeslig')
            aviso_previo = infos.get('indPagtoAPI')
            data_fim_aviso = infos.get('dtProjFimAPI')
            motivo_desligamento = infos.get('mtvDeslig')

            data_rescission.add(aviso_previo, [codi_emp, i_empregados, 'AVISO_PREVIO'])
            data_rescission.add(data_fim_aviso, [codi_emp, i_empregados, 'DATA_FIM_AVISO'])
            data_rescission.add(motivo_desligamento, [codi_emp, i_empregados, 'MOTIVO_DESLIGAMENTO'])
            data_rescission.add('empregado', [codi_emp, i_empregados, 'TIPO'])

        # Carregar contribuintes
        for s2399 in self.dicionario_s2399:
            cnpj_empregador = self.dicionario_s2399[s2399].get("ideEmpregador").get("nrInsc")
            cpf_empregado = self.dicionario_s2399[s2399].get("ideTrabSemVinculo").get("cpfTrab")
            i_empregados = relacao_empregados.get(codi_emp).get(cpf_empregado)

            if cnpj_empregador != inscricao:
                continue

            data_rescission.add('contribuinte', [codi_emp, i_empregados, 'TIPO'])

        data = Table('FOAFASTAMENTOS_IMPORTACAO', file=f'{self.DIRETORIO_IMPORTAR}\\FOAFASTAMENTOS_IMPORTACAO.txt')
        for line in data.items():
            if format_int(line.get_value('I_AFASTAMENTOS')) == 8:
                codi_emp = line.get_value('CODI_EMP')
                i_empregados = line.get_value('I_EMPREGADOS')

                new_line = DominioRescisao()
                new_line.connect(self.BANCO_SQLITE)

                aviso_previo = data_rescission.get([codi_emp, i_empregados, 'AVISO_PREVIO'])
                tipo = data_rescission.get([codi_emp, i_empregados, 'TIPO'])

                if tipo == 'empregado':
                    motivo_desligamento = data_rescission.get([codi_emp, i_empregados, 'MOTIVO_DESLIGAMENTO'])
                else:
                    # contribuintes vão por padrão no Domínio com motivo 99 - Outros
                    motivo_desligamento = '99'

                new_line.codi_emp = codi_emp
                new_line.i_empregados = i_empregados
                new_line.competencia = replace_day_date(line.get_value('DATA_REAL'), '%d/%m/%Y', 1)
                new_line.data_demissao = line.get_value('DATA_REAL')
                new_line.motivo = motivos_desligamento_esocial.get(motivo_desligamento)
                new_line.data_pagamento = ''

                if aviso_previo == 'S':
                    data_fim_aviso = data_rescission.get([codi_emp, i_empregados, 'DATA_FIM_AVISO'])
                    formated_data_fim_aviso = transform_date(data_fim_aviso, '%Y-%m-%d', '%d/%m/%Y')
                    dias_projecao_aviso = difference_between_dates(line.get_value('DATA_REAL'), formated_data_fim_aviso, '%d/%m/%Y')

                    new_line.aviso_previo = True
                    new_line.data_aviso = line.get_value('DATA_REAL')
                    new_line.dias_projecao_aviso = dias_projecao_aviso+1
                else:
                    new_line.aviso_previo = False
                    new_line.data_aviso = ''
                    new_line.dias_projecao_aviso = ''

                if not is_null(new_line.motivo):
                    new_line.save()

    def save_vacation(self, data_vacation):
        """
        Salvar dados de férias que o RPA irá calcular
        """
        # apagar dados já salvos
        table = DominioFerias()
        table.connect(self.BANCO_SQLITE)
        table.delete().execute()

        data = Table('FOFERIAS_GOZO', file=f'{self.DIRETORIO_IMPORTAR}\\FOFERIAS_GOZO.txt')
        for line in data.items():
            codi_emp = str(line.get_value('CODI_EMP'))
            i_empregados = str(line.get_value('I_EMPREGADOS'))
            competencia = replace_day_date(line.get_value('GOZO_INICIO'), '%d/%m/%Y', 1)

            # Se não encontra nenhum lançamento na competência atual, diminui dois
            # dias(prazo que as férias devem ser pagas) e tenta pesquisar novamente,
            # pois o pagamento pode ter sido feito na competência anterior
            data_rubric = data_vacation.get([codi_emp, i_empregados, competencia])
            if not data_rubric:
                data_pagto = add_day_to_date(line.get_value('GOZO_INICIO'), '%d/%m/%Y', -2)
                previus_competence = replace_day_date(data_pagto, '%d/%m/%Y', 1)
                data_rubric = data_vacation.get([codi_emp, i_empregados, previus_competence])

            for rubric in data_rubric:
                new_line = DominioFerias()
                new_line.connect(self.BANCO_SQLITE)

                new_line.codi_emp = codi_emp
                new_line.i_empregados = i_empregados
                new_line.competencia = competencia
                new_line.inicio_aquisitivo = line.get_value('INICIO_AQUISITIVO')
                new_line.fim_aquisitivo = line.get_value('FIM_AQUISITIVO')
                new_line.inicio_gozo = line.get_value('GOZO_INICIO')
                new_line.fim_gozo = line.get_value('GOZO_FIM')
                new_line.abono_paga = line.get_value('ABONO_PAGA')
                new_line.inicio_abono = line.get_value('ABONO_INICIO')
                new_line.fim_abono = line.get_value('ABONO_FIM')
                new_line.data_pagamento = line.get_value('DATA_PAGTO')
                new_line.rubrica = rubric
                new_line.valor_informado = data_rubric.get(rubric).get('VALOR_INFORMADO')
                new_line.valor_calculado = data_rubric.get(rubric).get('VALOR_CALCULADO')

                if not is_null(new_line.inicio_gozo):
                    new_line.save()

    def gerar_afastamentos_importacao(self, inscricao, codi_emp, relacao_empregados):
        """
        Gera o arquivo FOAFASTAMENTOS_IMPORTACAO
        """
        data_foafastamentos_importacao = []
        data_afastamentos_xml_incompleto = StorageData()
        data_afastamentos_xml = StorageData()
        check_demissao = StorageData()

        # Podem vir afastamentos onde a data de início está em um XML e a
        # data fim em outro, dessa forma precisamos organizar os dados e encontrar
        # os respectivos inicio e fim
        for s2230 in self.dicionario_s2230:
            cnpj_empregador = self.dicionario_s2230[s2230].get('ideEmpregador').get('nrInsc')
            cpf_empregado = self.dicionario_s2230[s2230].get('ideVinculo').get('cpfTrab')

            if cnpj_empregador != inscricao:
                continue

            data_inicio = ''
            data_fim = ''

            infos_afastamento = self.dicionario_s2230[s2230].get('infoAfastamento')
            if infos_afastamento.get('iniAfastamento') is not None:
                if infos_afastamento.get('iniAfastamento').get('dtIniAfast') is not None:
                    data_inicio = infos_afastamento.get('iniAfastamento').get('dtIniAfast')

            if infos_afastamento.get('fimAfastamento') is not None:
                if infos_afastamento.get('fimAfastamento').get('dtTermAfast') is not None:
                    data_fim = infos_afastamento.get('fimAfastamento').get('dtTermAfast')

            if not is_null(data_inicio) and not is_null(data_fim):
                data_afastamentos_xml.add(infos_afastamento, [cnpj_empregador, cpf_empregado, data_inicio])
            if is_null(data_fim):
                data_afastamentos_xml_incompleto.add(infos_afastamento, [cnpj_empregador, cpf_empregado, 'INICIO', data_inicio])
            if is_null(data_inicio):
                data_afastamentos_xml_incompleto.add(infos_afastamento, [cnpj_empregador, cpf_empregado, 'FIM', data_fim])

        # Para cada afastamento sem data fim, pega o primeiro fim que for posterior ao início
        for cnpj_empregador in data_afastamentos_xml_incompleto.get_all_dict():
            for cpf_empregado in data_afastamentos_xml_incompleto.get([cnpj_empregador]):

                # ordendar datas de início
                datas_inicio_ordenadas = []
                for data_inicio in data_afastamentos_xml_incompleto.get([cnpj_empregador, cpf_empregado, 'INICIO']):
                    datas_inicio_ordenadas.append(convert_date(data_inicio, '%Y-%m-%d'))
                datas_inicio_ordenadas.sort()

                # ordenar datas fim
                datas_fim_ordenadas = []
                for data_fim in data_afastamentos_xml_incompleto.get([cnpj_empregador, cpf_empregado, 'FIM']):
                    datas_fim_ordenadas.append(convert_date(data_fim, '%Y-%m-%d'))

                datas_fim_ordenadas.sort()

                # Tenta encontrar a data fim para o afastamento
                for data_inicio_formatada in datas_inicio_ordenadas:
                    data_inicio_string = data_inicio_formatada.strftime('%Y-%m-%d')
                    infos_afastamento = data_afastamentos_xml_incompleto.get([cnpj_empregador, cpf_empregado, 'INICIO', data_inicio_string])

                    end_date_found = False
                    for data_fim_formatada in datas_fim_ordenadas:
                        data_fim_string = data_fim_formatada.strftime('%Y-%m-%d')
                        if data_inicio_formatada < data_fim_formatada:
                            infos_fim = data_afastamentos_xml_incompleto.get([cnpj_empregador, cpf_empregado, 'FIM', data_fim_string])

                            if not is_null(infos_fim):
                                infos_afastamento.update(infos_fim)
                                data_afastamentos_xml.add(infos_afastamento, [cnpj_empregador, cpf_empregado, data_inicio_string])
                                data_afastamentos_xml_incompleto.overwrite('', [cnpj_empregador, cpf_empregado, 'FIM', data_fim_string])
                                end_date_found = True
                                break

                    if not end_date_found:
                        data_afastamentos_xml.add(infos_afastamento, [cnpj_empregador, cpf_empregado, data_inicio_string])

        # afastamentos temporários
        for cnpj_empregador in data_afastamentos_xml.get_all_dict():
            for cpf_empregado in data_afastamentos_xml.get([cnpj_empregador]):
                for data_inicio in data_afastamentos_xml.get([cnpj_empregador, cpf_empregado]):
                    infos_afastamento = data_afastamentos_xml.get([cnpj_empregador, cpf_empregado, data_inicio])
                    i_empregados = relacao_empregados.get(codi_emp).get(cpf_empregado)

                    if is_null(codi_emp) or is_null(i_empregados):
                        continue

                    data_fim = ''
                    if infos_afastamento.get('fimAfastamento') is not None:
                        data_fim = infos_afastamento.get('fimAfastamento').get('dtTermAfast')

                    cod_motivo_esocial = infos_afastamento.get('iniAfastamento').get('codMotAfast')
                    motivo = motivos_afastamentos_esocial.get(cod_motivo_esocial)

                    if is_null(motivo):
                        continue

                    # afastamento por doença ou acidente de trabalho tem o mesmo código no eSocial
                    # e no Domínio depende da quantidade de dias
                    if motivo in ['03', '06']:
                        if is_null(data_fim):
                            data_fim = get_current_day()

                    if difference_between_dates(data_inicio, data_fim, '%Y-%m-%d') <= 15:
                        if motivo == '03':
                            motivo = '17'
                        elif motivo == '06':
                            motivo = '18'

                    table = Table('FOAFASTAMENTOS_IMPORTACAO')

                    table.set_value('CODI_EMP', codi_emp)
                    table.set_value('I_EMPREGADOS', i_empregados)
                    table.set_value('I_AFASTAMENTOS', motivo)
                    table.set_value('DATA_REAL', transform_date(data_inicio, '%Y-%m-%d', '%d/%m/%Y'))
                    table.set_value('DATA_FIM', transform_date(data_fim, '%Y-%m-%d', '%d/%m/%Y', default_value_error='NULO'))
                    data_foafastamentos_importacao.append(table.do_output())

        # demissões empregados
        for s2299 in self.dicionario_s2299:
            cnpj_empregador = self.dicionario_s2299[s2299].get("ideEmpregador").get("nrInsc")
            cpf_empregado = self.dicionario_s2299[s2299].get("ideVinculo").get("cpfTrab")
            i_empregados = relacao_empregados.get(codi_emp).get(cpf_empregado)

            if is_null(codi_emp) or is_null(i_empregados):
                continue

            data_desligamento = self.dicionario_s2299[s2299].get("infoDeslig").get("dtDeslig")
            data_real_demissao = add_day_to_date(data_desligamento, '%Y-%m-%d', 1)
            if not check_demissao.exist([codi_emp, i_empregados]):
                table = Table('FOAFASTAMENTOS_IMPORTACAO')

                table.set_value('CODI_EMP', codi_emp)
                table.set_value('I_EMPREGADOS', i_empregados)
                table.set_value('I_AFASTAMENTOS', 8)
                table.set_value('DATA_REAL', data_real_demissao)
                data_foafastamentos_importacao.append(table.do_output())
                check_demissao.add('True', [codi_emp, i_empregados])

        # demissões contribuintes
        for s2399 in self.dicionario_s2399:
            cnpj_empregador = self.dicionario_s2399[s2399].get("ideEmpregador").get("nrInsc")
            cpf_empregado = self.dicionario_s2399[s2399].get("ideTrabSemVinculo").get("cpfTrab")
            i_empregados = relacao_empregados.get(codi_emp).get(cpf_empregado)

            if is_null(codi_emp) or is_null(i_empregados):
                continue

            data_demissao = self.dicionario_s2399[s2399].get("infoTSVTermino").get("dtTerm")

            if not check_demissao.exist([codi_emp, i_empregados]):
                table = Table('FOAFASTAMENTOS_IMPORTACAO')

                table.set_value('CODI_EMP', codi_emp)
                table.set_value('I_EMPREGADOS', i_empregados)
                table.set_value('I_AFASTAMENTOS', 8)
                table.set_value('DATA_REAL', transform_date(data_demissao, '%Y-%m-%d', '%d/%m/%Y'))
                data_foafastamentos_importacao.append(table.do_output())
                check_demissao.add('True', [codi_emp, i_empregados])

        print_to_import(f'{self.DIRETORIO_IMPORTAR}\\FOAFASTAMENTOS_IMPORTACAO.txt', data_foafastamentos_importacao)

    def gerar_ferias_importacao(self, inscricao, codi_emp, relacao_empregados):
        """
        Gera os arquivos FOFERIAS_AQUISITIVOS e FOFERIAS_GOZO
        """
        data_foferias_aquisitivos = []
        data_foferias_gozo = []

        sequencial_aquisitivos = Sequencial()
        sequencial_gozos = Sequencial()
        check_aquisitivos = StorageData()

        payment_data = self.load_date_payment()

        for s2230 in self.dicionario_s2230:
            insc_empresa = self.dicionario_s2230[s2230].get('ideEmpregador').get('nrInsc')
            cpf_empregado = self.dicionario_s2230[s2230].get('ideVinculo').get('cpfTrab')

            if insc_empresa != inscricao:
                continue

            infos_afastamento = self.dicionario_s2230[s2230].get("infoAfastamento")
            motivo = infos_afastamento.get('iniAfastamento').get("codMotAfast")

            # Afastamentos de férias é código 15 no eSocial
            if motivo != '15': continue

            i_empregados = relacao_empregados.get(codi_emp).get(cpf_empregado)

            if is_null(codi_emp) or is_null(i_empregados):
                continue

            data_inicio_aquisitivo = ''
            data_fim_aquisitivo = ''
            if infos_afastamento.get('iniAfastamento').get('perAquis') is not None:
                data_inicio_aquisitivo = infos_afastamento.get('iniAfastamento').get('perAquis').get('dtInicio')
                data_fim_aquisitivo = infos_afastamento.get('iniAfastamento').get('perAquis').get('dtFim')

            # ignora se não houver inicio e fim do aquisitivo
            if is_null(data_inicio_aquisitivo) or is_null(data_fim_aquisitivo): continue

            limite_para_gozo = add_year_to_date(data_inicio_aquisitivo, 2, '%Y-%m-%d')

            if not check_aquisitivos.exist([codi_emp, i_empregados, data_inicio_aquisitivo]):
                i_ferias_aquisitivos = sequencial_aquisitivos.add([codi_emp, i_empregados])

                table = Table('FOFERIAS_AQUISITIVOS')
                table.set_value('CODI_EMP', codi_emp)
                table.set_value('I_EMPREGADOS', i_empregados)
                table.set_value('I_FERIAS_AQUISITIVOS', i_ferias_aquisitivos)
                table.set_value('DATA_INICIO', transform_date(data_inicio_aquisitivo, '%Y-%m-%d', '%d/%m/%Y'))
                table.set_value('DATA_FIM', transform_date(data_fim_aquisitivo, '%Y-%m-%d', '%d/%m/%Y'))
                table.set_value('SITUACAO', 1)
                table.set_value('AFAST_PREVIDENCIA', 0)
                table.set_value('AFAST_SEM_REMUNERACAO', 0)
                table.set_value('AFAST_COM_REMUNERACAO', 0)
                table.set_value('DIAS_FALTAS', 0)
                table.set_value('DIAS_DIREITO', 30)
                table.set_value('DIAS_GOZADOS', 0)
                table.set_value('DIAS_ABONO', 0)
                table.set_value('AVOS_ADQUIRIDOS', 12)
                table.set_value('LIMITE_PARA_GOZO', limite_para_gozo)

                data_foferias_aquisitivos.append(table.do_output())
                check_aquisitivos.add(i_ferias_aquisitivos, [codi_emp, i_empregados, data_inicio_aquisitivo])

            data_inicio_gozo = ''
            data_fim_gozo = ''
            if infos_afastamento.get('iniAfastamento') is not None:
                data_inicio_gozo = infos_afastamento.get('iniAfastamento').get('dtIniAfast')

            if infos_afastamento.get('fimAfastamento') is not None:
                data_fim_gozo = infos_afastamento.get('fimAfastamento').get('dtTermAfast')

            # ignora se não houver inicio e fim do aquisitivo
            if is_null(data_inicio_gozo) or is_null(data_fim_gozo): continue

            competencia = get_competence(data_inicio_gozo)
            i_ferias_gozo = sequencial_gozos.add([codi_emp, i_empregados])
            i_ferias_aquisitivos = check_aquisitivos.get([codi_emp, i_empregados, data_inicio_aquisitivo])

            # Falta encontrar no XML as datas de abono
            abono_inicio = ''
            abono_fim = ''
            data_pagamento = payment_data.get([insc_empresa, cpf_empregado, competencia])

            abono_paga = 'N'
            if not is_null(abono_inicio) and not is_null(abono_fim):
                abono_paga = 'S'

            # campos decimais
            gozo_inicio_dn = f"{difference_between_dates('1900-01-01', data_inicio_gozo, '%Y-%m-%d')}.00"
            gozo_fim_dn = f"{difference_between_dates('1900-01-01', data_fim_gozo, '%Y-%m-%d')}.99"

            abono_inicio_dn = '0.00'
            abono_fim_dn = '0.00'
            if abono_paga == 'S':
                abono_inicio_dn = f"{difference_between_dates('1900-01-01', abono_inicio, '%Y-%m-%d')}.00"
                abono_fim_dn = difference_between_dates(abono_fim, '1900-01-01', '%Y-%m-%d')

            table = Table('FOFERIAS_GOZO')
            table.set_value('CODI_EMP', codi_emp)
            table.set_value('I_EMPREGADOS', i_empregados)
            table.set_value('I_FERIAS_GOZO', i_ferias_gozo)
            table.set_value('I_FERIAS_AQUISITIVOS', i_ferias_aquisitivos)
            table.set_value('GOZO_INICIO', transform_date(data_inicio_gozo, '%Y-%m-%d', '%d/%m/%Y'))
            table.set_value('GOZO_FIM', transform_date(data_fim_gozo, '%Y-%m-%d', '%d/%m/%Y'))
            table.set_value('ABONO_PAGA', abono_paga)
            table.set_value('ABONO_INICIO', abono_inicio)
            table.set_value('ABONO_FIM', abono_fim)
            table.set_value('DATA_PAGTO', transform_date(data_pagamento, '%Y-%m-%d', '%d/%m/%Y'))
            table.set_value('PAGA_AD13', '')
            table.set_value('TIPO', '1')
            table.set_value('GOZO_INICIO_DN', gozo_inicio_dn)
            table.set_value('GOZO_FIM_DN', gozo_fim_dn)
            table.set_value('ABONO_INICIO_DN', abono_inicio_dn)
            table.set_value('ABONO_FIM_DN', abono_fim_dn)
            table.set_value('INICIO_AQUISITIVO', transform_date(data_inicio_aquisitivo, '%Y-%m-%d', '%d/%m/%Y'))
            table.set_value('FIM_AQUISITIVO', transform_date(data_fim_aquisitivo, '%Y-%m-%d', '%d/%m/%Y'))

            data_foferias_gozo.append(table.do_output())

        print_to_import(f'{self.DIRETORIO_IMPORTAR}\\FOFERIAS_AQUISITIVOS.txt', data_foferias_aquisitivos)
        print_to_import(f'{self.DIRETORIO_IMPORTAR}\\FOFERIAS_GOZO.txt', data_foferias_gozo)

    def load_date_payment(self):
        """
        Carrega as datas de pagamento do evento 1210
        """
        payment_data = StorageData()
        for s1210 in self.dicionario_s1210:
            insc_empresa = self.dicionario_s1210[s1210].get('ideEmpregador').get('nrInsc')
            cpf_empregado = self.dicionario_s1210[s1210].get('ideBenef').get('cpfBenef')

            competence = self.dicionario_s1210[s1210].get('ideEvento').get('perApur')
            infos_pagto = self.dicionario_s1210[s1210].get('ideBenef').get('infoPgto')

            # as vezes as informações de pagamento vem em um unico objeto, e
            # outras vem em uma lista de objetos
            if isinstance(infos_pagto, dict):
                data_pagto = infos_pagto.get('dtPgto')
            elif isinstance(infos_pagto, list):
                data_pagto = ''

                # percorre a lista de infos sobre o pagamento e coleta a data
                # de pagamento daquela que for referente a mesma competência
                for item in infos_pagto:
                    if item.get('detPgtoFl') is not None:
                        ref_competence = item.get('detPgtoFl').get('perRef')
                    else:
                        ref_competence = item.get('perRef')

                    if competence == ref_competence:
                        data_pagto = item.get('dtPgto')

                # as vezes em vez da competência vem somente o ano do pagamento
                # dessa forma coletamos também quando o ano for igual ao da competência
                if is_null(data_pagto):
                    for item in infos_pagto:
                        if item.get('detPgtoFl') is not None:
                            ref_competence = item.get('detPgtoFl').get('perRef')
                        else:
                            ref_competence = item.get('perRef')

                        if not is_null(ref_competence) and len(ref_competence) == 4:
                            if get_year(competence) == get_year(ref_competence):
                                data_pagto = item.get('dtPgto')
                        elif competence == ref_competence:
                            data_pagto = item.get('dtPgto')
            else:
                data_pagto = ''

            payment_data.add(data_pagto, [insc_empresa, cpf_empregado, competence])

        return payment_data

    def generate_rubricas_esocial(self, generate_rubrics):
        """
        Alimenta o cadastro da rúbrica com os campos que vem do eSocial
        """
        rubrics_importation = []
        for rubric in generate_rubrics:

            i_eventos = int(rubric.get('codigo'))
            descricao = rubric.get('descricao')
            tipo = rubric.get('tipo')
            natureza_tributaria_rubrica = rubric.get('natureza_tributaria_rubrica')
            incidencia_inss = rubric.get('incidencia_inss_esocial')
            incidencia_irrf = rubric.get('incidencia_irrf_esocial')
            incidencia_fgts = rubric.get('incidencia_fgts_esocial')
            incidencia_sindicato = rubric.get('incidencia_sindical_esocial')

            table = Table('FOEVENTOS')
            table.set_value('I_EVENTOS', i_eventos)
            table.set_value('NOME', descricao)
            table.set_value('PROV_DESC', tipo)
            table.set_value('NATUREZA_FOLHA_MENSAL', natureza_tributaria_rubrica)
            table.set_value('CODIGO_INCIDENCIA_INSS_ESOCIAL', incidencia_inss)
            table.set_value('CODIGO_INCIDENCIA_IRRF_ESOCIAL', incidencia_irrf)
            table.set_value('CODIGO_INCIDENCIA_FGTS_ESOCIAL', incidencia_fgts)
            table.set_value('CODIGO_INCIDENCIA_SINDICAL_ESOCIAL', incidencia_sindicato)

            rubrics_importation.append(table.do_output())

        return rubrics_importation

    def read_companies_rubrics(self, inscricao, codi_emp, handle_lauch_rubrics):
        """
        Retorna um dicionário de quais empresas utilizam determinada rúbrica
        """
        companies_rubrics = {}

        for line in handle_lauch_rubrics:
            cnpj_empregador = line.get('nrInsc')
            i_eventos = int(line.get('codRubr'))

            if cnpj_empregador != inscricao:
                continue

            # adiciona a rubrica na lista de rubricas utilizadas pela empresa
            if i_eventos not in companies_rubrics.keys():
                companies_rubrics[i_eventos] = []

            if int(codi_emp) not in companies_rubrics[i_eventos]:
                companies_rubrics[i_eventos].append(int(codi_emp))

        return companies_rubrics

    def handle_lauch_rubrics(self):
        """
        Faz um tratamento inicial nos dados dos eventos S-1200 para deixá-los todos no mesmo padrão
        """
        new_data = []
        for s1200 in self.dicionario_s1200:
            infos_pagto = self.dicionario_s1200[s1200].get('dmDev')
            itens_to_handle = []
            if isinstance(infos_pagto, list):
                itens_to_handle.extend(infos_pagto)
            else:
                itens_to_handle.append(infos_pagto)

            for item in itens_to_handle:
                dm_dev = item.get('ideDmDev')
                infos_events = item.get('infoPerApur').get('ideEstabLot').get('remunPerApur').get('itensRemun')

                events_to_handle = []
                if isinstance(infos_events, list):
                    events_to_handle.extend(infos_events)
                else:
                    events_to_handle.append(infos_events)

                for line in events_to_handle:
                    new_line = dict()
                    new_line['nrInsc'] = self.dicionario_s1200[s1200].get('ideEmpregador').get('nrInsc')
                    new_line['cpfTrab'] = self.dicionario_s1200[s1200].get('ideTrabalhador').get('cpfTrab')
                    new_line['perApur'] = self.dicionario_s1200[s1200].get('ideEvento').get('perApur')
                    new_line['ideDmDev'] = dm_dev
                    new_line['codRubr'] = line.get('codRubr')
                    new_line['fatorRubr'] = line.get('fatorRubr')
                    new_line['vrRubr'] = line.get('vrRubr')

                    new_data.append(new_line)

        return new_data

    def read_rescission_rubrics(self, handle_lauch_rubrics):
        """
        Em alguns eventos S-2299 vem informadas algumas verbas rescisórias, então juntamos essas verbas
        na lista de lançamentos que precisam ser feitos
        """
        for s2299 in self.dicionario_s2299:
            infos_pagto = self.dicionario_s2299[s2299].get('infoDeslig').get('verbasResc')

            if infos_pagto is not None:

                items_to_handle = []
                if isinstance(infos_pagto.get('dmDev'), list):
                    items_to_handle.extend(infos_pagto.get('dmDev'))
                else:
                    items_to_handle.append(infos_pagto.get('dmDev'))

                for item in items_to_handle:
                    dm_dev = item.get('ideDmDev')

                    infos_events = item.get('infoPerApur').get('ideEstabLot').get('detVerbas')

                    events_to_handle = []
                    if isinstance(infos_events, list):
                        events_to_handle.extend(infos_events)
                    else:
                        events_to_handle.append(infos_events)

                    for line in events_to_handle:
                        new_line = dict()
                        new_line['nrInsc'] = self.dicionario_s2299[s2299].get('ideEmpregador').get('nrInsc')
                        new_line['cpfTrab'] = self.dicionario_s2299[s2299].get('ideVinculo').get('cpfTrab')
                        new_line['perApur'] = get_competence(self.dicionario_s2299[s2299].get('infoDeslig').get('dtDeslig'))
                        new_line['ideDmDev'] = dm_dev
                        new_line['codRubr'] = line.get('codRubr')
                        new_line['fatorRubr'] = line.get('qtdRubr')
                        new_line['vrRubr'] = line.get('vrRubr')

                        handle_lauch_rubrics.append(new_line)

    def complete_data_rubrics(self, rubrics_esocial, companies_rubrics, rubrics_relationship, rubrics_averages):
        """
        Complementa a tabela de rúbricas com alguma equivalente do contábil, e gera também as bases de cálculo
        e fórmulas necessárias
        """
        # campos que virão dos dados do eSocial
        not_overwrite_keys = [
            'NOME',
            'PROV_DESC',
            'NATUREZA_FOLHA_MENSAL',
            'CODIGO_INCIDENCIA_INSS_ESOCIAL',
            'CODIGO_INCIDENCIA_IRRF_ESOCIAL',
            'CODIGO_INCIDENCIA_FGTS_ESOCIAL',
            'CODIGO_INCIDENCIA_SINDICAL_ESOCIAL'
        ]
        sybase = Sybase(self.base_dominio, self.usuario_dominio, self.senha_dominio)
        connection = sybase.connect()

        data_rubrics, data_base_calc_rubrics, data_formula_rubrics = sybase.select_data_rubrics(connection, self.empresa_padrao_rubricas)
        uses_company_rubrics = sybase.select_companies_to_use_rubrics(connection)
        dominio_rubrics = sybase.select_rubrics(connection)
        dominio_rubrics_esocial = sybase.select_codigo_esocial_rubrics(connection)
        cnpj_companies = sybase.select_cnpj_companies(connection)

        rubrics_importation = []
        rubrics_base_calc_importation = []
        rubrics_formula = []
        check_importated_rubrics = StorageData()
        for line_rubric in rubrics_esocial:
            i_eventos = line_rubric.get('I_EVENTOS')
            if i_eventos in companies_rubrics.keys():
                for codi_emp in companies_rubrics.get(i_eventos):
                    table = Table('FOEVENTOS')

                    rubric_calc_base = {}
                    rubric_formula = {}

                    natureza_folha_mensal = line_rubric.get('NATUREZA_FOLHA_MENSAL')
                    if natureza_folha_mensal in data_rubrics.keys():

                        natureza_folha_mensal_dominio, index_rubric = self.search_similar_rubric(line_rubric, data_rubrics)
                        if index_rubric:

                            # copiar campos da rubrica do Domínio
                            for column in data_rubrics[natureza_folha_mensal_dominio][index_rubric]:
                                column_value = data_rubrics[natureza_folha_mensal_dominio][index_rubric][column]
                                if not is_null(column_value) and str(column_value) != 'None':
                                    table.set_value(column, column_value)

                            # Copiar base de cálculo e fórmula se tiver
                            if table.get_value('I_EVENTOS') in data_base_calc_rubrics.keys():
                                rubric_calc_base = data_base_calc_rubrics[table.get_value('I_EVENTOS')]

                            if table.get_value('I_EVENTOS') in data_formula_rubrics.keys():
                                rubric_formula = data_formula_rubrics[table.get_value('I_EVENTOS')]

                    # copiar campos que vem dos dados do eSocial
                    for field in not_overwrite_keys:
                        table.set_value(field, line_rubric.get(field))

                    # Algumas empresas podem replicar rubricas de outras, aqui buscamos o código da empresa
                    # onde a rubrica deve ser importada
                    codi_emp_eve = uses_company_rubrics.get(codi_emp)

                    # checa se rubrica já não foi criada na empresa
                    if not check_importated_rubrics.exist([codi_emp_eve, i_eventos]):
                        check_importated_rubrics.add('True', [codi_emp_eve, i_eventos])

                        table.set_value('CODI_EMP', codi_emp_eve)
                        table.set_value('NOME', format_name_rubric(line_rubric.get('NOME')))

                        i_eventos_importation, codigo_esocial = self.generate_i_evento(codi_emp_eve, dominio_rubrics, dominio_rubrics_esocial, cnpj_companies)
                        table.set_value('I_EVENTOS', i_eventos_importation)
                        table.set_value('CODIGO_ESOCIAL', codigo_esocial)

                        # salva o relacionamento da rúbrica
                        rubrics_relationship.add(i_eventos_importation, [str(codi_emp_eve), str(i_eventos)])

                        # se tiver incidência no IRRF, marca a rubrica para compor a DIRF
                        if format_int(table.get_value('CODIGO_INCIDENCIA_IRRF_ESOCIAL')) in [11, 12, 13]:
                            table.set_value('SOMA_INF_REN', 'S')
                            table.set_value('REND_TRIBUTAVEIS', '1')
                        else:
                            table.set_value('SOMA_INF_REN', 'N')
                            table.set_value('REND_TRIBUTAVEIS', '0')

                        rubrics_importation.append(table.do_output())

                        # checa se a rubrica deve entrar para médias
                        if str(table.get_value('SOMA_MEDIA_AVISO_PREVIO')) == '1':
                            if str(table.get_value('SOMA_MED_13')) == 'S':
                                if str(table.get_value('SOMA_MED_FER')) == 'S':
                                    if str(table.get_value('SOMA_MEDIA_LICENCA_PREMIO')) == '1':
                                        if str(table.get_value('SOMA_MED_AFAST')) == 'S':
                                            if str(table.get_value('SOMA_MEDIA_SALDO_SALARIO')) == '1':
                                                if str(table.get_value('I_EVENTOS')) not in rubrics_averages:
                                                    rubrics_averages.append(str(table.get_value('I_EVENTOS')))

                        # para os tipos de rubricas que possuem formula
                        if rubric_formula:
                            table_formula = Table('FOFORMULAS')
                            table_formula.set_value('CODI_EMP', table.get_value('CODI_EMP'))
                            table_formula.set_value('I_EVENTOS', table.get_value('I_EVENTOS'))
                            table_formula.set_value('SCRIPT', rubric_formula.get('SCRIPT'))
                            table_formula.set_value('FIL1', rubric_formula.get('FIL1'))
                            table_formula.set_value('FIL2', rubric_formula.get('FIL2'))
                            table_formula.set_value('FIL3', rubric_formula.get('FIL3'))
                            table_formula.set_value('FIL4', rubric_formula.get('FIL4'))
                            rubrics_formula.append(table_formula.do_output())

                        # gera as bases de cálculo para a rúbrica
                        incidencia_inss = table.get_value('CODIGO_INCIDENCIA_INSS_ESOCIAL')
                        incidencia_irrf = table.get_value('CODIGO_INCIDENCIA_IRRF_ESOCIAL')
                        incidencia_fgts = table.get_value('CODIGO_INCIDENCIA_FGTS_ESOCIAL')
                        incidencia_sindical = table.get_value('CODIGO_INCIDENCIA_SINDICAL_ESOCIAL')

                        # marca qual base de INSS precisa ser gerada conforme a incidência da rubrica
                        base_inss_mensal, base_inss_empresa_mensal, base_inss_terceiros_mensal, base_inss_rat_mensal = get_incidencia_inss(incidencia_inss)

                        # marca qual base de IRRF precisa ser gerada conforme a incidência da rubrica
                        base_irrf = get_incidencia_irrf(incidencia_irrf)

                        # marca qual base de FGTS precisa ser gerada conforme a incidência da rubrica
                        base_fgts = get_incidencia_fgts(incidencia_fgts)

                        if rubric_calc_base:
                            for base_calc in rubric_calc_base:
                                if not is_a_valid_base(incidencia_irrf, incidencia_inss, incidencia_fgts, incidencia_sindical, base_calc['I_CADBASES']):
                                    continue

                                # se a rubrica já tiver a base, não precisa ser gerada
                                if base_inss_mensal == format_int(base_calc['I_CADBASES']):
                                    base_inss_mensal = False

                                if base_inss_empresa_mensal == format_int(base_calc['I_CADBASES']):
                                    base_inss_empresa_mensal = False

                                if base_inss_terceiros_mensal == format_int(base_calc['I_CADBASES']):
                                    base_inss_terceiros_mensal = False

                                if base_inss_rat_mensal == format_int(base_calc['I_CADBASES']):
                                    base_inss_rat_mensal = False

                                if base_irrf == format_int(base_calc['I_CADBASES']):
                                    base_irrf = False

                                if base_fgts == format_int(base_calc['I_CADBASES']):
                                    base_fgts = False

                                table_calc = Table('FOEVENTOSBASES')
                                table_calc.set_value('CODI_EMP', table.get_value('CODI_EMP'))
                                table_calc.set_value('I_EVENTOS', table.get_value('I_EVENTOS'))
                                table_calc.set_value('I_CADBASES', base_calc['I_CADBASES'])
                                table_calc.set_value('ENVIAR_ESOCIAL', base_calc['ENVIAR_ESOCIAL'])
                                table_calc.set_value('INCLUSAO_VALIDADA_ESOCIAL', base_calc['INCLUSAO_VALIDADA_ESOCIAL'])
                                table_calc.set_value('GERAR_RETIFICACAO_ESOCIAL', base_calc['GERAR_RETIFICACAO_ESOCIAL'])
                                table_calc.set_value('PROCESSAR_EXCLUSAO_ESOCIAL', base_calc['PROCESSAR_EXCLUSAO_ESOCIAL'])
                                table_calc.set_value('COMPANY_ID', base_calc['COMPANY_ID'])

                                rubrics_base_calc_importation.append(table_calc.do_output())

                        # gera a base de calculo se a rubrica tiver com determinada incidência marcada
                        if base_inss_mensal:
                            default_base = generate_default_base(table.get_value('CODI_EMP'), table.get_value('I_EVENTOS'), base_inss_mensal)
                            rubrics_base_calc_importation.append(default_base)

                        if base_inss_empresa_mensal:
                            default_base = generate_default_base(table.get_value('CODI_EMP'), table.get_value('I_EVENTOS'), base_inss_empresa_mensal)
                            rubrics_base_calc_importation.append(default_base)

                        if base_inss_terceiros_mensal:
                            default_base = generate_default_base(table.get_value('CODI_EMP'), table.get_value('I_EVENTOS'), base_inss_terceiros_mensal)
                            rubrics_base_calc_importation.append(default_base)

                        if base_inss_rat_mensal:
                            default_base = generate_default_base(table.get_value('CODI_EMP'), table.get_value('I_EVENTOS'), base_inss_rat_mensal)
                            rubrics_base_calc_importation.append(default_base)

                        if base_irrf:
                            default_base = generate_default_base(table.get_value('CODI_EMP'), table.get_value('I_EVENTOS'), base_irrf)
                            rubrics_base_calc_importation.append(default_base)

                        if base_fgts:
                            default_base = generate_default_base(table.get_value('CODI_EMP'), table.get_value('I_EVENTOS'), base_fgts)
                            rubrics_base_calc_importation.append(default_base)

        return rubrics_importation, rubrics_base_calc_importation, rubrics_formula

    def search_similar_rubric(self, rubric, data_rubrics):
        """
        Procura uma rúbrica da Domínio o mais similar possível com a rúbrica da importação
        e retorna os campos NATUREZA_FOLHA_MENSAL e I_EVENTOS da rubrica encontrada
        """
        natureza_folha_mensal_dominio = ''
        index_rubric = ''

        fields_to_compare = [
            'PROV_DESC',
            'CODIGO_INCIDENCIA_INSS_ESOCIAL',
            'CODIGO_INCIDENCIA_IRRF_ESOCIAL',
            'CODIGO_INCIDENCIA_FGTS_ESOCIAL',
            'CODIGO_INCIDENCIA_SINDICAL_ESOCIAL'
        ]

        # Vai checando qual a rúbrica com mais tem campos iguais
        natureza_folha_mensal = rubric.get('NATUREZA_FOLHA_MENSAL')
        if str(natureza_folha_mensal) not in 'NULO' and natureza_folha_mensal in data_rubrics.keys():
            if len(data_rubrics[natureza_folha_mensal]) > 1:
                old_advance = 0
                for dominio_rubric in data_rubrics[natureza_folha_mensal]:
                    advance = 0
                    for number_field, field in enumerate(fields_to_compare):
                        if str(dominio_rubric.get(field)) == str(rubric.get(field)):
                            advance += 1
                            if len(fields_to_compare) == (number_field+1):
                                natureza_folha_mensal_dominio = dominio_rubric.get('NATUREZA_FOLHA_MENSAL')
                                index_rubric = data_rubrics[natureza_folha_mensal].index(dominio_rubric)
                        else:
                            if advance > old_advance:
                                natureza_folha_mensal_dominio = dominio_rubric.get('NATUREZA_FOLHA_MENSAL')
                                index_rubric = data_rubrics[natureza_folha_mensal].index(dominio_rubric)
                                old_advance = int(advance)

        return natureza_folha_mensal_dominio, index_rubric

    def generate_i_evento(self, codi_emp_eventos, dominio_rubrics, dominio_rubrics_esocial, cnpj_companies):
        """
        Gera um código de evento válido, dentro do range permitido(maior que 201).
        E retorna o código da rubrica e o código eSocial
        """
        i_evento = 201
        codigo_esocial = 201
        raiz_cnpj = str(cnpj_companies[codi_emp_eventos])[0:8]

        while True:
            if i_evento in dominio_rubrics[codi_emp_eventos]:
                i_evento += 1
            else:
                codigo_esocial = i_evento
                while True:
                    if str(codigo_esocial) in dominio_rubrics_esocial[raiz_cnpj]:
                        codigo_esocial += 1
                    else:
                        break
                break

        dominio_rubrics[codi_emp_eventos].append(i_evento)
        dominio_rubrics_esocial[raiz_cnpj].append(str(codigo_esocial))
        return i_evento, codigo_esocial


def get_incidencia_inss(incidencia):
    """
    Retorna os códigos de bases respectivos de cada incidência de base de INSS
    """
    base_inss_mensal = False
    base_inss_empresa_mensal = False
    base_inss_terceiros_mensal = False
    base_inss_rat_mensal = False

    if format_int(incidencia) in [11, 12, 13]:
        base_inss_mensal, base_inss_empresa_mensal, base_inss_terceiros_mensal, base_inss_rat_mensal = incidencias_bases_INSS.get(str(incidencia))

    return base_inss_mensal, base_inss_empresa_mensal, base_inss_terceiros_mensal, base_inss_rat_mensal


def get_incidencia_irrf(incidencia):
    """
    Retorna os códigos de bases respectivos de cada incidência de base de IRRF
    """
    base_irrf = False

    if format_int(incidencia) in [11, 12, 13]:
        base_irrf = incidencias_bases_IRRF.get(str(incidencia))[0]

    return base_irrf


def get_incidencia_fgts(incidencia):
    """
    Retorna os códigos de bases respectivos de cada incidência de base de FGTS
    """
    base_fgts = False

    if format_int(incidencia) in [11, 12]:
        base_fgts = incidencias_bases_FGTS.get(str(incidencia))[0]

    return base_fgts


def check_inss_irrf_fgts_base(tipo, incidencia, i_cad_base):
    """
    Checa se a base de INSS, IRRF e FGTS estão de acordo com a incidência da rubrica.
    Exemplo: rubrica está com incidência de IRRF mensal marcada e tem uma base de IRRF férias.
    """
    formated_i_cad_base = format_int(i_cad_base)
    if tipo == 'IRRF':
        if str(incidencia) in incidencias_bases_IRRF.keys():
            if formated_i_cad_base in get_all_incidencias('IRRF'):
                return formated_i_cad_base == get_incidencia_irrf(incidencia)
            else:
                return True
        else:
            return True
    if tipo == 'INSS':
        if str(incidencia) in incidencias_bases_INSS.keys():
            if formated_i_cad_base in get_all_incidencias('INSS'):
                return formated_i_cad_base in get_incidencia_inss(incidencia)
            else:
                return True
        else:
            return True
    if tipo == 'FGTS':
        if str(incidencia) in incidencias_bases_FGTS.keys():
            if formated_i_cad_base in get_all_incidencias('FGTS'):
                return formated_i_cad_base == get_incidencia_fgts(incidencia)
            else:
                return True
        else:
            return True


def get_all_incidencias(tipo):
    """
    Retorna todos os códigos de bases que podem ser incidências de IRRF, FGTS ou INSS
    """
    result = []
    values = []
    if tipo == 'INSS':
        values = incidencias_bases_INSS.values()
    elif tipo == 'IRRF':
        values = incidencias_bases_IRRF.values()
    elif tipo == 'FGTS':
        values = incidencias_bases_FGTS.values()

    for lista_bases in values:
        result.extend(lista_bases)

    return result


def ignore_base_calc(base, base_calc):
    """"
    Função para validar se a base de calculo é uma base referente a IRRF, INSS, FGTS ou Sindical
    """
    if base in 'IRRF':
        if int(base_calc) in i_cadbases_irrf:
            return True

    if base in 'INSS':
        if int(base_calc) in i_cadbases_inss:
            return True

    if base in 'FGTS':
        if int(base_calc) in i_cadbases_fgts:
            return True

    if base in 'SINDICAL':
        if int(base_calc) == 6:
            return True

    return False

def is_a_valid_base(incidencia_irrf, incidencia_inss, incidencia_fgts, incidencia_sindical, i_cadbases):
    """
    Valida se o código da base está valida de acordo com a incidência da rúbrica
    """
    # se tiver desmarcada a incidência de IRRF, retira as bases de calculo referente ao IRRF
    if not is_null(incidencia_irrf):
        if format_int(incidencia_irrf) in [0, 9]:
            if ignore_base_calc('IRRF', i_cadbases):
                return False
        else:
            if not check_inss_irrf_fgts_base('IRRF', incidencia_irrf, i_cadbases):
                return False

    # se tiver desmarcada a incidência de INSS, retira as bases de calculo referente ao INSS
    if not is_null(incidencia_inss):
        if format_int(incidencia_inss) in [0]:
            if ignore_base_calc('INSS', i_cadbases):
                return False
        else:
            if not check_inss_irrf_fgts_base('INSS', incidencia_inss, i_cadbases):
                return False

    # se tiver desmarcada a incidência de FGTS, retira as bases de calculo referente ao FGTS
    if not is_null(incidencia_fgts):
        if format_int(incidencia_fgts) in [0]:
            if ignore_base_calc('FGTS', i_cadbases):
                return False
        else:
            if not check_inss_irrf_fgts_base('FGTS', incidencia_fgts, i_cadbases):
                return False

    # se tiver desmarcada a incidência SINDICAL, retira as bases de calculo referente ao sindicato
    if not is_null(incidencia_sindical):
        if format_int(incidencia_sindical) in [0]:
            if ignore_base_calc('SINDICAL', i_cadbases):
                return False

    return True


def generate_default_base(codi_emp, i_eventos, i_cadbases):
    """
    Gerar um registro padrão da tabela FOEVENTOSBASES com os dados passados por parâmetro
    """
    table_calc = Table('FOEVENTOSBASES')
    table_calc.set_value('CODI_EMP', codi_emp)
    table_calc.set_value('I_EVENTOS', i_eventos)
    table_calc.set_value('I_CADBASES', i_cadbases)
    table_calc.set_value('ENVIAR_ESOCIAL', 1)
    table_calc.set_value('INCLUSAO_VALIDADA_ESOCIAL', 0)
    table_calc.set_value('GERAR_RETIFICACAO_ESOCIAL', 0)
    table_calc.set_value('PROCESSAR_EXCLUSAO_ESOCIAL', 0)
    table_calc.set_value('COMPANY_ID', '00000000000000000000000000000000')

    return table_calc.do_output()


def load_rubrics_relatioship(companies_rubrics, rubrics_relationship, general_rubrics_relationship, uses_company_rubrics):
    for i_eventos in companies_rubrics:
        for codi_emp in companies_rubrics.get(i_eventos):
            codi_emp_eve = uses_company_rubrics.get(codi_emp)

            i_eventos_importation = general_rubrics_relationship.get(i_eventos)
            rubrics_relationship.add(i_eventos_importation, [str(codi_emp_eve), str(i_eventos)])
