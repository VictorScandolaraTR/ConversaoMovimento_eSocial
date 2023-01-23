import os, shutil, json
from tqdm import tqdm
import xml.dom.minidom as xml

class eSocialXML():
    def __init__(self, diretorio_xml):
        self.DIRETORIO_XML = f"{diretorio_xml}\\eventos"
        self.DIRETORIO_DOWNLOADS = f"{diretorio_xml}\\downloads"

        self.dicionario_s1010 = {} # Rubricas
        self.dicionario_s1200 = {} # Remuneração Regime Previdenciário Geral
        self.dicionario_s1202 = {} # Remuneração Regime Previdenciário Próprio
        self.dicionario_s1210 = {} # Pagamentos de Rendimentos do Trabalho
        self.dicionario_s2200 = {} # Afastamentos temporários
        self.dicionario_s2230 = {} # Afastamentos temporários
        self.dicionario_s2299 = {} # Demissão
        self.dicionario_s2300 = {} # Demissão (contribuintes)
        self.dicionario_s2399 = {} # Demissão (contribuintes)

    def preparar_arquivos_xml(self):
        for root, dirs, files in os.walk(self.DIRETORIO_DOWNLOADS):
            arquivos = files.copy()

        print("Extraindo arquivos obtidos do portal")
        os.system("del /q "+self.DIRETORIO_XML)
        for arquivo in tqdm(arquivos):
            if str(arquivo[-3::]).upper()=="ZIP":
                shutil.unpack_archive(f"{self.DIRETORIO_DOWNLOADS}\\{arquivo}", self.DIRETORIO_XML)

    def carregar_informacoes_xml(self):

        for root, dirs, files in os.walk(self.DIRETORIO_XML):
            arquivos = files.copy()

        for arquivo in tqdm(arquivos):
            try:
                doc = xml.parse(self.DIRETORIO_XML+"\\"+arquivo)

                for eSocial in doc.getElementsByTagName("eSocial"):
                    xmlns = eSocial.getAttribute("xmlns")
                    if(xmlns==None): evento = ""
                    elif(xmlns==""): evento = ""
                    else: evento = xmlns.split('/')[-2]

                    match evento:
                        case "evtInfoEmpregador": pass # S-1000
                        case "evtTabEstab": pass # S-1005
                        case "evtTabRubrica": # S-1010
                            inscricao = self.extrai_tag(eSocial,"nrInsc","ideEmpregador")
                            codigo_rubrica = self.extrai_tag(eSocial,"codRubr","ideRubrica")
                            dicionario_atual = {}
                            processos_cp = {}
                            processos_irrf = {}
                            processos_fgts = {}

                            if self.verifica_tag(eSocial,"ideProcessoCP","dadosRubrica"):
                                i = 0
                                while self.extrai_tag(eSocial,"nrProc","ideProcessoCP",i) != "NULO":
                                    processos_cp[i] = {
                                        self.extrai_tag(eSocial,"tpProc","ideProcessoCP"),
                                        self.extrai_tag(eSocial,"nrProc","ideProcessoCP"),
                                        self.extrai_tag(eSocial,"extDecisao","ideProcessoCP"),
                                        self.extrai_tag(eSocial,"codSusp","ideProcessoCP")
                                    }
                                    i = i + 1

                            if self.verifica_tag(eSocial,"ideProcessoIRRF","dadosRubrica"):
                                i = 0
                                while self.extrai_tag(eSocial,"nrProc","ideProcessoIRRF",i) != "NULO":
                                    processos_irrf[i] = {
                                        "numero_processo": self.extrai_tag(eSocial,"nrProc","ideProcessoIRRF"),
                                        "codigo_suspensao": self.extrai_tag(eSocial,"codSusp","ideProcessoIRRF")
                                    }
                                    i = i + 1

                            if self.verifica_tag(eSocial,"ideProcessoFGTS","dadosRubrica"):
                                i = 0
                                while self.extrai_tag(eSocial,"nrProc","ideProcessoFGTS",i) != "NULO":
                                    processos_fgts[i] = {
                                        "numero_processo": self.extrai_tag(eSocial,"nrProc","ideProcessoFGTS")
                                    }
                                    i = i + 1

                            dicionario_atual = {
                                "inscricao_empresa": inscricao,
                                "codigo_rubrica": codigo_rubrica,
                                "tabela_rubrica": self.extrai_tag(eSocial,"ideTabRubr","ideRubrica"),
                                "inicio_validade": self.extrai_tag(eSocial,"iniValid","ideRubrica"),
                                "fim_validade": self.extrai_tag(eSocial,"fimValid","ideRubrica"),
                                "descricao": self.extrai_tag(eSocial,"dscRubr","dadosRubrica"),
                                "natureza_rubrica": self.extrai_tag(eSocial,"natRubr","dadosRubrica"),
                                "tipo_rubrica": self.extrai_tag(eSocial,"tpRubr","dadosRubrica"),
                                "incidencia_previdencia": self.extrai_tag(eSocial,"codIncCP","dadosRubrica"),
                                "incidencia_irrf": self.extrai_tag(eSocial,"codIncIRRF","dadosRubrica"),
                                "incidencia_fgts": self.extrai_tag(eSocial,"codIncFGTS","dadosRubrica"),
                                "incidencia_rpps": self.extrai_tag(eSocial,"codIncCPRP","dadosRubrica"),
                                "teto_remuneratorio": self.extrai_tag(eSocial,"tetoRemun","dadosRubrica"),
                                "observacao": self.extrai_tag(eSocial,"observacao","dadosRubrica"),
                                "processos_cp": processos_cp,
                                "processos_irrf": processos_irrf,
                                "processos_fgts": processos_fgts
                            }
                            self.dicionario_s1010[f"{inscricao}-{codigo_rubrica}"] = dicionario_atual
                        case "evtTabLotacao": pass # S-1020
                        case "evtTabCargo": pass # S-1030
                        case "evtRemun": # S-1200
                            lista_remuneracoes = {}
                            tipo_inscricao = self.extrai_tag(eSocial,"tpInsc","ideEmpregador")
                            inscricao = self.extrai_tag(eSocial,"nrInsc","ideEmpregador")
                            cpf = self.extrai_tag(eSocial,"cpfTrab","ideTrabalhador")
                            periodo_apuracao = self.extrai_tag(eSocial,"perApur","ideEvento")

                            if(len(periodo_apuracao)>4):
                                data_dominio = f'01/{periodo_apuracao.split("-")[1]}/{periodo_apuracao.split("-")[0]}'
                            else:
                                data_dominio = f'01/12/{periodo_apuracao}'
                            
                            if self.verifica_tag(eSocial,"itensRemun","remunPerApur"):
                                i = 0
                                while self.extrai_tag(eSocial,"codRubr","itensRemun",i) != "NULO":
                                    rubrica = self.extrai_tag(eSocial,"codRubr","itensRemun",i)
                                    valor = self.extrai_tag(eSocial,"vrRubr","itensRemun",i)
                                    quantidade = self.extrai_tag(eSocial,"qtdRubr","itensRemun",i)

                                    lista_remuneracoes[rubrica] = {
                                        "rubrica": rubrica,
                                        "quantidade": quantidade,
                                        "valor": valor
                                    }
                                    i = i + 1

                            dicionario_atual = {
                                "tipo_inscricao": tipo_inscricao,
                                "inscricao": inscricao,
                                "data": data_dominio,
                                "cpf": cpf,
                                "lista_remuneracoes": lista_remuneracoes
                            }
                            self.dicionario_s1200[f"{inscricao}-{cpf}-{data_dominio}"] = dicionario_atual

                        case "evtPgtos": # S-1210
                            lista_pagamentos = {}
                            tipo_inscricao = self.extrai_tag(eSocial,"tpInsc","ideEmpregador")
                            inscricao = self.extrai_tag(eSocial,"nrInsc","ideEmpregador")
                            cpf = self.extrai_tag(eSocial,"cpfTrab","ideTrabalhador")
                            periodo_apuracao = self.extrai_tag(eSocial,"perApur","ideEvento")

                            if(len(periodo_apuracao)>4):
                                data_dominio = f'01/{periodo_apuracao.split("-")[1]}/{periodo_apuracao.split("-")[0]}'
                            else:
                                data_dominio = f'01/12/{periodo_apuracao}'
                            
                            if self.verifica_tag(eSocial,"ideBenef","evtPgtos"):
                                i = 0
                                while self.extrai_tag(eSocial,"dtPgto","infoPgto",i) != "NULO":
                                    data_pagamento = self.extrai_tag(eSocial,"dtPgto","infoPgto",i)
                                    tipo = self.extrai_tag(eSocial,"tpPgto","infoPgto",i)
                                    periodo = self.extrai_tag(eSocial,"perRef","infoPgto",i)
                                    identificador = self.extrai_tag(eSocial,"ideDmDev","infoPgto",i)
                                    valor = self.extrai_tag(eSocial,"vrLiq","infoPgto",i)

                                    lista_pagamentos[data_pagamento] = {
                                        "data_pagamento": data_pagamento,
                                        "tipo": tipo,
                                        "periodo": periodo,
                                        "identificador": identificador,
                                        "valor": valor
                                    }
                                    i = i + 1

                            dicionario_atual = {
                                "tipo_inscricao": tipo_inscricao,
                                "inscricao": inscricao,
                                "data": data_dominio,
                                "cpf": cpf,
                                "lista_pagamentos": lista_pagamentos
                            }
                            self.dicionario_s1200[f"{inscricao}-{cpf}-{data_dominio}"] = dicionario_atual

                        case "evtReabreEvPer": pass # S-1298
                        case "evtFechaEvPer": pass # S-1299
                        case "evtAdmPrelim": pass # S-2190
                        case "evtAdmissao": pass # S-2200
                        case "evtAltCadastral": pass # S-2205
                        case "evtAltContratual": pass # S-2206
                        case "evtMonit": pass # S-2220
                        case "evtAfastTemp": # S-2230
                            inscricao = self.extrai_tag(doc,"nrInsc")
                            cpf = self.extrai_tag(doc,"cpfTrab")
                            inicio_afastamento = self.extrai_tag(doc,"dtIniAfast")
                            id_evento = eSocial.getElementsByTagName("evtAfastTemp")[0].getAttribute("Id")

                            if(inicio_afastamento!="NULO"):
                                dicionario_atual = {
                                    "inscricao" : inscricao,
                                    "cpf" : cpf,
                                    "matricula" : self.extrai_tag(doc,"matricula"),
                                    "data_inicio_afastamento" : inicio_afastamento,
                                    #"numero_inicio_afastamento" : int(self.formata_data(inicio_afastamento,formato_final="number")),
                                    "data_termino_afastamento" : self.extrai_tag(doc,"dtTermAfast"),
                                    "data_inicio_periodo_aquisitivo": self.extrai_tag(doc,"dtInicio","perAquis"),
                                    "data_fim_periodo_aquisitivo": self.extrai_tag(doc,"dtFim","perAquis"),
                                    "dias_afastamento": self.extrai_tag(doc,"qtdDiasAfast","infoAtestado"),
                                    "motivo_afastamento": self.extrai_tag(doc,"codMotAfast"),
                                    "ID": id_evento
                                }
                                self.dicionario_s2230[inscricao+"-"+cpf+"-"+inicio_afastamento+"-I"] = dicionario_atual
                            else:
                                termino_afastamento = self.extrai_tag(doc,"dtTermAfast")
                                dicionario_atual = {
                                    "inscricao" : inscricao,
                                    "cpf" : cpf,
                                    "matricula" : self.extrai_tag(doc,"matricula"),
                                    "data_termino_afastamento" : self.extrai_tag(doc,"dtTermAfast"),
                                    #"numero_termino_afastamento" : int(self.formata_data(self.extrai_tag(eSocial,"dtTermAfast"),formato_final="number")),
                                    "dias_afastamento": self.extrai_tag(doc,"qtdDiasAfast","infoAtestado"),
                                    "aplicado":"N",
                                    "ID": id_evento
                                }
                                self.dicionario_s2230[inscricao+"-"+cpf+"-"+termino_afastamento+"-T"] = dicionario_atual
                        case "evtExpRisco": pass # S-2240
                        case "evtDeslig": # S-2299
                            inscricao = self.extrai_tag(doc,"nrInsc")
                            cpf = self.extrai_tag(doc,"cpfTrab")
                            id_evento = eSocial.getElementsByTagName("evtDeslig")[0].getAttribute("Id")

                            dicionario_atual = {
                                "inscricao": inscricao,
                                "cpf": cpf,
                                "matricula": self.extrai_tag(doc,"matricula"),
                                "motivo_desligamento": self.extrai_tag(doc,"mtvDeslig"),
                                "data_desligamento": self.extrai_tag(doc,"dtDeslig"),
                                "pagamento_aviso_previo": self.extrai_tag(doc,"indPagtoAPI"),
                                "data_fim_aviso_previo": self.extrai_tag(doc,"dtProjFimAPI"),
                                "pensao_alimenticia": self.extrai_tag(doc,"pensAlim"),
                                "cumprimento_aviso": self.extrai_tag(doc,"indCumprParc"),
                                "id_evento": id_evento
                            }
                            self.dicionario_s2299[inscricao+"-"+cpf] = dicionario_atual

                        case "evtTSVInicio": pass # S-2300
                        case "evtTSVAltContr": pass # S-2305
                        case "evtTSVTermino": # S-2399
                            inscricao = self.extrai_tag(eSocial,"nrInsc")
                            cpf = self.extrai_tag(eSocial,"cpfTrab")

                            dicionario_atual = {
                                "inscricao": inscricao,
                                "cpf": cpf,
                                "matricula": self.extrai_tag(eSocial,"matricula"),
                                "motivo_desligamento": self.extrai_tag(eSocial,"mtvDeslig"),
                                "data_desligamento": self.extrai_tag(eSocial,"dtDeslig"),
                                "pagamento_aviso_previo": self.extrai_tag(eSocial,"indPagtoAPI"),
                                "data_fim_aviso_previo": self.extrai_tag(eSocial,"dtProjFimAPI"),
                                "pensao_alimenticia": self.extrai_tag(eSocial,"pensAlim"),
                                "cumprimento_aviso": self.extrai_tag(eSocial,"indCumprParc")
                            }
                            self.dicionario_s2399[inscricao+"-"+cpf] = dicionario_atual

                        case "evtExclusao": pass # S-3000
                        case "evtBasesTrab": pass # S-5001
                        case "evtIrrf": pass # S-5002
                        case "evtIrrfBenef": pass # S-5002
                        case "evtBasesFGTS": pass # S-5003
                        case "evtCS": pass # S-5011
                        case "evtFGTS": pass # S-5013
                        case "retornoEvento": pass # Retorno de consulta de evento
                        case "retornoProcessamento": pass # Retorno de envio de evento

            except Exception as e:
                print(f"Erro:{arquivo}")
                print(e)

    def extrai_tag(self,docXML, tag, tag_superior = '', ocorrencia = 0, ocorrencia_filho = 0, nulo_zero = False):
        '''Extrai tag do xml, atribuindo NULO ou 0 quando a tag não é encontrada.'''

        try:
            if(tag_superior==''):
                return (docXML.getElementsByTagName(tag)[ocorrencia].firstChild.nodeValue if self.verifica_tag(docXML,tag) else "NULO")
            else:
                return (docXML.getElementsByTagName(tag_superior)[ocorrencia].getElementsByTagName(tag)[ocorrencia_filho].firstChild.nodeValue if self.verifica_tag(docXML,tag,tag_superior) else "NULO")
        except IndexError:
            if(nulo_zero): # nulo_zero deve ser True em campos que não aceitam NULO na importação
                return 0
            else:
                return "NULO"

    def verifica_tag(self,docXML, tag, tag_superior = ''):
        '''Verifica a existência de uma tag em um objeto xml'''

        try:
            if(tag_superior==''):
                docXML.getElementsByTagName(tag)[0]
            else:
                docXML.getElementsByTagName(tag_superior)[0].getElementsByTagName(tag)[0]
            return True
        except IndexError:
            return False  

esocial = eSocialXML("xml")
esocial.carregar_informacoes_xml()

f = open("s1010.json","w")
f.write(json.dumps(esocial.dicionario_s1010))
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
f.close()