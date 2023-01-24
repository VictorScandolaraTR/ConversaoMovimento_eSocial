import os, shutil, json, xmltodict
from tqdm import tqdm
import xml.dom.minidom as xml
#from Table import Table

class eSocialXML():
    def __init__(self, diretorio_xml):
        self.DIRETORIO_XML = f"{diretorio_xml}\\eventos"
        self.DIRETORIO_DOWNLOADS = f"{diretorio_xml}\\downloads"

        self.dicionario_s1010 = {} # Rubricas
        self.dicionario_s1200 = {} # Remuneração Regime Previdenciário Geral
        self.dicionario_s1202 = {} # Remuneração Regime Previdenciário Próprio
        self.dicionario_s1210 = {} # Pagamentos de Rendimentos do Trabalho
        self.dicionario_s2230 = {} # Afastamentos temporários
        self.dicionario_s2299 = {} # Demissão
        self.dicionario_s2399 = {} # Demissão (contribuintes)

    def baixar_dados_esocial(self, usuario, senha, certificado, tipo_certificado = "A1"):
        '''Acessa o portal e-Social com as credenciais necessárias e faz download dos arquivos do período'''
        pass

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

        f = open("eventos_nao_tratados.json","w")
        f.write(json.dumps(eventos_nao_tratados))
        f.close()