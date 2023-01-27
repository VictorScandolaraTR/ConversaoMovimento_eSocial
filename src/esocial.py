import os, shutil, json, xmltodict, Levenshtein
from tqdm import tqdm
from classes.Table import Table
from sqlalchemy import create_engine
import xml.dom.minidom as xml
import pandas as pd

class eSocialXML():
    def __init__(self, diretorio_xml):
        self.DIRETORIO_RAIZ = diretorio_xml
        self.DIRETORIO_XML = f"{diretorio_xml}\\eventos"
        self.DIRETORIO_DOWNLOADS = f"{diretorio_xml}\\downloads"
        self.DIRETORIO_SAIDA = f"{diretorio_xml}\\saida"

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
        self.senha_dominio = parametros["senha_dominio"]
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

    def relaciona_empresas(self):
        '''Gera listagem de empresas que tem rubricas sendo tratadas'''
        dicionario_empresas = {}
        cgcs_rubricas = []

        engine = create_engine("sybase+pyodbc://{user}:{pw}@{dsn}".format(user=self.usuario_dominio, pw=self.senha_dominio, dsn=self.base_dominio))

        sql = "SELECT * FROM BETHADBA.GEEMPRE"
        df_empresas = pd.read_sql(sql,con=engine)

        for rubrica in self.dicionario_s1010:
            inscricao = self.dicionario_s1010.get(rubrica).get("ideEmpregador").get("nrInsc")

            if(self.dicionario_s1010.get(rubrica).get("ideEmpregador").get("tpInsc")=="1"):
                inscricao = self.completar_cnpj(inscricao)

            if inscricao not in cgcs_rubricas:
                cgcs_rubricas.append(inscricao)

        for i in range(len(df_empresas)):
            if(df_empresas.loc[i,"cgce_emp"] in cgcs_rubricas):
                dicionario_empresas[inscricao] = {
                    "codigo":df_empresas.loc[i,"codi_emp"],
                    "nome":df_empresas.loc[i,"nome_emp"],
                    "cgc":df_empresas.loc[i,"cgce_emp"]
                }

        return dicionario_empresas

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
    
    def gera_excel_relacao(self):
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

    def gerar_arquivos_saida(self):
        tabela_FOEVENTOS = []

        dicionario_s1010 = self.processar_rubricas()

        for s1010 in dicionario_s1010:
            inscricao = dicionario_s1010[s1010].get("ideEmpregador").get("nrInsc")
            codigo_rubrica = dicionario_s1010[s1010].get("infoRubrica").get("inclusao").get("ideRubrica").get("codRubr")
            descricao = dicionario_s1010[s1010].get("infoRubrica").get("inclusao").get("dadosRubrica").get("dscRubr")
            natureza = dicionario_s1010[s1010].get("infoRubrica").get("inclusao").get("dadosRubrica").get("natRubr")
            tipo = dicionario_s1010[s1010].get("infoRubrica").get("inclusao").get("dadosRubrica").get("tpRubr")
            inss = dicionario_s1010[s1010].get("infoRubrica").get("inclusao").get("dadosRubrica").get("codIncCP")
            irrf = dicionario_s1010[s1010].get("infoRubrica").get("inclusao").get("dadosRubrica").get("codIncIRRF")
            fgts = dicionario_s1010[s1010].get("infoRubrica").get("inclusao").get("dadosRubrica").get("codIncFGTS")
            sindicato = dicionario_s1010[s1010].get("infoRubrica").get("inclusao").get("dadosRubrica").get("codIncSIND")

            match tipo:
                case 1: tipo = "P" # Vencimento, provento ou pensão
                case 2: tipo = "D" # Desconto
                case 3: tipo = "I" # Informativa
                case 4: tipo = "ID" # Informativa dedutora

            table = Table('FOEVENTOS')
            table.set_value('CODI_EMP', inscricao)
            table.set_value('I_EVENTOS', codigo_rubrica)
            table.set_value('NOME', descricao)
            table.set_value('PROV_DESC', tipo)
            table.set_value('NATUREZA_FOLHA_MENSAL', natureza)
            table.set_value('CODIGO_INCIDENCIA_INSS_ESOCIAL', inss)
            table.set_value('CODIGO_INCIDENCIA_IRRF_ESOCIAL', irrf)
            table.set_value('CODIGO_INCIDENCIA_FGTS_ESOCIAL', fgts)
            table.set_value('CODIGO_INCIDENCIA_SINDICAL_ESOCIAL', sindicato)
            tabela_FOEVENTOS.append(table.do_output())

            table = Table('FOEVENTOS')
            table.set_value('CODI_EMP', inscricao)
            table.set_value('I_EVENTOS', codigo_rubrica)
            table.set_value('NOME', descricao)
            table.set_value('PROV_DESC', tipo)
            table.set_value('NATUREZA_FOLHA_MENSAL', natureza)
            table.set_value('CODIGO_INCIDENCIA_INSS_ESOCIAL', inss)
            table.set_value('CODIGO_INCIDENCIA_IRRF_ESOCIAL', irrf)
            table.set_value('CODIGO_INCIDENCIA_FGTS_ESOCIAL', fgts)
            table.set_value('CODIGO_INCIDENCIA_SINDICAL_ESOCIAL', sindicato)
            tabela_FOEVENTOS.append(table.do_output())