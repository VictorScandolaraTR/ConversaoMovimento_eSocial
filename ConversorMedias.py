from datetime import datetime
from genericpath import isdir
import os
import sys
import xml.dom.minidom as xml
import json
import re
import math
import pandas as pd
from tqdm import tqdm
import Levenshtein

pasta_conversor_un = sys.path[0].split('\\')[-6]
caminho_conversor_un = sys.path[0].split(pasta_conversor_un)[0]+pasta_conversor_un
caminho_completo_pacotes = f'{caminho_conversor_un}\[CONV]\[Python]'
sys.path.append(caminho_completo_pacotes)

from classes.Table import Table
from utils.functions import *

class ConversorXMLeSocial():
    def __init__(self, pasta_entrada, pasta_saida, pasta_xml, conversor, empresa_rubricas = 9996):
        self.DIRETORIO_ENTRADA = pasta_entrada
        self.DIRETORIO_SAIDA = pasta_saida
        self.DIRETORIO_XML = pasta_xml
        self.CONVERSOR = conversor
        self.rubricas_cadastrar = []
        self.rubricas_novas = []

        self.dicionario_s1010 = {} # Rubricas
        self.dicionario_s1200 = {} # Remuneração Regime Previdenciário Geral
        self.dicionario_s1202 = {} # Remuneração Regime Previdenciário Próprio
        self.dicionario_s1210 = {} # Pagamentos de Rendimentos do Trabalho
        self.dicionario_s2230 = {} # Afastamentos temporários
        self.dicionario_s2299 = {} # Demissão
        self.dicionario_s2399 = {} # Demissão (contribuintes)

        self.dicionario_rubricas_esocial = {}
        self.dicionario_bases_rubricas_esocial = {}
        self.dicionario_formulas_esocial = {}
        
        print('Carregando rubricas padrão do sistema Domínio')
        data_frame_rubricas_dominio = pd.read_table(f'{caminho_completo_pacotes}\classes\\FOEVENTOS.txt')
        data_frame_bases_rubricas_dominio = pd.read_table(f'{caminho_completo_pacotes}\classes\\FOEVENTOSBASES.txt', sep="\t")
        data_frame_formulas_dominio = pd.read_table(f'{caminho_completo_pacotes}\classes\\FOFORMULAS.txt', sep="\t")

        for i in range(len(data_frame_rubricas_dominio)):
            if(int(data_frame_rubricas_dominio.loc[i,"codi_emp"])==empresa_rubricas):
                self.dicionario_rubricas_esocial[data_frame_rubricas_dominio.loc[i,"i_eventos"]] = {
                    "i_eventos": data_frame_rubricas_dominio.loc[i,"i_eventos"],
                    "nome": data_frame_rubricas_dominio.loc[i,"nome"],
                    "soma_med_13": data_frame_rubricas_dominio.loc[i,"soma_med_13"],
                    "soma_med_fer": data_frame_rubricas_dominio.loc[i,"soma_med_fer"],
                    "taxa": data_frame_rubricas_dominio.loc[i,"taxa"],
                    "prov_desc": data_frame_rubricas_dominio.loc[i,"prov_desc"],
                    "tipo_inf": data_frame_rubricas_dominio.loc[i,"tipo_inf"],
                    "tipo_base": data_frame_rubricas_dominio.loc[i,"tipo_base"],
                    "base_irrf": data_frame_rubricas_dominio.loc[i,"base_irrf"],
                    "base_inss": data_frame_rubricas_dominio.loc[i,"base_inss"],
                    "base_fgts": data_frame_rubricas_dominio.loc[i,"base_fgts"],
                    "base_sindicato": data_frame_rubricas_dominio.loc[i,"base_sindicato"],
                    "base_hextra": data_frame_rubricas_dominio.loc[i,"base_hextra"],
                    "base_periculosidade": data_frame_rubricas_dominio.loc[i,"base_periculosidade"],
                    "base_aux1": data_frame_rubricas_dominio.loc[i,"base_aux1"],
                    "base_aux2": data_frame_rubricas_dominio.loc[i,"base_aux2"],
                    "base_aux3": data_frame_rubricas_dominio.loc[i,"base_aux3"],
                    "horas_mes": data_frame_rubricas_dominio.loc[i,"horas_mes"],
                    "comp_13fer": data_frame_rubricas_dominio.loc[i,"comp_13fer"],
                    "soma_fic_fin": data_frame_rubricas_dominio.loc[i,"soma_fic_fin"],
                    "soma_rais": data_frame_rubricas_dominio.loc[i,"soma_rais"],
                    "soma_inf_ren": data_frame_rubricas_dominio.loc[i,"soma_inf_ren"],
                    "paga_prop": data_frame_rubricas_dominio.loc[i,"paga_prop"],
                    "aparece_recibo": data_frame_rubricas_dominio.loc[i,"aparece_recibo"],
                    "soma_sal_base": data_frame_rubricas_dominio.loc[i,"soma_sal_base"],
                    "ordem_calculo": data_frame_rubricas_dominio.loc[i,"ordem_calculo"],
                    "classificacao": data_frame_rubricas_dominio.loc[i,"classificacao"],
                    "rend_tributaveis": data_frame_rubricas_dominio.loc[i,"rend_tributaveis"],
                    "rend_isentos": data_frame_rubricas_dominio.loc[i,"rend_isentos"],
                    "rend_sujeitos": data_frame_rubricas_dominio.loc[i,"rend_sujeitos"],
                    "base_pis": data_frame_rubricas_dominio.loc[i,"base_pis"],
                    "rend_adicionais": data_frame_rubricas_dominio.loc[i,"rend_adicionais"],
                    "base_rdsr": data_frame_rubricas_dominio.loc[i,"base_rdsr"],
                    "base_rdsr_eve": data_frame_rubricas_dominio.loc[i,"base_rdsr_eve"],
                    "soma_med_afast": data_frame_rubricas_dominio.loc[i,"soma_med_afast"],
                    "soma_med_afast_02": data_frame_rubricas_dominio.loc[i,"soma_med_afast_02"],
                    "soma_med_afast_03": data_frame_rubricas_dominio.loc[i,"soma_med_afast_03"],
                    "soma_med_afast_04": data_frame_rubricas_dominio.loc[i,"soma_med_afast_04"],
                    "soma_med_afast_05": data_frame_rubricas_dominio.loc[i,"soma_med_afast_05"],
                    "soma_med_afast_06": data_frame_rubricas_dominio.loc[i,"soma_med_afast_06"],
                    "soma_med_afast_07": data_frame_rubricas_dominio.loc[i,"soma_med_afast_07"],
                    "soma_med_afast_13": data_frame_rubricas_dominio.loc[i,"soma_med_afast_13"],
                    "soma_med_afast_14": data_frame_rubricas_dominio.loc[i,"soma_med_afast_14"],
                    "soma_med_afast_24": data_frame_rubricas_dominio.loc[i,"soma_med_afast_24"],
                    "i_cadbases": data_frame_rubricas_dominio.loc[i,"i_cadbases"],
                    "calc_afast": data_frame_rubricas_dominio.loc[i,"calc_afast"],
                    "adic_afast": data_frame_rubricas_dominio.loc[i,"adic_afast"],
                    "i_horasaula": data_frame_rubricas_dominio.loc[i,"i_horasaula"],
                    "CALC_AFAST_02": data_frame_rubricas_dominio.loc[i,"CALC_AFAST_02"],
                    "CALC_AFAST_03": data_frame_rubricas_dominio.loc[i,"CALC_AFAST_03"],
                    "CALC_AFAST_04": data_frame_rubricas_dominio.loc[i,"CALC_AFAST_04"],
                    "CALC_AFAST_05": data_frame_rubricas_dominio.loc[i,"CALC_AFAST_05"],
                    "CALC_AFAST_06": data_frame_rubricas_dominio.loc[i,"CALC_AFAST_06"],
                    "CALC_AFAST_07": data_frame_rubricas_dominio.loc[i,"CALC_AFAST_07"],
                    "CALC_AFAST_13": data_frame_rubricas_dominio.loc[i,"CALC_AFAST_13"],
                    "CALC_AFAST_14": data_frame_rubricas_dominio.loc[i,"CALC_AFAST_14"],
                    "CALC_AFAST_24": data_frame_rubricas_dominio.loc[i,"CALC_AFAST_24"],
                    "CALC_FIXO_FER": data_frame_rubricas_dominio.loc[i,"CALC_FIXO_FER"],
                    "CALC_FIXO_FER_EVE": data_frame_rubricas_dominio.loc[i,"CALC_FIXO_FER_EVE"],
                    "CALC_FIXO_FER_PROP_MES": data_frame_rubricas_dominio.loc[i,"CALC_FIXO_FER_PROP_MES"],
                    "CALC_FIXO_FER_PROP_FER": data_frame_rubricas_dominio.loc[i,"CALC_FIXO_FER_PROP_FER"],
                    "CALC_FIXO_13": data_frame_rubricas_dominio.loc[i,"CALC_FIXO_13"],
                    "CALC_FIXO_13_EVE": data_frame_rubricas_dominio.loc[i,"CALC_FIXO_13_EVE"],
                    "HOMOLOGNET": data_frame_rubricas_dominio.loc[i,"HOMOLOGNET"],
                    "RUBRICA": data_frame_rubricas_dominio.loc[i,"RUBRICA"],
                    "CODI_RUBRICA": data_frame_rubricas_dominio.loc[i,"CODI_RUBRICA"],
                    "EMITIR_TERMO_RESCISAO": data_frame_rubricas_dominio.loc[i,"EMITIR_TERMO_RESCISAO"],
                    "CAMPO_TERMO_RESCISAO": data_frame_rubricas_dominio.loc[i,"CAMPO_TERMO_RESCISAO"],
                    "REND_ISENTOS_DESCRICAO": data_frame_rubricas_dominio.loc[i,"REND_ISENTOS_DESCRICAO"],
                    "REND_SUJEITOS_DESCRICAO": data_frame_rubricas_dominio.loc[i,"REND_SUJEITOS_DESCRICAO"],
                    "SOMA_MED_AFAST_26": data_frame_rubricas_dominio.loc[i,"SOMA_MED_AFAST_26"],
                    "CALC_AFAST_26": data_frame_rubricas_dominio.loc[i,"CALC_AFAST_26"],
                    "CORRIGE_MEDIA": data_frame_rubricas_dominio.loc[i,"CORRIGE_MEDIA"],
                    "TIPO_CALCULO": data_frame_rubricas_dominio.loc[i,"TIPO_CALCULO"],
                    "CALC_FIXO_13_DESC_ADIANT_13": data_frame_rubricas_dominio.loc[i,"CALC_FIXO_13_DESC_ADIANT_13"],
                    "CALC_FIXO_ADIANT_13": data_frame_rubricas_dominio.loc[i,"CALC_FIXO_ADIANT_13"],
                    "CALC_FIXO_ADIANT_13_EVE": data_frame_rubricas_dominio.loc[i,"CALC_FIXO_ADIANT_13_EVE"],
                    "CALC_FIXO_ADIANT_13_PROP": data_frame_rubricas_dominio.loc[i,"CALC_FIXO_ADIANT_13_PROP"],
                    "SOMA_MEDIA_AVISO_PREVIO": data_frame_rubricas_dominio.loc[i,"SOMA_MEDIA_AVISO_PREVIO"],
                    "SOMA_ADICIONAL_AVISO_PREVIO": data_frame_rubricas_dominio.loc[i,"SOMA_ADICIONAL_AVISO_PREVIO"],
                    "SOMA_MED_AFAST_32": data_frame_rubricas_dominio.loc[i,"SOMA_MED_AFAST_32"],
                    "COMPOE_CAMPO_23_TERMO_RESCISAO": data_frame_rubricas_dominio.loc[i,"COMPOE_CAMPO_23_TERMO_RESCISAO"],
                    "SOMA_MEDIA_SALDO_SALARIO": data_frame_rubricas_dominio.loc[i,"SOMA_MEDIA_SALDO_SALARIO"],
                    "DESCONTA_DSR": data_frame_rubricas_dominio.loc[i,"DESCONTA_DSR"],
                    "DESCONTA_DSR_EVENTO": data_frame_rubricas_dominio.loc[i,"DESCONTA_DSR_EVENTO"],
                    "COMPOE_ADIANTAMENTO_SALARIAL": data_frame_rubricas_dominio.loc[i,"COMPOE_ADIANTAMENTO_SALARIAL"],
                    "COMPOE_LIQUIDO": data_frame_rubricas_dominio.loc[i,"COMPOE_LIQUIDO"],
                    "TIPO_CONSIDERACAO_CAMPO_23_TERMO_RESCISAO": data_frame_rubricas_dominio.loc[i,"TIPO_CONSIDERACAO_CAMPO_23_TERMO_RESCISAO"],
                    "CALC_AFAST_35": data_frame_rubricas_dominio.loc[i,"CALC_AFAST_35"],
                    "DATA_INICIO": data_frame_rubricas_dominio.loc[i,"DATA_INICIO"],
                    "SITUACAO": data_frame_rubricas_dominio.loc[i,"SITUACAO"],
                    "DATA_INATIVACAO": data_frame_rubricas_dominio.loc[i,"DATA_INATIVACAO"],
                    "NATUREZA_FOLHA_MENSAL": data_frame_rubricas_dominio.loc[i,"NATUREZA_FOLHA_MENSAL"],
                    "NATUREZA_13_INTEGRAL": data_frame_rubricas_dominio.loc[i,"NATUREZA_13_INTEGRAL"],
                    "POSSUI_PROCESSO_REFERENTE_SUSPENSAO_INCIDENCIA_ENCARGOS": data_frame_rubricas_dominio.loc[i,"POSSUI_PROCESSO_REFERENTE_SUSPENSAO_INCIDENCIA_ENCARGOS"],
                    "POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_PATRONAL": data_frame_rubricas_dominio.loc[i,"POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_PATRONAL"],
                    "CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_PATRONAL": data_frame_rubricas_dominio.loc[i,"CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_PATRONAL"],
                    "POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_EMPREGADOS": data_frame_rubricas_dominio.loc[i,"POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_EMPREGADOS"],
                    "CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_EMPREGADOS": data_frame_rubricas_dominio.loc[i,"CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_EMPREGADOS"],
                    "POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_FGTS": data_frame_rubricas_dominio.loc[i,"POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_FGTS"],
                    "CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_FGTS": data_frame_rubricas_dominio.loc[i,"CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_FGTS"],
                    "POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_IRRF": data_frame_rubricas_dominio.loc[i,"POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_IRRF"],
                    "CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_IRRF": data_frame_rubricas_dominio.loc[i,"CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_IRRF"],
                    "POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_SINDICAL": data_frame_rubricas_dominio.loc[i,"POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_SINDICAL"],
                    "CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_SINDICAL": data_frame_rubricas_dominio.loc[i,"CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_SINDICAL"],
                    "PERMITE_INFORMAR_NATUREZA_FOLHA_MENSAL": data_frame_rubricas_dominio.loc[i,"PERMITE_INFORMAR_NATUREZA_FOLHA_MENSAL"],
                    "PERMITE_INFORMAR_NATUREZA_13_INTEGRAL": data_frame_rubricas_dominio.loc[i,"PERMITE_INFORMAR_NATUREZA_13_INTEGRAL"],
                    "CODIGO_ESOCIAL": data_frame_rubricas_dominio.loc[i,"CODIGO_ESOCIAL"],
                    "CONSIDERAR_FALTAS_PAGAMENTO_PROPORCIONAL": data_frame_rubricas_dominio.loc[i,"CONSIDERAR_FALTAS_PAGAMENTO_PROPORCIONAL"],
                    "CALCULA_DIFERENCA_ALTERACAO_PISO_SALARIAL": data_frame_rubricas_dominio.loc[i,"CALCULA_DIFERENCA_ALTERACAO_PISO_SALARIAL"],
                    "I_EVENTOS_DIFERENCA_PISO_SALARIAL": data_frame_rubricas_dominio.loc[i,"I_EVENTOS_DIFERENCA_PISO_SALARIAL"],
                    "PERMITE_CALCULAR_DIFERENCA_PISO_SALARIAL": data_frame_rubricas_dominio.loc[i,"PERMITE_CALCULAR_DIFERENCA_PISO_SALARIAL"],
                    "CALC_AFAST_39": data_frame_rubricas_dominio.loc[i,"CALC_AFAST_39"],
                    "TIPO_VALOR_CONSIDERAR_CALCULO_MEDIAS": data_frame_rubricas_dominio.loc[i,"TIPO_VALOR_CONSIDERAR_CALCULO_MEDIAS"],
                    "DETALHAR_LANCAMENTO_POR_SERVICO": data_frame_rubricas_dominio.loc[i,"DETALHAR_LANCAMENTO_POR_SERVICO"],
                    "CALC_FIXO_ADIANT_13_EVE_MENSAL": data_frame_rubricas_dominio.loc[i,"CALC_FIXO_ADIANT_13_EVE_MENSAL"],
                    "CALC_FIXO_ADIANT_13_MENSAL": data_frame_rubricas_dominio.loc[i,"CALC_FIXO_ADIANT_13_MENSAL"],
                    "CALC_FIXO_ADIANT_13_PROP_MENSAL": data_frame_rubricas_dominio.loc[i,"CALC_FIXO_ADIANT_13_PROP_MENSAL"],
                    "SOMA_MED_AFAST_41": data_frame_rubricas_dominio.loc[i,"SOMA_MED_AFAST_41"],
                    "CALC_AFAST_41": data_frame_rubricas_dominio.loc[i,"CALC_AFAST_41"],
                    "CALCULA_RATEIO_CONFORME_PERIODO_CADA_SERVICO": data_frame_rubricas_dominio.loc[i,"CALCULA_RATEIO_CONFORME_PERIODO_CADA_SERVICO"],
                    "CALCULAR_DIFERENCA_RUBRICA": data_frame_rubricas_dominio.loc[i,"CALCULAR_DIFERENCA_RUBRICA"],
                    "I_EVENTOS_DIFERENCA_VALOR": data_frame_rubricas_dominio.loc[i,"I_EVENTOS_DIFERENCA_VALOR"],
                    "SOMA_MED_AFAST_50": data_frame_rubricas_dominio.loc[i,"SOMA_MED_AFAST_50"],
                    "CALC_AFAST_50": data_frame_rubricas_dominio.loc[i,"CALC_AFAST_50"],
                    "GERAR_RUBRICA_SALDO_SALARIO_RESCISAO": data_frame_rubricas_dominio.loc[i,"GERAR_RUBRICA_SALDO_SALARIO_RESCISAO"],
                    "RUBRICA_SALDO_SALARIO_RESCISAO": data_frame_rubricas_dominio.loc[i,"RUBRICA_SALDO_SALARIO_RESCISAO"],
                    "CODIGO_INCIDENCIA_IRRF_ESOCIAL": data_frame_rubricas_dominio.loc[i,"CODIGO_INCIDENCIA_IRRF_ESOCIAL"],
                    "CODIGO_INCIDENCIA_INSS_ESOCIAL": data_frame_rubricas_dominio.loc[i,"CODIGO_INCIDENCIA_INSS_ESOCIAL"],
                    "SOMA_MED_AFAST_19": data_frame_rubricas_dominio.loc[i,"SOMA_MED_AFAST_19"],
                    "SOMA_MEDIA_LICENCA_PREMIO": data_frame_rubricas_dominio.loc[i,"SOMA_MEDIA_LICENCA_PREMIO"],
                    "SOMA_ADICIONAL_LICENCA_PREMIO": data_frame_rubricas_dominio.loc[i,"SOMA_ADICIONAL_LICENCA_PREMIO"],
                    "SOMA_MED_AFAST_35": data_frame_rubricas_dominio.loc[i,"SOMA_MED_AFAST_35"],
                    "CONSIDERAR_FALTAS_PARCIAIS_CALCULO_PROPORCIONAL": data_frame_rubricas_dominio.loc[i,"CONSIDERAR_FALTAS_PARCIAIS_CALCULO_PROPORCIONAL"],
                    "CONSIDERAR_FALTAS_DSR_CALCULO_PROPORCIONAL": data_frame_rubricas_dominio.loc[i,"CONSIDERAR_FALTAS_DSR_CALCULO_PROPORCIONAL"],
                    "CONSIDERAR_FALTAS_NOTURNAS_CALCULO_PROPORCIONAL": data_frame_rubricas_dominio.loc[i,"CONSIDERAR_FALTAS_NOTURNAS_CALCULO_PROPORCIONAL"],
                    "CODIGO_INCIDENCIA_FGTS_ESOCIAL": data_frame_rubricas_dominio.loc[i,"CODIGO_INCIDENCIA_FGTS_ESOCIAL"],
                    "SOMA_MED_AFAST_20": data_frame_rubricas_dominio.loc[i,"SOMA_MED_AFAST_20"],
                    "CODIGO_INCIDENCIA_SINDICAL_ESOCIAL": data_frame_rubricas_dominio.loc[i,"CODIGO_INCIDENCIA_SINDICAL_ESOCIAL"],
                    "SOMA_MED_AFAST_59": data_frame_rubricas_dominio.loc[i,"SOMA_MED_AFAST_59"],
                    "SOMA_MED_AFAST_60": data_frame_rubricas_dominio.loc[i,"SOMA_MED_AFAST_60"],
                    "CALC_AFAST_59": data_frame_rubricas_dominio.loc[i,"CALC_AFAST_59"],
                    "CALC_AFAST_60": data_frame_rubricas_dominio.loc[i,"CALC_AFAST_60"],
                    "UTILIZA_PARA_ESOCIAL_DOMESTICO": data_frame_rubricas_dominio.loc[i,"UTILIZA_PARA_ESOCIAL_DOMESTICO"],
                    "CODIGO_ESOCIAL_DOMESTICO": data_frame_rubricas_dominio.loc[i,"CODIGO_ESOCIAL_DOMESTICO"],
                    "aparece_relatorio": data_frame_rubricas_dominio.loc[i,"aparece_relatorio"],
                    "CODIGO_INCIDENCIA_RPPS_ESOCIAL": data_frame_rubricas_dominio.loc[i,"CODIGO_INCIDENCIA_RPPS_ESOCIAL"]
                }

        for i in range(len(data_frame_bases_rubricas_dominio)):
            if(int(data_frame_bases_rubricas_dominio.iloc[i,0])==empresa_rubricas):
                if data_frame_bases_rubricas_dominio.iloc[i,1] not in self.dicionario_bases_rubricas_esocial:
                    self.dicionario_bases_rubricas_esocial[data_frame_bases_rubricas_dominio.iloc[i,1]] = {}
                self.dicionario_bases_rubricas_esocial[data_frame_bases_rubricas_dominio.iloc[i,1]][data_frame_bases_rubricas_dominio.iloc[i,2]] = {
                    "i_eventos": data_frame_bases_rubricas_dominio.iloc[i,1],
                    "i_cadbases": data_frame_bases_rubricas_dominio.iloc[i,2],
                    "I_DADOS_EVENTOS_ESOCIAL": data_frame_bases_rubricas_dominio.iloc[i,3],
                    "I_LOTE_ESOCIAL": data_frame_bases_rubricas_dominio.iloc[i,4],
                    "STATUS_ESOCIAL": data_frame_bases_rubricas_dominio.iloc[i,5],
                    "ENVIAR_ESOCIAL": data_frame_bases_rubricas_dominio.iloc[i,6],
                    "INCLUSAO_VALIDADA_ESOCIAL": data_frame_bases_rubricas_dominio.iloc[i,7],
                    "GERAR_RETIFICACAO_ESOCIAL": data_frame_bases_rubricas_dominio.iloc[i,8],
                    "PROCESSAR_EXCLUSAO_ESOCIAL": data_frame_bases_rubricas_dominio.iloc[i,9],
                    "COMPANY_ID": data_frame_bases_rubricas_dominio.iloc[i,10]
                }

        for i in range(len(data_frame_formulas_dominio)):
            if(int(data_frame_formulas_dominio.iloc[i,0])==empresa_rubricas):
                self.dicionario_formulas_esocial[data_frame_formulas_dominio.iloc[i,1]] = {
                    "i_eventos": data_frame_formulas_dominio.iloc[i,1],
                    "script": data_frame_formulas_dominio.iloc[i,2],
                    "fil1": data_frame_formulas_dominio.iloc[i,3],
                    "fil2": data_frame_formulas_dominio.iloc[i,4],
                    "fil3": data_frame_formulas_dominio.iloc[i,5],
                    "fil4": data_frame_formulas_dominio.iloc[i,6],
                    "COMPANY_ID": data_frame_formulas_dominio.iloc[i,8]
                }

        #FOLANCAMENTOS_EVENTOS - Lançamento de movimentação
        #FOEVENTOS - Rubricas
        #FOEVENTOSBASES - Bases de cálculo das rubricas
        #FOFORMULAS - Fórmulas das rubricas
        #FOLANCTOMEDIAS - Lançamentos de rúbricas para médias

    def executar_extracao(self):
        print('Preparando XMLs dos eventos de rubrica do e-Social')

        arquivo_relacoes = open(f'{caminho_completo_pacotes}\classes\\relacao_rubricas.json')
        texto_relacoes = arquivo_relacoes.readline()
        arquivo_relacoes.close()
        dicionario_relacoes = json.loads(texto_relacoes)
        
        os.system(f'del /q {self.DIRETORIO_XML}')
        self.processa_arquivo('s1010')
        self.processa_arquivo('s1200')

        print('Extraindo informações')
        self.extrai_informacoes_xml()

        f = open(f'{self.DIRETORIO_XML}\s1010.json', "w")
        f.write(json.dumps(self.dicionario_s1010))
        f.close()

        f = open(f'{self.DIRETORIO_XML}\s1200.json', "w")
        f.write(json.dumps(self.dicionario_s1200))
        f.close()

        # Salva os dados extraídos do xml em txt para não precisar processar novamente
        f = open(f'{self.DIRETORIO_XML}\s1010.txt', "w")
        f.write("inscricao_empresa\tcodigo_rubrica\ttabela_rubrica\tinicio_validade\tfim_validade\tdescricao\tnatureza_rubrica\ttipo_rubrica\tincidencia_previdencia\tincidencia_irrf\tincidencia_fgts\tincidencia_rpps\tteto_remuneratorio\tobservacao\n")
        for s1010 in self.dicionario_s1010:
            f.write(f'{self.dicionario_s1010[s1010]["inscricao_empresa"]}\t{self.dicionario_s1010[s1010]["codigo_rubrica"]}\t{self.dicionario_s1010[s1010]["tabela_rubrica"]}\t{self.dicionario_s1010[s1010]["inicio_validade"]}\t{self.dicionario_s1010[s1010]["fim_validade"]}\t{self.dicionario_s1010[s1010]["descricao"]}\t{self.dicionario_s1010[s1010]["natureza_rubrica"]}\t{self.dicionario_s1010[s1010]["tipo_rubrica"]}\t{self.dicionario_s1010[s1010]["incidencia_previdencia"]}\t{self.dicionario_s1010[s1010]["incidencia_irrf"]}\t{self.dicionario_s1010[s1010]["incidencia_fgts"]}\t{self.dicionario_s1010[s1010]["incidencia_rpps"]}\t{self.dicionario_s1010[s1010]["teto_remuneratorio"]}\t{self.dicionario_s1010[s1010]["observacao"]}\n')
        f.close()

        f = open(f'{self.DIRETORIO_XML}\s1200.txt', "w")
        f.write("tipo_inscricao\tinscricao\tdata\tcpf\tlista_remuneracoes\trubrica\tquantidade\tvalor\n")
        for s1200 in self.dicionario_s1200:
            linha = ''
            linha = f'{self.dicionario_s1200[s1200]["tipo_inscricao"]}\t{self.dicionario_s1200[s1200]["inscricao"]}\t{self.dicionario_s1200[s1200]["data"]}\t{self.dicionario_s1200[s1200]["cpf"]}'
            for remuneracao in self.dicionario_s1200[s1200]["lista_remuneracoes"]:
                f.write(f'{linha}\t{self.dicionario_s1200[s1200]["lista_remuneracoes"][remuneracao]["rubrica"]}\t{self.dicionario_s1200[s1200]["lista_remuneracoes"][remuneracao]["quantidade"]}\t{self.dicionario_s1200[s1200]["lista_remuneracoes"][remuneracao]["valor"]}\n')
        f.close()

        print('Gerando planilha')
        self.gera_excel_relacao(dicionario_relacoes,self.CONVERSOR,self.DIRETORIO_XML)

    def processar_medias(self):
        data_frame_rubricas_relacionadas = pd.read_excel(f'{self.DIRETORIO_XML}\\relacao_rubricas.xlsx', sheet_name='Relacionado')
        data_frame_rubricas_multirelacionadas = pd.read_excel(f'{self.DIRETORIO_XML}\\relacao_rubricas.xlsx', sheet_name='+ de 1 result.')
        data_frame_rubricas_nao_relacionadas = pd.read_excel(f'{self.DIRETORIO_XML}\\relacao_rubricas.xlsx', sheet_name='Sem result.')
        data_frame_rubricas_duplicadas = pd.read_excel(f'{self.DIRETORIO_XML}\\relacao_rubricas.xlsx', sheet_name='Alerta')

        data_frame_parametros = pd.read_csv(f'{self.DIRETORIO_XML}\\FOPARMTO.txt', sep="\t")
        data_frame_s1010 = pd.read_csv(f'{self.DIRETORIO_XML}\\s1010.txt', sep="\t", encoding="ANSI")
        data_frame_s1200 = pd.read_csv(f'{self.DIRETORIO_XML}\\s1200.txt', sep="\t", encoding="ANSI")
            
        tabela_FOEVENTOS = []
        tabela_FOFORMULAS = []
        tabela_FOEVENTOSBASES = []
        tabela_FOLANCTOMEDIAS = []
        rubricas_impressas = []
        dicionario_rubricas_relacionadas = {}
        dicionario_rubricas_multirelacionadas = {}
        dicionario_rubricas_nao_relacionadas = {}
        dicionario_rubricas_duplicadas = {}
        dicionario_empresas = {}
        dicionario_empresas_padrao = {}
        dicionario_empregados = {}
        indice_codigo_empregado = 0
        indice_cpf_empregado = 0

        print('Carregando relações de Rubricas')

        for i in range(len(data_frame_s1010)):
            inscricao_empresa = data_frame_s1010.iloc[i,0]
            codigo_rubrica = data_frame_s1010.iloc[i,1]

            self.dicionario_s1010[f"{inscricao_empresa}-{codigo_rubrica}"] = {
                "inscricao_empresa": inscricao_empresa,
                "codigo_rubrica": codigo_rubrica,
                "tabela_rubrica": data_frame_s1010.iloc[i,2],
                "inicio_validade": data_frame_s1010.iloc[i,3],
                "fim_validade": data_frame_s1010.iloc[i,4],
                "descricao": data_frame_s1010.iloc[i,5],
                "natureza_rubrica": data_frame_s1010.iloc[i,6],
                "tipo_rubrica": data_frame_s1010.iloc[i,7],
                "incidencia_previdencia": data_frame_s1010.iloc[i,8],
                "incidencia_irrf": data_frame_s1010.iloc[i,9],
                "incidencia_fgts": data_frame_s1010.iloc[i,10],
                "incidencia_rpps": data_frame_s1010.iloc[i,11],
                "teto_remuneratorio": data_frame_s1010.iloc[i,12],
                "observacao": data_frame_s1010.iloc[i,13]
            }

        for i in range(len(data_frame_s1200)):
            tipo_inscricao = data_frame_s1200.iloc[i,0]
            inscricao = data_frame_s1200.iloc[i,1]
            data = data_frame_s1200.iloc[i,2]
            cpf = data_frame_s1200.iloc[i,3]
            rubrica = data_frame_s1200.iloc[i,4]
            quantidade = data_frame_s1200.iloc[i,5]
            valor = data_frame_s1200.iloc[i,6]

            if f"{inscricao}-{cpf}-{data}" not in self.dicionario_s1200:
                self.dicionario_s1200[f"{inscricao}-{cpf}-{data}"] = {
                    "tipo_inscricao": tipo_inscricao,
                    "inscricao": inscricao,
                    "data": data,
                    "cpf": cpf,
                    "lista_remuneracoes": {}
                }

            self.dicionario_s1200[f"{inscricao}-{cpf}-{data}"]["lista_remuneracoes"][rubrica] = {
                "rubrica": rubrica,
                "quantidade": quantidade,
                "valor": valor
            }

        for i in range(len(data_frame_parametros)):
            empresa = data_frame_parametros.iloc[i,0]
            empresa_referencia = data_frame_parametros.iloc[i,6]
            dicionario_empresas_padrao[empresa] = empresa_referencia
        
        for i in range(len(data_frame_rubricas_relacionadas)):
            if (data_frame_rubricas_relacionadas.loc[i,"Código Domínio"]!=""):
                acao = data_frame_rubricas_relacionadas.loc[i,'"X" para manter o relacionamento \nou \nInforme a rúbrica equivalente \nou \n"N" para cadastrar a rúbrica']
                dicionario_rubricas_relacionadas[data_frame_rubricas_relacionadas.loc[i,"Código"]] = {
                    "codi_emp": str(data_frame_rubricas_relacionadas.loc[i,"Código Domínio"]),
                    "nome": data_frame_rubricas_relacionadas.loc[i,"Descrição"],
                    "natureza_tributaria_rubrica": int(data_frame_rubricas_relacionadas.loc[i,"natureza_tributaria_rubrica"]),
                    "acao": (acao if (acao!="") else "X")
                }
                
        for i in range(len(data_frame_rubricas_multirelacionadas)):
            codi_emp = data_frame_rubricas_multirelacionadas.loc[i,'Informe a rúbrica equivalente \nou \n"N" para cadastrar a rúbrica']
            dicionario_rubricas_multirelacionadas[data_frame_rubricas_multirelacionadas.loc[i,"Código"]] = {
                "codi_emp": str(codi_emp),
                "nome": data_frame_rubricas_multirelacionadas.loc[i,"Descrição"],
                "natureza_tributaria_rubrica": int(data_frame_rubricas_multirelacionadas.loc[i,"natureza_tributaria_rubrica"])
            }
                
        for i in range(len(data_frame_rubricas_nao_relacionadas)):
            codi_emp = data_frame_rubricas_nao_relacionadas.loc[i,'Informe a rúbrica equivalente \nou \n"N" para cadastrar a rúbrica']
            dicionario_rubricas_nao_relacionadas[data_frame_rubricas_nao_relacionadas.loc[i,"Código"]] = {
                "codi_emp": str(codi_emp),
                "nome": data_frame_rubricas_nao_relacionadas.loc[i,"Descrição"],
                "natureza_tributaria_rubrica": int(data_frame_rubricas_nao_relacionadas.loc[i,"natureza_tributaria_rubrica"])
            }
                
        for i in range(len(data_frame_rubricas_duplicadas)):
            if (data_frame_rubricas_duplicadas.loc[i,"Código Domínio"]!=""):
                acao = data_frame_rubricas_duplicadas.loc[i,'"X" para somar as rúbricas \nou \n"D" para desconsiderar as rúbricas duplicadas \nou \nInforme a rúbrica equivalente \nou \n"N" para cadastrar a rúbrica']
                dicionario_rubricas_duplicadas[data_frame_rubricas_duplicadas.loc[i,"Código"]] = {
                    "codi_emp": str(data_frame_rubricas_duplicadas.loc[i,"Código Domínio"]),
                    "natureza_tributaria_rubrica": int(data_frame_rubricas_duplicadas.loc[i,"natureza_tributaria_rubrica"]),
                    "nome": data_frame_rubricas_duplicadas.loc[i,"Descrição"],
                    "acao": (acao if (acao!="") else "X")
                }

        arquivo_1200 = open(f'{self.DIRETORIO_XML}\s1200.json')
        texto_1200 = arquivo_1200.readline()
        arquivo_1200.close()
        self.dicionario_s1200 = json.loads(texto_1200)

        if os.path.isdir(f'{self.DIRETORIO_SAIDA}\\lay'):
            # A iteração pelos arquivos lay com o pandas não estava funcionando. Como o modelo lay será extinto, foi implementado com split
            with open(f'{self.DIRETORIO_SAIDA}\\lay\\GEEMPRE.txt') as lay_empresas:
                for line in lay_empresas:
                    linha = line.replace("\n","")
                    if(linha in ["GEEMPRE,empresas.txt",""]): continue
                    
                    if (line.split("\t")[1]=="codi_emp"):
                        indice_codigo_empresa = int(line.split("\t")[2])-1
                    elif (line.split("\t")[1]=="cgce_emp"):
                        indice_cgc_empresa = int(line.split("\t")[2])-1

            with open(f'{self.DIRETORIO_SAIDA}\\lay\\FOEMPREGADOS.txt') as lay_empregados:
                for line in lay_empregados:
                    linha = line.replace("\n","")
                    if(linha in ["FOEMPREGADOS,empregados.txt",""]): continue
                    
                    if (line.split("\t")[1]=="codi_emp"):
                        indice_codigo_empresa_empregado = int(line.split("\t")[2])-1
                    elif (line.split("\t")[1]=="i_empregados"):
                        indice_codigo_empregado = int(line.split("\t")[2])-1
                    elif (line.split("\t")[1]=="cpf"):
                        indice_cpf_empregado = int(line.split("\t")[2])-1

            arquivo_empresas = f'{self.DIRETORIO_SAIDA}\\empresas.txt'
            arquivo_empregados = f'{self.DIRETORIO_SAIDA}\\empregados.txt'
            
        else:
            indice_codigo_empresa = 11
            indice_cgc_empresa = 5

            indice_codigo_empresa_empregado = 1
            indice_codigo_empregado = 2
            indice_cpf_empregado = 33

            arquivo_empresas = f'{self.DIRETORIO_SAIDA}\\GEEMPRE.txt'
            arquivo_empregados = f'{self.DIRETORIO_SAIDA}\\FOEMPREGADOS.txt'
        
        data_frame_empresas = pd.read_table(arquivo_empresas,encoding='ANSI',low_memory=False)
        data_frame_empregados = pd.read_table(arquivo_empregados,encoding='ANSI',low_memory=False)
        
        for i in range(len(data_frame_empresas)):
            codigo_empresa = data_frame_empresas.iloc[i,indice_codigo_empresa]
            cgc_empresa = str(data_frame_empresas.iloc[i,indice_cgc_empresa])

            dicionario_empresas[cgc_empresa] = codigo_empresa
        
        for i in range(len(data_frame_empregados)):
            codigo_empresa_empregado = data_frame_empregados.iloc[i,indice_codigo_empresa_empregado]
            cpf_empregado = str(data_frame_empregados.iloc[i,indice_cpf_empregado])
            codigo_empregado = data_frame_empregados.iloc[i,indice_codigo_empregado]

            dicionario_empregados[f'{codigo_empresa_empregado}-{cpf_empregado}'] = codigo_empregado

        linhas_impressao = {}
        for s1200 in self.dicionario_s1200:
            codi_emp = ""
            i_empregados = ""

            if (self.dicionario_s1200[s1200]["tipo_inscricao"]=="1"):
                codi_emp = dicionario_empresas.get(self.completar_cnpj(self.dicionario_s1200[s1200]["inscricao"]))
                i_empregados = dicionario_empregados.get(f'{codi_emp}-{str(self.dicionario_s1200[s1200]["cpf"])}')
            else:
                codi_emp = dicionario_empresas.get(self.dicionario_s1200[s1200]["inscricao"])
                i_empregados = dicionario_empregados.get(f'{codi_emp}-{str(self.dicionario_s1200[s1200]["cpf"])}')

            if(codi_emp==None): continue

            for rubrica in self.dicionario_s1200[s1200]["lista_remuneracoes"]:
                try:
                    natureza = ""
                    nome = ""
                    rubrica_dominio = False
                    novo_codigo = False

                    if(int(rubrica) in dicionario_rubricas_nao_relacionadas):
                        if(dicionario_rubricas_nao_relacionadas[int(rubrica)]["codi_emp"]!="N")|(dicionario_rubricas_nao_relacionadas[int(rubrica)]["codi_emp"]==""):
                            rubrica_dominio = int(dicionario_rubricas_nao_relacionadas[int(rubrica)])
                        elif(dicionario_rubricas_nao_relacionadas[int(rubrica)]["codi_emp"]=="N"):
                            natureza = dicionario_rubricas_multirelacionadas[int(rubrica)]["natureza_tributaria_rubrica"]
                            nome = dicionario_rubricas_multirelacionadas[int(rubrica)]["nome"]
                            novo_codigo = self.atribui_nova_rubrica(rubrica,natureza)
                            
                            if novo_codigo:
                                rubrica_dominio = novo_codigo
                        else:
                            pass # Ignora linhas com a coluna de ação em branco

                    elif(int(rubrica) in dicionario_rubricas_multirelacionadas):
                        if(dicionario_rubricas_multirelacionadas[int(rubrica)]["codi_emp"]!="N")&(dicionario_rubricas_multirelacionadas[int(rubrica)]["codi_emp"]!=""):
                            if(int(rubrica) not in dicionario_rubricas_duplicadas):
                                try:
                                    rubrica_dominio = int(dicionario_rubricas_multirelacionadas[int(rubrica)]["codi_emp"])
                                except ValueError:
                                    pass
                            elif(dicionario_rubricas_duplicadas[int(rubrica)]["codi_emp"]==dicionario_rubricas_multirelacionadas[int(rubrica)]["codi_emp"]):
                                if(dicionario_rubricas_duplicadas[int(rubrica)]["acao"]=="X"):
                                    rubrica_dominio = dicionario_rubricas_duplicadas[int(rubrica)]["codi_emp"]
                                elif(dicionario_rubricas_duplicadas[int(rubrica)]["acao"]=="D")|(dicionario_rubricas_duplicadas[int(rubrica)]["acao"]==""):
                                    pass # Desconsidera registros com esta opção
                                elif(dicionario_rubricas_duplicadas[int(rubrica)]["acao"]=="N"):
                                    natureza = dicionario_rubricas_multirelacionadas[int(rubrica)]["natureza_tributaria_rubrica"]
                                    nome = dicionario_rubricas_multirelacionadas[int(rubrica)]["nome"]
                                    novo_codigo = self.atribui_nova_rubrica(rubrica,natureza)
                                    
                                    if novo_codigo:
                                        rubrica_dominio = novo_codigo
                                else:
                                    rubrica_dominio = dicionario_rubricas_duplicadas[int(rubrica)]["acao"]
                            else:
                                try:
                                    rubrica_dominio = int(dicionario_rubricas_multirelacionadas[int(rubrica)]["codi_emp"])
                                except ValueError:
                                    pass
                        else:
                            if(dicionario_rubricas_duplicadas[int(rubrica)]["acao"]=="X"):
                                valor = dicionario_rubricas_multirelacionadas[int(rubrica)]["codi_emp"]
                                if(valor=="N"):
                                    natureza = dicionario_rubricas_multirelacionadas[int(rubrica)]["natureza_tributaria_rubrica"]
                                    nome = dicionario_rubricas_multirelacionadas[int(rubrica)]["nome"]
                                    novo_codigo = self.atribui_nova_rubrica(rubrica,natureza)
                                    
                                    if novo_codigo:
                                        rubrica_dominio = novo_codigo
                                else:
                                    rubrica_dominio = int(dicionario_rubricas_multirelacionadas[int(rubrica)]["codi_emp"])
                            elif(dicionario_rubricas_duplicadas[int(rubrica)]["acao"]=="N"):
                                natureza = dicionario_rubricas_multirelacionadas[int(rubrica)]["natureza_tributaria_rubrica"]
                                nome = dicionario_rubricas_multirelacionadas[int(rubrica)]["nome"]
                                novo_codigo = self.atribui_nova_rubrica(rubrica,natureza)
                                
                                if novo_codigo:
                                    rubrica_dominio = novo_codigo
                            elif(dicionario_rubricas_duplicadas[int(rubrica)]["acao"]=="D"):
                                pass # Desconsidera registros com essa opção

                    elif(int(rubrica) in dicionario_rubricas_relacionadas):
                        if(int(rubrica) not in dicionario_rubricas_duplicadas):
                            if(dicionario_rubricas_relacionadas[int(rubrica)]["acao"]=="X"):
                                rubrica_dominio = int(dicionario_rubricas_relacionadas[int(rubrica)]["codi_emp"])
                            elif(dicionario_rubricas_relacionadas[int(rubrica)]["acao"]=="N"):
                                natureza = dicionario_rubricas_relacionadas[int(rubrica)]["natureza_tributaria_rubrica"]
                                nome = dicionario_rubricas_relacionadas[int(rubrica)]["nome"]
                                novo_codigo = self.atribui_nova_rubrica(rubrica,natureza)
                                
                                if novo_codigo:
                                    rubrica_dominio = novo_codigo
                            elif(dicionario_rubricas_relacionadas[int(rubrica)]["acao"]!=""):
                                rubrica_dominio = int(dicionario_rubricas_relacionadas[int(rubrica)]["acao"])
                        else:
                            if(dicionario_rubricas_duplicadas[int(rubrica)]["acao"]=="X"):
                                valor = dicionario_rubricas_relacionadas[int(rubrica)]["codi_emp"]
                                if(valor=="N"):
                                    natureza = dicionario_rubricas_relacionadas[int(rubrica)]["natureza_tributaria_rubrica"]
                                    nome = dicionario_rubricas_relacionadas[int(rubrica)]["nome"]
                                    novo_codigo = self.atribui_nova_rubrica(rubrica,natureza)
                                    
                                    if novo_codigo:
                                        rubrica_dominio = novo_codigo
                                else:
                                    rubrica_dominio = int(dicionario_rubricas_relacionadas[int(rubrica)]["codi_emp"])
                            elif(dicionario_rubricas_duplicadas[int(rubrica)]["acao"]=="N"):
                                natureza = dicionario_rubricas_relacionadas[int(rubrica)]["natureza_tributaria_rubrica"]
                                nome = dicionario_rubricas_relacionadas[int(rubrica)]["nome"]
                                novo_codigo = self.atribui_nova_rubrica(rubrica,natureza)
                                
                                if novo_codigo:
                                    rubrica_dominio = novo_codigo
                            elif(dicionario_rubricas_duplicadas[int(rubrica)]["acao"]=="D")|(dicionario_rubricas_duplicadas[int(rubrica)]["acao"]==''):
                                pass # Desconsidera registros com essa opção
                            else:
                                rubrica_dominio = int(dicionario_rubricas_duplicadas[int(rubrica)]["acao"])

                    if novo_codigo:
                        corpo_padrao = self.preenchimento_padrao_por_natureza(natureza)
                        media_13 = corpo_padrao["soma_med_13"]
                        media_ferias = corpo_padrao["soma_med_fer"]
                        tipo_inf = corpo_padrao["tipo_inf"]
                    else:
                        media_13 = (self.dicionario_rubricas_esocial[rubrica_dominio]["soma_med_13"] if rubrica_dominio else 'N')
                        media_ferias = (self.dicionario_rubricas_esocial[rubrica_dominio]["soma_med_fer"] if rubrica_dominio else 'N')
                        tipo_inf = (self.dicionario_rubricas_esocial[rubrica_dominio]["tipo_inf"] if rubrica_dominio else 'N')
                        
                    quantidade = self.dicionario_s1200[s1200]["lista_remuneracoes"][rubrica]["quantidade"]
                    quantidade = (0 if quantidade=="NULO" else float(quantidade))
                    valor = float(self.dicionario_s1200[s1200]["lista_remuneracoes"][rubrica]["valor"])
                    data = self.dicionario_s1200[s1200]["data"]
                    
                    if((media_13=='S')|(media_ferias=='S')):
                        if(f'{codi_emp}-{i_empregados}-{rubrica_dominio}-{data}' in linhas_impressao.keys()):
                            quantidade_anterior = linhas_impressao[f'{codi_emp}-{i_empregados}-{rubrica_dominio}-{data}']["quantidade"]
                            valor_anterior = linhas_impressao[f'{codi_emp}-{i_empregados}-{rubrica_dominio}-{data}']["valor"]

                            linhas_impressao[f'{codi_emp}-{i_empregados}-{rubrica_dominio}-{data}']["quantidade"] = quantidade_anterior + quantidade
                            linhas_impressao[f'{codi_emp}-{i_empregados}-{rubrica_dominio}-{data}']["valor"] = valor_anterior + valor
                        else:
                            linhas_impressao[f'{codi_emp}-{i_empregados}-{rubrica_dominio}-{data}'] = {
                                "codi_emp": codi_emp,
                                "i_empregados": i_empregados,
                                "rubrica_dominio": rubrica_dominio,
                                "data": data,
                                "quantidade": quantidade,
                                "valor": valor,
                                "nome": nome,
                                "natureza": natureza,
                                "tipo_inf": tipo_inf
                            }
                except KeyError:
                    pass
            
        for linha in linhas_impressao:
            codi_emp = linhas_impressao[linha]["codi_emp"]
            codi_emp_rubrica = codi_emp
            i_empregados = linhas_impressao[linha]["i_empregados"]
            rubrica_dominio = linhas_impressao[linha]["rubrica_dominio"]
            quantidade = linhas_impressao[linha]["quantidade"]
            valor = linhas_impressao[linha]["valor"]
            data = linhas_impressao[linha]["data"]
            natureza = linhas_impressao[linha]["natureza"]
            nome = linhas_impressao[linha]["nome"]
            tipo_inf = linhas_impressao[linha]["tipo_inf"]

            if int(codi_emp) in dicionario_empresas_padrao.keys():
                codi_emp_rubrica = dicionario_empresas_padrao[codi_emp]
            else:
                codi_emp_rubrica = codi_emp
                
            rubricas_proprias = codi_emp_rubrica<9995
            rubricas_empresas_modelo = (codi_emp_rubrica>9995)&(int(rubrica_dominio>200))&(int(rubrica_dominio<250))
                
            if (rubricas_proprias|rubricas_empresas_modelo):
                if(f'{codi_emp}-{rubrica_dominio}' not in rubricas_impressas):
                    tableE = Table('FOEVENTOS')
                    tableE.set_value('CODI_EMP', codi_emp_rubrica)
                    tableE.set_value('I_EVENTOS', rubrica_dominio)

                    if rubrica_dominio in self.rubricas_novas:
                        dados_rubricas = self.preenchimento_padrao_por_natureza(natureza)

                        tableE.set_value('NOME', nome)
                        tableE.set_value('SOMA_MED_13', dados_rubricas["soma_med_13"])
                        tableE.set_value('SOMA_MED_FER', dados_rubricas["soma_med_fer"])
                        tableE.set_value('TAXA', dados_rubricas["taxa"])
                        tableE.set_value('PROV_DESC', dados_rubricas["prov_desc"])
                        tableE.set_value('TIPO_INF', dados_rubricas["tipo_inf"])
                        tableE.set_value('TIPO_BASE', dados_rubricas["tipo_base"])
                        tableE.set_value('BASE_IRRF', dados_rubricas["base_irrf"])
                        tableE.set_value('BASE_INSS', dados_rubricas["base_inss"])
                        tableE.set_value('BASE_FGTS', dados_rubricas["base_fgts"])
                        tableE.set_value('BASE_SINDICATO', dados_rubricas["base_sindicato"])
                        tableE.set_value('BASE_HEXTRA', dados_rubricas["base_hextra"])
                        tableE.set_value('BASE_PERICULOSIDADE', dados_rubricas["base_periculosidade"])
                        tableE.set_value('BASE_AUX1', dados_rubricas["base_aux1"])
                        tableE.set_value('BASE_AUX2', dados_rubricas["base_aux2"])
                        tableE.set_value('BASE_AUX3', dados_rubricas["base_aux3"])
                        tableE.set_value('HORAS_MES', dados_rubricas["horas_mes"])
                        tableE.set_value('COMP_13FER', dados_rubricas["comp_13fer"])
                        tableE.set_value('SOMA_FIC_FIN', dados_rubricas["soma_fic_fin"])
                        tableE.set_value('SOMA_RAIS', dados_rubricas["soma_rais"])
                        tableE.set_value('SOMA_INF_REN', dados_rubricas["soma_inf_ren"])
                        tableE.set_value('PAGA_PROP', dados_rubricas["paga_prop"])
                        tableE.set_value('APARECE_RECIBO', dados_rubricas["aparece_recibo"])
                        tableE.set_value('SOMA_SAL_BASE', dados_rubricas["soma_sal_base"])
                        tableE.set_value('ORDEM_CALCULO', dados_rubricas["ordem_calculo"])
                        tableE.set_value('CLASSIFICACAO', dados_rubricas["classificacao"])
                        tableE.set_value('REND_TRIBUTAVEIS', dados_rubricas["rend_tributaveis"])
                        tableE.set_value('REND_ISENTOS', dados_rubricas["rend_isentos"])
                        tableE.set_value('REND_SUJEITOS', dados_rubricas["rend_sujeitos"])
                        tableE.set_value('BASE_PIS', dados_rubricas["base_pis"])
                        tableE.set_value('REND_ADICIONAIS', dados_rubricas["rend_adicionais"])
                        tableE.set_value('BASE_RDSR', dados_rubricas["base_rdsr"])
                        tableE.set_value('BASE_RDSR_EVE', dados_rubricas["base_rdsr_eve"])
                        tableE.set_value('SOMA_MED_AFAST', dados_rubricas["soma_med_afast"])
                        tableE.set_value('SOMA_MED_AFAST_02', dados_rubricas["soma_med_afast_02"])
                        tableE.set_value('SOMA_MED_AFAST_03', dados_rubricas["soma_med_afast_03"])
                        tableE.set_value('SOMA_MED_AFAST_04', dados_rubricas["soma_med_afast_04"])
                        tableE.set_value('SOMA_MED_AFAST_05', dados_rubricas["soma_med_afast_05"])
                        tableE.set_value('SOMA_MED_AFAST_06', dados_rubricas["soma_med_afast_06"])
                        tableE.set_value('SOMA_MED_AFAST_07', dados_rubricas["soma_med_afast_07"])
                        tableE.set_value('SOMA_MED_AFAST_13', dados_rubricas["soma_med_afast_13"])
                        tableE.set_value('SOMA_MED_AFAST_14', dados_rubricas["soma_med_afast_14"])
                        tableE.set_value('SOMA_MED_AFAST_24', dados_rubricas["soma_med_afast_24"])
                        tableE.set_value('I_CADBASES', dados_rubricas["i_cadbases"])
                        tableE.set_value('CALC_AFAST', dados_rubricas["calc_afast"])
                        tableE.set_value('ADIC_AFAST', dados_rubricas["adic_afast"])
                        tableE.set_value('I_HORASAULA', dados_rubricas["i_horasaula"])
                        tableE.set_value('CALC_AFAST_02', dados_rubricas["CALC_AFAST_02"])
                        tableE.set_value('CALC_AFAST_03', dados_rubricas["CALC_AFAST_03"])
                        tableE.set_value('CALC_AFAST_04', dados_rubricas["CALC_AFAST_04"])
                        tableE.set_value('CALC_AFAST_05', dados_rubricas["CALC_AFAST_05"])
                        tableE.set_value('CALC_AFAST_06', dados_rubricas["CALC_AFAST_06"])
                        tableE.set_value('CALC_AFAST_07', dados_rubricas["CALC_AFAST_07"])
                        tableE.set_value('CALC_AFAST_13', dados_rubricas["CALC_AFAST_13"])
                        tableE.set_value('CALC_AFAST_14', dados_rubricas["CALC_AFAST_14"])
                        tableE.set_value('CALC_AFAST_24', dados_rubricas["CALC_AFAST_24"])
                        tableE.set_value('CALC_FIXO_FER', dados_rubricas["CALC_FIXO_FER"])
                        tableE.set_value('CALC_FIXO_FER_EVE', dados_rubricas["CALC_FIXO_FER_EVE"])
                        tableE.set_value('CALC_FIXO_FER_PROP_MES', dados_rubricas["CALC_FIXO_FER_PROP_MES"])
                        tableE.set_value('CALC_FIXO_FER_PROP_FER', dados_rubricas["CALC_FIXO_FER_PROP_FER"])
                        tableE.set_value('CALC_FIXO_13', dados_rubricas["CALC_FIXO_13"])
                        tableE.set_value('CALC_FIXO_13_EVE', dados_rubricas["CALC_FIXO_13_EVE"])
                        tableE.set_value('HOMOLOGNET', dados_rubricas["HOMOLOGNET"])
                        tableE.set_value('RUBRICA', dados_rubricas["RUBRICA"])
                        tableE.set_value('CODI_RUBRICA', dados_rubricas["CODI_RUBRICA"])
                        tableE.set_value('EMITIR_TERMO_RESCISAO', dados_rubricas["EMITIR_TERMO_RESCISAO"])
                        tableE.set_value('CAMPO_TERMO_RESCISAO', dados_rubricas["CAMPO_TERMO_RESCISAO"])
                        tableE.set_value('REND_ISENTOS_DESCRICAO', dados_rubricas["REND_ISENTOS_DESCRICAO"])
                        tableE.set_value('REND_SUJEITOS_DESCRICAO', dados_rubricas["REND_SUJEITOS_DESCRICAO"])
                        tableE.set_value('SOMA_MED_AFAST_26', dados_rubricas["SOMA_MED_AFAST_26"])
                        tableE.set_value('CALC_AFAST_26', dados_rubricas["CALC_AFAST_26"])
                        tableE.set_value('CORRIGE_MEDIA', dados_rubricas["CORRIGE_MEDIA"])
                        tableE.set_value('TIPO_CALCULO', dados_rubricas["TIPO_CALCULO"])
                        tableE.set_value('CALC_FIXO_13_DESC_ADIANT_13', dados_rubricas["CALC_FIXO_13_DESC_ADIANT_13"])
                        tableE.set_value('CALC_FIXO_ADIANT_13', dados_rubricas["CALC_FIXO_ADIANT_13"])
                        tableE.set_value('CALC_FIXO_ADIANT_13_EVE', dados_rubricas["CALC_FIXO_ADIANT_13_EVE"])
                        tableE.set_value('CALC_FIXO_ADIANT_13_PROP', dados_rubricas["CALC_FIXO_ADIANT_13_PROP"])
                        tableE.set_value('SOMA_MEDIA_AVISO_PREVIO', dados_rubricas["SOMA_MEDIA_AVISO_PREVIO"])
                        tableE.set_value('SOMA_ADICIONAL_AVISO_PREVIO', dados_rubricas["SOMA_ADICIONAL_AVISO_PREVIO"])
                        tableE.set_value('SOMA_MED_AFAST_32', dados_rubricas["SOMA_MED_AFAST_32"])
                        tableE.set_value('COMPOE_CAMPO_23_TERMO_RESCISAO', dados_rubricas["COMPOE_CAMPO_23_TERMO_RESCISAO"])
                        tableE.set_value('SOMA_MEDIA_SALDO_SALARIO', dados_rubricas["SOMA_MEDIA_SALDO_SALARIO"])
                        tableE.set_value('DESCONTA_DSR', dados_rubricas["DESCONTA_DSR"])
                        tableE.set_value('DESCONTA_DSR_EVENTO', dados_rubricas["DESCONTA_DSR_EVENTO"])
                        tableE.set_value('COMPOE_ADIANTAMENTO_SALARIAL', dados_rubricas["COMPOE_ADIANTAMENTO_SALARIAL"])
                        tableE.set_value('COMPOE_LIQUIDO', dados_rubricas["COMPOE_LIQUIDO"])
                        tableE.set_value('TIPO_CONSIDERACAO_CAMPO_23_TERMO_RESCISAO', dados_rubricas["TIPO_CONSIDERACAO_CAMPO_23_TERMO_RESCISAO"])
                        tableE.set_value('CALC_AFAST_35', dados_rubricas["CALC_AFAST_35"])
                        tableE.set_value('DATA_INICIO', dados_rubricas["DATA_INICIO"])
                        tableE.set_value('SITUACAO', dados_rubricas["SITUACAO"])
                        tableE.set_value('DATA_INATIVACAO', dados_rubricas["DATA_INATIVACAO"])
                        tableE.set_value('NATUREZA_FOLHA_MENSAL', dados_rubricas["NATUREZA_FOLHA_MENSAL"])
                        tableE.set_value('NATUREZA_13_INTEGRAL', dados_rubricas["NATUREZA_13_INTEGRAL"])
                        tableE.set_value('POSSUI_PROCESSO_REFERENTE_SUSPENSAO_INCIDENCIA_ENCARGOS', dados_rubricas["POSSUI_PROCESSO_REFERENTE_SUSPENSAO_INCIDENCIA_ENCARGOS"])
                        tableE.set_value('POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_PATRONAL', dados_rubricas["POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_PATRONAL"])
                        tableE.set_value('CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_PATRONAL', dados_rubricas["CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_PATRONAL"])
                        tableE.set_value('POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_EMPREGADOS', dados_rubricas["POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_EMPREGADOS"])
                        tableE.set_value('CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_EMPREGADOS', dados_rubricas["CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_EMPREGADOS"])
                        tableE.set_value('POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_FGTS', dados_rubricas["POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_FGTS"])
                        tableE.set_value('CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_FGTS', dados_rubricas["CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_FGTS"])
                        tableE.set_value('POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_IRRF', dados_rubricas["POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_IRRF"])
                        tableE.set_value('CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_IRRF', dados_rubricas["CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_IRRF"])
                        tableE.set_value('POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_SINDICAL', dados_rubricas["POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_SINDICAL"])
                        tableE.set_value('CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_SINDICAL', dados_rubricas["CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_SINDICAL"])
                        tableE.set_value('PERMITE_INFORMAR_NATUREZA_FOLHA_MENSAL', dados_rubricas["PERMITE_INFORMAR_NATUREZA_FOLHA_MENSAL"])
                        tableE.set_value('PERMITE_INFORMAR_NATUREZA_13_INTEGRAL', dados_rubricas["PERMITE_INFORMAR_NATUREZA_13_INTEGRAL"])
                        tableE.set_value('CODIGO_ESOCIAL', rubrica_dominio)
                        tableE.set_value('CONSIDERAR_FALTAS_PAGAMENTO_PROPORCIONAL', dados_rubricas["CONSIDERAR_FALTAS_PAGAMENTO_PROPORCIONAL"])
                        tableE.set_value('CALCULA_DIFERENCA_ALTERACAO_PISO_SALARIAL', dados_rubricas["CALCULA_DIFERENCA_ALTERACAO_PISO_SALARIAL"])
                        tableE.set_value('I_EVENTOS_DIFERENCA_PISO_SALARIAL', dados_rubricas["I_EVENTOS_DIFERENCA_PISO_SALARIAL"])
                        tableE.set_value('PERMITE_CALCULAR_DIFERENCA_PISO_SALARIAL', dados_rubricas["PERMITE_CALCULAR_DIFERENCA_PISO_SALARIAL"])
                        tableE.set_value('CALC_AFAST_39', dados_rubricas["CALC_AFAST_39"])
                        tableE.set_value('TIPO_VALOR_CONSIDERAR_CALCULO_MEDIAS', dados_rubricas["TIPO_VALOR_CONSIDERAR_CALCULO_MEDIAS"])
                        tableE.set_value('DETALHAR_LANCAMENTO_POR_SERVICO', dados_rubricas["DETALHAR_LANCAMENTO_POR_SERVICO"])
                        tableE.set_value('CALC_FIXO_ADIANT_13_EVE_MENSAL', dados_rubricas["CALC_FIXO_ADIANT_13_EVE_MENSAL"])
                        tableE.set_value('CALC_FIXO_ADIANT_13_MENSAL', dados_rubricas["CALC_FIXO_ADIANT_13_MENSAL"])
                        tableE.set_value('CALC_FIXO_ADIANT_13_PROP_MENSAL', dados_rubricas["CALC_FIXO_ADIANT_13_PROP_MENSAL"])
                        tableE.set_value('SOMA_MED_AFAST_41', dados_rubricas["SOMA_MED_AFAST_41"])
                        tableE.set_value('CALC_AFAST_41', dados_rubricas["CALC_AFAST_41"])
                        tableE.set_value('CALCULA_RATEIO_CONFORME_PERIODO_CADA_SERVICO', dados_rubricas["CALCULA_RATEIO_CONFORME_PERIODO_CADA_SERVICO"])
                        tableE.set_value('CALCULAR_DIFERENCA_RUBRICA', dados_rubricas["CALCULAR_DIFERENCA_RUBRICA"])
                        tableE.set_value('I_EVENTOS_DIFERENCA_VALOR', dados_rubricas["I_EVENTOS_DIFERENCA_VALOR"])
                        tableE.set_value('SOMA_MED_AFAST_50', dados_rubricas["SOMA_MED_AFAST_50"])
                        tableE.set_value('CALC_AFAST_50', dados_rubricas["CALC_AFAST_50"])
                        tableE.set_value('GERAR_RUBRICA_SALDO_SALARIO_RESCISAO', dados_rubricas["GERAR_RUBRICA_SALDO_SALARIO_RESCISAO"])
                        tableE.set_value('RUBRICA_SALDO_SALARIO_RESCISAO', dados_rubricas["RUBRICA_SALDO_SALARIO_RESCISAO"])
                        tableE.set_value('CODIGO_INCIDENCIA_IRRF_ESOCIAL', dados_rubricas["CODIGO_INCIDENCIA_IRRF_ESOCIAL"])
                        tableE.set_value('CODIGO_INCIDENCIA_INSS_ESOCIAL', dados_rubricas["CODIGO_INCIDENCIA_INSS_ESOCIAL"])
                        tableE.set_value('SOMA_MED_AFAST_19', dados_rubricas["SOMA_MED_AFAST_19"])
                        tableE.set_value('SOMA_MEDIA_LICENCA_PREMIO', dados_rubricas["SOMA_MEDIA_LICENCA_PREMIO"])
                        tableE.set_value('SOMA_ADICIONAL_LICENCA_PREMIO', dados_rubricas["SOMA_ADICIONAL_LICENCA_PREMIO"])
                        tableE.set_value('SOMA_MED_AFAST_35', dados_rubricas["SOMA_MED_AFAST_35"])
                        tableE.set_value('CONSIDERAR_FALTAS_PARCIAIS_CALCULO_PROPORCIONAL', dados_rubricas["CONSIDERAR_FALTAS_PARCIAIS_CALCULO_PROPORCIONAL"])
                        tableE.set_value('CONSIDERAR_FALTAS_DSR_CALCULO_PROPORCIONAL', dados_rubricas["CONSIDERAR_FALTAS_DSR_CALCULO_PROPORCIONAL"])
                        tableE.set_value('CONSIDERAR_FALTAS_NOTURNAS_CALCULO_PROPORCIONAL', dados_rubricas["CONSIDERAR_FALTAS_NOTURNAS_CALCULO_PROPORCIONAL"])
                        tableE.set_value('CODIGO_INCIDENCIA_FGTS_ESOCIAL', dados_rubricas["CODIGO_INCIDENCIA_FGTS_ESOCIAL"])
                        tableE.set_value('SOMA_MED_AFAST_20', dados_rubricas["SOMA_MED_AFAST_20"])
                        tableE.set_value('CODIGO_INCIDENCIA_SINDICAL_ESOCIAL', dados_rubricas["CODIGO_INCIDENCIA_SINDICAL_ESOCIAL"])
                        tableE.set_value('SOMA_MED_AFAST_59', dados_rubricas["SOMA_MED_AFAST_59"])
                        tableE.set_value('SOMA_MED_AFAST_60', dados_rubricas["SOMA_MED_AFAST_60"])
                        tableE.set_value('CALC_AFAST_59', dados_rubricas["CALC_AFAST_59"])
                        tableE.set_value('CALC_AFAST_60', dados_rubricas["CALC_AFAST_60"])
                        tableE.set_value('UTILIZA_PARA_ESOCIAL_DOMESTICO', dados_rubricas["UTILIZA_PARA_ESOCIAL_DOMESTICO"])
                        tableE.set_value('CODIGO_ESOCIAL_DOMESTICO', dados_rubricas["CODIGO_ESOCIAL_DOMESTICO"])
                        tableE.set_value('aparece_relatorio', dados_rubricas["aparece_relatorio"])
                        tableE.set_value('CODIGO_INCIDENCIA_RPPS_ESOCIAL', dados_rubricas["CODIGO_INCIDENCIA_RPPS_ESOCIAL"])
                        tableE.set_value('ORIGEM_REG', "1")

                        formula = self.dicionario_formulas_esocial[dados_rubricas['i_eventos']]

                        for base in self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']]:
                            tableEB = Table('FOEVENTOSBASES')
                            tableEB.set_value('codi_emp', codi_emp_rubrica)
                            tableEB.set_value('i_eventos',rubrica_dominio)
                            tableEB.set_value('i_cadbases',self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']][base]["i_cadbases"])
                            tableEB.set_value('I_DADOS_EVENTOS_ESOCIAL',self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']][base]["I_DADOS_EVENTOS_ESOCIAL"])
                            tableEB.set_value('I_LOTE_ESOCIAL',self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']][base]["I_LOTE_ESOCIAL"])
                            tableEB.set_value('STATUS_ESOCIAL',self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']][base]["STATUS_ESOCIAL"])
                            tableEB.set_value('ENVIAR_ESOCIAL',self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']][base]["ENVIAR_ESOCIAL"])
                            tableEB.set_value('INCLUSAO_VALIDADA_ESOCIAL',self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']][base]["INCLUSAO_VALIDADA_ESOCIAL"])
                            tableEB.set_value('GERAR_RETIFICACAO_ESOCIAL',self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']][base]["GERAR_RETIFICACAO_ESOCIAL"])
                            tableEB.set_value('PROCESSAR_EXCLUSAO_ESOCIAL',self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']][base]["PROCESSAR_EXCLUSAO_ESOCIAL"])
                            tableEB.set_value('COMPANY_ID',self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']][base]["COMPANY_ID"])

                            tabela_FOEVENTOSBASES.append(tableEB.do_output())
                    else:
                        tableE.set_value('NOME', self.dicionario_rubricas_esocial[rubrica_dominio]["nome"])
                        tableE.set_value('SOMA_MED_13', self.dicionario_rubricas_esocial[rubrica_dominio]["soma_med_13"])
                        tableE.set_value('SOMA_MED_FER', self.dicionario_rubricas_esocial[rubrica_dominio]["soma_med_fer"])
                        tableE.set_value('TAXA', self.dicionario_rubricas_esocial[rubrica_dominio]["taxa"])
                        tableE.set_value('PROV_DESC', self.dicionario_rubricas_esocial[rubrica_dominio]["prov_desc"])
                        tableE.set_value('TIPO_INF', self.dicionario_rubricas_esocial[rubrica_dominio]["tipo_inf"])
                        tableE.set_value('TIPO_BASE', self.dicionario_rubricas_esocial[rubrica_dominio]["tipo_base"])
                        tableE.set_value('BASE_IRRF', self.dicionario_rubricas_esocial[rubrica_dominio]["base_irrf"])
                        tableE.set_value('BASE_INSS', self.dicionario_rubricas_esocial[rubrica_dominio]["base_inss"])
                        tableE.set_value('BASE_FGTS', self.dicionario_rubricas_esocial[rubrica_dominio]["base_fgts"])
                        tableE.set_value('BASE_SINDICATO', self.dicionario_rubricas_esocial[rubrica_dominio]["base_sindicato"])
                        tableE.set_value('BASE_HEXTRA', self.dicionario_rubricas_esocial[rubrica_dominio]["base_hextra"])
                        tableE.set_value('BASE_PERICULOSIDADE', self.dicionario_rubricas_esocial[rubrica_dominio]["base_periculosidade"])
                        tableE.set_value('BASE_AUX1', self.dicionario_rubricas_esocial[rubrica_dominio]["base_aux1"])
                        tableE.set_value('BASE_AUX2', self.dicionario_rubricas_esocial[rubrica_dominio]["base_aux2"])
                        tableE.set_value('BASE_AUX3', self.dicionario_rubricas_esocial[rubrica_dominio]["base_aux3"])
                        tableE.set_value('HORAS_MES', self.dicionario_rubricas_esocial[rubrica_dominio]["horas_mes"])
                        tableE.set_value('COMP_13FER', self.dicionario_rubricas_esocial[rubrica_dominio]["comp_13fer"])
                        tableE.set_value('SOMA_FIC_FIN', self.dicionario_rubricas_esocial[rubrica_dominio]["soma_fic_fin"])
                        tableE.set_value('SOMA_RAIS', self.dicionario_rubricas_esocial[rubrica_dominio]["soma_rais"])
                        tableE.set_value('SOMA_INF_REN', self.dicionario_rubricas_esocial[rubrica_dominio]["soma_inf_ren"])
                        tableE.set_value('PAGA_PROP', self.dicionario_rubricas_esocial[rubrica_dominio]["paga_prop"])
                        tableE.set_value('APARECE_RECIBO', self.dicionario_rubricas_esocial[rubrica_dominio]["aparece_recibo"])
                        tableE.set_value('SOMA_SAL_BASE', self.dicionario_rubricas_esocial[rubrica_dominio]["soma_sal_base"])
                        tableE.set_value('ORDEM_CALCULO', self.dicionario_rubricas_esocial[rubrica_dominio]["ordem_calculo"])
                        tableE.set_value('CLASSIFICACAO', self.dicionario_rubricas_esocial[rubrica_dominio]["classificacao"])
                        tableE.set_value('REND_TRIBUTAVEIS', self.dicionario_rubricas_esocial[rubrica_dominio]["rend_tributaveis"])
                        tableE.set_value('REND_ISENTOS', self.dicionario_rubricas_esocial[rubrica_dominio]["rend_isentos"])
                        tableE.set_value('REND_SUJEITOS', self.dicionario_rubricas_esocial[rubrica_dominio]["rend_sujeitos"])
                        tableE.set_value('BASE_PIS', self.dicionario_rubricas_esocial[rubrica_dominio]["base_pis"])
                        tableE.set_value('REND_ADICIONAIS', self.dicionario_rubricas_esocial[rubrica_dominio]["rend_adicionais"])
                        tableE.set_value('BASE_RDSR', self.dicionario_rubricas_esocial[rubrica_dominio]["base_rdsr"])
                        tableE.set_value('BASE_RDSR_EVE', self.dicionario_rubricas_esocial[rubrica_dominio]["base_rdsr_eve"])
                        tableE.set_value('SOMA_MED_AFAST', self.dicionario_rubricas_esocial[rubrica_dominio]["soma_med_afast"])
                        tableE.set_value('SOMA_MED_AFAST_02', self.dicionario_rubricas_esocial[rubrica_dominio]["soma_med_afast_02"])
                        tableE.set_value('SOMA_MED_AFAST_03', self.dicionario_rubricas_esocial[rubrica_dominio]["soma_med_afast_03"])
                        tableE.set_value('SOMA_MED_AFAST_04', self.dicionario_rubricas_esocial[rubrica_dominio]["soma_med_afast_04"])
                        tableE.set_value('SOMA_MED_AFAST_05', self.dicionario_rubricas_esocial[rubrica_dominio]["soma_med_afast_05"])
                        tableE.set_value('SOMA_MED_AFAST_06', self.dicionario_rubricas_esocial[rubrica_dominio]["soma_med_afast_06"])
                        tableE.set_value('SOMA_MED_AFAST_07', self.dicionario_rubricas_esocial[rubrica_dominio]["soma_med_afast_07"])
                        tableE.set_value('SOMA_MED_AFAST_13', self.dicionario_rubricas_esocial[rubrica_dominio]["soma_med_afast_13"])
                        tableE.set_value('SOMA_MED_AFAST_14', self.dicionario_rubricas_esocial[rubrica_dominio]["soma_med_afast_14"])
                        tableE.set_value('SOMA_MED_AFAST_24', self.dicionario_rubricas_esocial[rubrica_dominio]["soma_med_afast_24"])
                        tableE.set_value('I_CADBASES', self.dicionario_rubricas_esocial[rubrica_dominio]["i_cadbases"])
                        tableE.set_value('CALC_AFAST', self.dicionario_rubricas_esocial[rubrica_dominio]["calc_afast"])
                        tableE.set_value('ADIC_AFAST', self.dicionario_rubricas_esocial[rubrica_dominio]["adic_afast"])
                        tableE.set_value('I_HORASAULA', self.dicionario_rubricas_esocial[rubrica_dominio]["i_horasaula"])
                        tableE.set_value('CALC_AFAST_02', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_AFAST_02"])
                        tableE.set_value('CALC_AFAST_03', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_AFAST_03"])
                        tableE.set_value('CALC_AFAST_04', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_AFAST_04"])
                        tableE.set_value('CALC_AFAST_05', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_AFAST_05"])
                        tableE.set_value('CALC_AFAST_06', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_AFAST_06"])
                        tableE.set_value('CALC_AFAST_07', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_AFAST_07"])
                        tableE.set_value('CALC_AFAST_13', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_AFAST_13"])
                        tableE.set_value('CALC_AFAST_14', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_AFAST_14"])
                        tableE.set_value('CALC_AFAST_24', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_AFAST_24"])
                        tableE.set_value('CALC_FIXO_FER', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_FIXO_FER"])
                        tableE.set_value('CALC_FIXO_FER_EVE', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_FIXO_FER_EVE"])
                        tableE.set_value('CALC_FIXO_FER_PROP_MES', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_FIXO_FER_PROP_MES"])
                        tableE.set_value('CALC_FIXO_FER_PROP_FER', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_FIXO_FER_PROP_FER"])
                        tableE.set_value('CALC_FIXO_13', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_FIXO_13"])
                        tableE.set_value('CALC_FIXO_13_EVE', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_FIXO_13_EVE"])
                        tableE.set_value('HOMOLOGNET', self.dicionario_rubricas_esocial[rubrica_dominio]["HOMOLOGNET"])
                        tableE.set_value('RUBRICA', self.dicionario_rubricas_esocial[rubrica_dominio]["RUBRICA"])
                        tableE.set_value('CODI_RUBRICA', self.dicionario_rubricas_esocial[rubrica_dominio]["CODI_RUBRICA"])
                        tableE.set_value('EMITIR_TERMO_RESCISAO', self.dicionario_rubricas_esocial[rubrica_dominio]["EMITIR_TERMO_RESCISAO"])
                        tableE.set_value('CAMPO_TERMO_RESCISAO', self.dicionario_rubricas_esocial[rubrica_dominio]["CAMPO_TERMO_RESCISAO"])
                        tableE.set_value('REND_ISENTOS_DESCRICAO', self.dicionario_rubricas_esocial[rubrica_dominio]["REND_ISENTOS_DESCRICAO"])
                        tableE.set_value('REND_SUJEITOS_DESCRICAO', self.dicionario_rubricas_esocial[rubrica_dominio]["REND_SUJEITOS_DESCRICAO"])
                        tableE.set_value('SOMA_MED_AFAST_26', self.dicionario_rubricas_esocial[rubrica_dominio]["SOMA_MED_AFAST_26"])
                        tableE.set_value('CALC_AFAST_26', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_AFAST_26"])
                        tableE.set_value('CORRIGE_MEDIA', self.dicionario_rubricas_esocial[rubrica_dominio]["CORRIGE_MEDIA"])
                        tableE.set_value('TIPO_CALCULO', self.dicionario_rubricas_esocial[rubrica_dominio]["TIPO_CALCULO"])
                        tableE.set_value('CALC_FIXO_13_DESC_ADIANT_13', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_FIXO_13_DESC_ADIANT_13"])
                        tableE.set_value('CALC_FIXO_ADIANT_13', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_FIXO_ADIANT_13"])
                        tableE.set_value('CALC_FIXO_ADIANT_13_EVE', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_FIXO_ADIANT_13_EVE"])
                        tableE.set_value('CALC_FIXO_ADIANT_13_PROP', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_FIXO_ADIANT_13_PROP"])
                        tableE.set_value('SOMA_MEDIA_AVISO_PREVIO', self.dicionario_rubricas_esocial[rubrica_dominio]["SOMA_MEDIA_AVISO_PREVIO"])
                        tableE.set_value('SOMA_ADICIONAL_AVISO_PREVIO', self.dicionario_rubricas_esocial[rubrica_dominio]["SOMA_ADICIONAL_AVISO_PREVIO"])
                        tableE.set_value('SOMA_MED_AFAST_32', self.dicionario_rubricas_esocial[rubrica_dominio]["SOMA_MED_AFAST_32"])
                        tableE.set_value('COMPOE_CAMPO_23_TERMO_RESCISAO', self.dicionario_rubricas_esocial[rubrica_dominio]["COMPOE_CAMPO_23_TERMO_RESCISAO"])
                        tableE.set_value('SOMA_MEDIA_SALDO_SALARIO', self.dicionario_rubricas_esocial[rubrica_dominio]["SOMA_MEDIA_SALDO_SALARIO"])
                        tableE.set_value('DESCONTA_DSR', self.dicionario_rubricas_esocial[rubrica_dominio]["DESCONTA_DSR"])
                        tableE.set_value('DESCONTA_DSR_EVENTO', self.dicionario_rubricas_esocial[rubrica_dominio]["DESCONTA_DSR_EVENTO"])
                        tableE.set_value('COMPOE_ADIANTAMENTO_SALARIAL', self.dicionario_rubricas_esocial[rubrica_dominio]["COMPOE_ADIANTAMENTO_SALARIAL"])
                        tableE.set_value('COMPOE_LIQUIDO', self.dicionario_rubricas_esocial[rubrica_dominio]["COMPOE_LIQUIDO"])
                        tableE.set_value('TIPO_CONSIDERACAO_CAMPO_23_TERMO_RESCISAO', self.dicionario_rubricas_esocial[rubrica_dominio]["TIPO_CONSIDERACAO_CAMPO_23_TERMO_RESCISAO"])
                        tableE.set_value('CALC_AFAST_35', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_AFAST_35"])
                        tableE.set_value('DATA_INICIO', self.dicionario_rubricas_esocial[rubrica_dominio]["DATA_INICIO"])
                        tableE.set_value('SITUACAO', self.dicionario_rubricas_esocial[rubrica_dominio]["SITUACAO"])
                        tableE.set_value('DATA_INATIVACAO', self.dicionario_rubricas_esocial[rubrica_dominio]["DATA_INATIVACAO"])
                        tableE.set_value('NATUREZA_FOLHA_MENSAL', self.dicionario_rubricas_esocial[rubrica_dominio]["NATUREZA_FOLHA_MENSAL"])
                        tableE.set_value('NATUREZA_13_INTEGRAL', self.dicionario_rubricas_esocial[rubrica_dominio]["NATUREZA_13_INTEGRAL"])
                        tableE.set_value('POSSUI_PROCESSO_REFERENTE_SUSPENSAO_INCIDENCIA_ENCARGOS', self.dicionario_rubricas_esocial[rubrica_dominio]["POSSUI_PROCESSO_REFERENTE_SUSPENSAO_INCIDENCIA_ENCARGOS"])
                        tableE.set_value('POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_PATRONAL', self.dicionario_rubricas_esocial[rubrica_dominio]["POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_PATRONAL"])
                        tableE.set_value('CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_PATRONAL', self.dicionario_rubricas_esocial[rubrica_dominio]["CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_PATRONAL"])
                        tableE.set_value('POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_EMPREGADOS', self.dicionario_rubricas_esocial[rubrica_dominio]["POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_EMPREGADOS"])
                        tableE.set_value('CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_EMPREGADOS', self.dicionario_rubricas_esocial[rubrica_dominio]["CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_INSS_EMPREGADOS"])
                        tableE.set_value('POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_FGTS', self.dicionario_rubricas_esocial[rubrica_dominio]["POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_FGTS"])
                        tableE.set_value('CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_FGTS', self.dicionario_rubricas_esocial[rubrica_dominio]["CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_FGTS"])
                        tableE.set_value('POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_IRRF', self.dicionario_rubricas_esocial[rubrica_dominio]["POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_IRRF"])
                        tableE.set_value('CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_IRRF', self.dicionario_rubricas_esocial[rubrica_dominio]["CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_IRRF"])
                        tableE.set_value('POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_SINDICAL', self.dicionario_rubricas_esocial[rubrica_dominio]["POSSUI_PROCESSO_SUSPENSAO_INCIDENCIA_SINDICAL"])
                        tableE.set_value('CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_SINDICAL', self.dicionario_rubricas_esocial[rubrica_dominio]["CODIGO_PROCESSO_SUSPENSAO_INCIDENCIA_SINDICAL"])
                        tableE.set_value('PERMITE_INFORMAR_NATUREZA_FOLHA_MENSAL', self.dicionario_rubricas_esocial[rubrica_dominio]["PERMITE_INFORMAR_NATUREZA_FOLHA_MENSAL"])
                        tableE.set_value('PERMITE_INFORMAR_NATUREZA_13_INTEGRAL', self.dicionario_rubricas_esocial[rubrica_dominio]["PERMITE_INFORMAR_NATUREZA_13_INTEGRAL"])
                        tableE.set_value('CODIGO_ESOCIAL', self.dicionario_rubricas_esocial[rubrica_dominio]["CODIGO_ESOCIAL"])
                        tableE.set_value('CONSIDERAR_FALTAS_PAGAMENTO_PROPORCIONAL', self.dicionario_rubricas_esocial[rubrica_dominio]["CONSIDERAR_FALTAS_PAGAMENTO_PROPORCIONAL"])
                        tableE.set_value('CALCULA_DIFERENCA_ALTERACAO_PISO_SALARIAL', self.dicionario_rubricas_esocial[rubrica_dominio]["CALCULA_DIFERENCA_ALTERACAO_PISO_SALARIAL"])
                        tableE.set_value('I_EVENTOS_DIFERENCA_PISO_SALARIAL', self.dicionario_rubricas_esocial[rubrica_dominio]["I_EVENTOS_DIFERENCA_PISO_SALARIAL"])
                        tableE.set_value('PERMITE_CALCULAR_DIFERENCA_PISO_SALARIAL', self.dicionario_rubricas_esocial[rubrica_dominio]["PERMITE_CALCULAR_DIFERENCA_PISO_SALARIAL"])
                        tableE.set_value('CALC_AFAST_39', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_AFAST_39"])
                        tableE.set_value('TIPO_VALOR_CONSIDERAR_CALCULO_MEDIAS', self.dicionario_rubricas_esocial[rubrica_dominio]["TIPO_VALOR_CONSIDERAR_CALCULO_MEDIAS"])
                        tableE.set_value('DETALHAR_LANCAMENTO_POR_SERVICO', self.dicionario_rubricas_esocial[rubrica_dominio]["DETALHAR_LANCAMENTO_POR_SERVICO"])
                        tableE.set_value('CALC_FIXO_ADIANT_13_EVE_MENSAL', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_FIXO_ADIANT_13_EVE_MENSAL"])
                        tableE.set_value('CALC_FIXO_ADIANT_13_MENSAL', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_FIXO_ADIANT_13_MENSAL"])
                        tableE.set_value('CALC_FIXO_ADIANT_13_PROP_MENSAL', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_FIXO_ADIANT_13_PROP_MENSAL"])
                        tableE.set_value('SOMA_MED_AFAST_41', self.dicionario_rubricas_esocial[rubrica_dominio]["SOMA_MED_AFAST_41"])
                        tableE.set_value('CALC_AFAST_41', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_AFAST_41"])
                        tableE.set_value('CALCULA_RATEIO_CONFORME_PERIODO_CADA_SERVICO', self.dicionario_rubricas_esocial[rubrica_dominio]["CALCULA_RATEIO_CONFORME_PERIODO_CADA_SERVICO"])
                        tableE.set_value('CALCULAR_DIFERENCA_RUBRICA', self.dicionario_rubricas_esocial[rubrica_dominio]["CALCULAR_DIFERENCA_RUBRICA"])
                        tableE.set_value('I_EVENTOS_DIFERENCA_VALOR', self.dicionario_rubricas_esocial[rubrica_dominio]["I_EVENTOS_DIFERENCA_VALOR"])
                        tableE.set_value('SOMA_MED_AFAST_50', self.dicionario_rubricas_esocial[rubrica_dominio]["SOMA_MED_AFAST_50"])
                        tableE.set_value('CALC_AFAST_50', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_AFAST_50"])
                        tableE.set_value('GERAR_RUBRICA_SALDO_SALARIO_RESCISAO', self.dicionario_rubricas_esocial[rubrica_dominio]["GERAR_RUBRICA_SALDO_SALARIO_RESCISAO"])
                        tableE.set_value('RUBRICA_SALDO_SALARIO_RESCISAO', self.dicionario_rubricas_esocial[rubrica_dominio]["RUBRICA_SALDO_SALARIO_RESCISAO"])
                        tableE.set_value('CODIGO_INCIDENCIA_IRRF_ESOCIAL', self.dicionario_rubricas_esocial[rubrica_dominio]["CODIGO_INCIDENCIA_IRRF_ESOCIAL"])
                        tableE.set_value('CODIGO_INCIDENCIA_INSS_ESOCIAL', self.dicionario_rubricas_esocial[rubrica_dominio]["CODIGO_INCIDENCIA_INSS_ESOCIAL"])
                        tableE.set_value('SOMA_MED_AFAST_19', self.dicionario_rubricas_esocial[rubrica_dominio]["SOMA_MED_AFAST_19"])
                        tableE.set_value('SOMA_MEDIA_LICENCA_PREMIO', self.dicionario_rubricas_esocial[rubrica_dominio]["SOMA_MEDIA_LICENCA_PREMIO"])
                        tableE.set_value('SOMA_ADICIONAL_LICENCA_PREMIO', self.dicionario_rubricas_esocial[rubrica_dominio]["SOMA_ADICIONAL_LICENCA_PREMIO"])
                        tableE.set_value('SOMA_MED_AFAST_35', self.dicionario_rubricas_esocial[rubrica_dominio]["SOMA_MED_AFAST_35"])
                        tableE.set_value('CONSIDERAR_FALTAS_PARCIAIS_CALCULO_PROPORCIONAL', self.dicionario_rubricas_esocial[rubrica_dominio]["CONSIDERAR_FALTAS_PARCIAIS_CALCULO_PROPORCIONAL"])
                        tableE.set_value('CONSIDERAR_FALTAS_DSR_CALCULO_PROPORCIONAL', self.dicionario_rubricas_esocial[rubrica_dominio]["CONSIDERAR_FALTAS_DSR_CALCULO_PROPORCIONAL"])
                        tableE.set_value('CONSIDERAR_FALTAS_NOTURNAS_CALCULO_PROPORCIONAL', self.dicionario_rubricas_esocial[rubrica_dominio]["CONSIDERAR_FALTAS_NOTURNAS_CALCULO_PROPORCIONAL"])
                        tableE.set_value('CODIGO_INCIDENCIA_FGTS_ESOCIAL', self.dicionario_rubricas_esocial[rubrica_dominio]["CODIGO_INCIDENCIA_FGTS_ESOCIAL"])
                        tableE.set_value('SOMA_MED_AFAST_20', self.dicionario_rubricas_esocial[rubrica_dominio]["SOMA_MED_AFAST_20"])
                        tableE.set_value('CODIGO_INCIDENCIA_SINDICAL_ESOCIAL', self.dicionario_rubricas_esocial[rubrica_dominio]["CODIGO_INCIDENCIA_SINDICAL_ESOCIAL"])
                        tableE.set_value('SOMA_MED_AFAST_59', self.dicionario_rubricas_esocial[rubrica_dominio]["SOMA_MED_AFAST_59"])
                        tableE.set_value('SOMA_MED_AFAST_60', self.dicionario_rubricas_esocial[rubrica_dominio]["SOMA_MED_AFAST_60"])
                        tableE.set_value('CALC_AFAST_59', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_AFAST_59"])
                        tableE.set_value('CALC_AFAST_60', self.dicionario_rubricas_esocial[rubrica_dominio]["CALC_AFAST_60"])
                        tableE.set_value('UTILIZA_PARA_ESOCIAL_DOMESTICO', self.dicionario_rubricas_esocial[rubrica_dominio]["UTILIZA_PARA_ESOCIAL_DOMESTICO"])
                        tableE.set_value('CODIGO_ESOCIAL_DOMESTICO', self.dicionario_rubricas_esocial[rubrica_dominio]["CODIGO_ESOCIAL_DOMESTICO"])
                        tableE.set_value('aparece_relatorio', self.dicionario_rubricas_esocial[rubrica_dominio]["aparece_relatorio"])
                        tableE.set_value('CODIGO_INCIDENCIA_RPPS_ESOCIAL', self.dicionario_rubricas_esocial[rubrica_dominio]["CODIGO_INCIDENCIA_RPPS_ESOCIAL"])
                        tableE.set_value('ORIGEM_REG', "1")

                        #formula = self.dicionario_formulas_esocial[dados_rubricas['i_eventos']]

                        #for base in self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']]:
                        #    tableEB = Table('FOEVENTOSBASES')
                        #    tableEB.set_value('codi_emp', codi_emp_rubrica)
                        #    tableEB.set_value('i_eventos',rubrica_dominio)
                        #    tableEB.set_value('i_cadbases',self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']][base]["i_cadbases"])
                        #    tableEB.set_value('I_DADOS_EVENTOS_ESOCIAL',self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']][base]["I_DADOS_EVENTOS_ESOCIAL"])
                        #    tableEB.set_value('I_LOTE_ESOCIAL',self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']][base]["I_LOTE_ESOCIAL"])
                        #    tableEB.set_value('STATUS_ESOCIAL',self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']][base]["STATUS_ESOCIAL"])
                        #    tableEB.set_value('ENVIAR_ESOCIAL',self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']][base]["ENVIAR_ESOCIAL"])
                        #    tableEB.set_value('INCLUSAO_VALIDADA_ESOCIAL',self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']][base]["INCLUSAO_VALIDADA_ESOCIAL"])
                        #    tableEB.set_value('GERAR_RETIFICACAO_ESOCIAL',self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']][base]["GERAR_RETIFICACAO_ESOCIAL"])
                        #    tableEB.set_value('PROCESSAR_EXCLUSAO_ESOCIAL',self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']][base]["PROCESSAR_EXCLUSAO_ESOCIAL"])
                        #    tableEB.set_value('COMPANY_ID',self.dicionario_bases_rubricas_esocial[dados_rubricas['i_eventos']][base]["COMPANY_ID"])

                        #    tabela_FOEVENTOSBASES.append(tableEB.do_output())

                        #formula = self.dicionario_formulas_esocial[rubrica_dominio]

                    tabela_FOEVENTOS.append(tableE.do_output())
                    
                    #tableF = Table('FOFORMULAS')
                    #tableF.set_value('codi_emp',codi_emp_rubrica)
                    #tableF.set_value('i_eventos',rubrica_dominio)
                    #tableF.set_value('script',formula["script"])
                    #tableF.set_value('fil1',formula["fil1"])
                    #tableF.set_value('fil2',formula["fil2"])
                    #tableF.set_value('fil3',formula["fil3"])
                    #tableF.set_value('fil4',formula["fil4"])
                    #tableF.set_value('origem_reg',"1")
                    #tableF.set_value('COMPANY_ID',formula["COMPANY_ID"])

                    #tabela_FOFORMULAS.append(tableF.do_output())

                    rubricas_impressas.append(f'{codi_emp}-{rubrica_dominio}')
                
                tableL = Table('FOLANCTOMEDIAS')
                tableL.set_value('CODI_EMP', codi_emp)
                tableL.set_value('I_EMPREGADOS', i_empregados)
                tableL.set_value('COMPETENCIA', data)
                tableL.set_value('I_EVENTOS', rubrica_dominio)

                if(tipo_inf=="V"):
                    coluna_valor = valor
                else:
                    coluna_valor = quantidade

                coluna_valor = str(coluna_valor)

                if '.' in coluna_valor:
                    coluna_valor = coluna_valor.split('.')[0].rjust(10,'0') + '.' + coluna_valor.split('.')[1].rjust(2,'0')
                else:
                    coluna_valor = coluna_valor.rjust(10,'0') + '.00'

                tableL.set_value('VALOR', coluna_valor)
                tableL.set_value('I_FERIAS_GOZO', "NULO")
                tableL.set_value('ORIGEM', "1")
                tabela_FOLANCTOMEDIAS.append(tableL.do_output())

        print_to_import(f'{self.DIRETORIO_SAIDA}\\FOEVENTOS.txt', tabela_FOEVENTOS)
        #print_to_import(f'{self.DIRETORIO_SAIDA}\\FOEVENTOSBASES.txt', tabela_FOEVENTOS)
        #print_to_import(f'{self.DIRETORIO_SAIDA}\\FOFORMULAS.txt', tabela_FOEVENTOS)
        print_to_import(f'{self.DIRETORIO_SAIDA}\\FOLANCTOMEDIAS.txt', tabela_FOLANCTOMEDIAS)

    def salva_xml(self, nome, xml):
        arquivo_xml = open(f'{self.DIRETORIO_XML}\{nome}.xml', 'w')
        arquivo_xml.write(xml)
        arquivo_xml.close()

    def processa_arquivo(self, evento):
        nome = ''
        xml = ''
        arquivo = open(f"{self.DIRETORIO_ENTRADA}\\{evento}xml.csv", 'r')
        for linha in arquivo:
            if((linha!="") & (linha[0]!="(")):
                vetor = linha.split(";")
                nome = vetor[0]
                xml = self.normalizador(vetor[1])
                self.salva_xml(nome,xml)
        arquivo.close()

    def extrai_informacoes_xml(self):
        json_xmls_nao_processados = {}
        xml_reprocessamento = []
        posicao_reprocessamento = []

        for root, dirs, files in os.walk(self.DIRETORIO_XML):
            arquivos_xml = files.copy()

        for arquivo in tqdm(arquivos_xml):
            if(arquivo==".gitignore"): continue
            try:  
                doc = xml.parse(f'{self.DIRETORIO_XML}\{arquivo}')
                evento = ""

                for eSocial in doc.getElementsByTagName("eSocial"):
                    xmlns = eSocial.getAttribute("xmlns")
                    ambiente = self.extrai_tag(eSocial,"tpAmb")

                    if(xmlns==None): evento = ""
                    elif(xmlns==""): evento = ""
                    else: evento = xmlns.split('/')[-2]
                    
                    if(ambiente=="1"): 
                        if(evento=="evtTabRubrica"): #S1010
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
                        
                        if(evento=='evtRemun'): #S1200
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
                            
            except IndexError:
                print("Erro de indexação")
            except FileNotFoundError:
                pass
            except Exception as e:
                erro = str(e)

                if(erro[:15]=="not well-formed"):
                    xml_reprocessamento.append(arquivo)
                    posicao_erro = re.sub('[\D]','',erro)
                    posicao_reprocessamento.append(int(posicao_erro[1:]))

        for arquivo in xml_reprocessamento:
            try:
                f = open(f'{self.DIRETORIO_XML}\{arquivo}','r')
                texto_xml = f.read()
                f.close

                texto_xml = texto_xml[0:xml_reprocessamento.index(arquivo)] + texto_xml[xml_reprocessamento.index(arquivo) + 1:]

                doc = xml.parseString(f'{texto_xml}')
                evento = ""

                for eSocial in doc.getElementsByTagName("eSocial"):
                    xmlns = eSocial.getAttribute("xmlns")
                    ambiente = self.extrai_tag(eSocial,"tpAmb")

                    if(xmlns==None): evento = ""
                    elif(xmlns==""): evento = ""
                    else: evento = xmlns.split('/')[-2]
                    
                    if(ambiente=="1"): 
                        if(evento=="evtTabRubrica"): #S1010
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
                        
                        if(evento=='evtRemun'): #S1200
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
            except IndexError:
                print("Erro de indexação")
            except FileNotFoundError:
                pass
            except Exception as e:
                erro = str(e)
                json_xmls_nao_processados[arquivo] = {
                    'erro': erro
                }

        f = open(f'{self.DIRETORIO_XML}\\nao_processados.json', "w")
        f.write(json.dumps(json_xmls_nao_processados))
        f.close()

    def gera_excel_relacao(self, dicionario_relacoes, conversor, pasta_xml):
        '''Gera o excel com as rubricas para relacionar com as rubricas padrão do Domínio'''

        linhas_excel_alerta = set()
        linhas_excel_relacionado = set()
        linhas_excel_nao_relacionado = set()
        linhas_excel_multirelacionado = set()
        relacao_dominio_esocial = {}
        lista_rubricas = []
        
        for s1010 in self.dicionario_s1010:
            if (self.dicionario_s1010[s1010]["codigo_rubrica"] not in lista_rubricas):
                lista_rubricas.append(self.dicionario_s1010[s1010]["codigo_rubrica"])

                lista_relacoes = self.relaciona_rubricas(self.dicionario_s1010[s1010], dicionario_relacoes, conversor)

                if(len(lista_relacoes)==0):
                    linhas_excel_nao_relacionado.add((
                        self.dicionario_s1010[s1010]["codigo_rubrica"],
                        self.dicionario_s1010[s1010]["descricao"],
                        self.dicionario_s1010[s1010]["natureza_rubrica"],
                        self.dicionario_s1010[s1010]["incidencia_previdencia"],
                        self.dicionario_s1010[s1010]["incidencia_irrf"],
                        self.dicionario_s1010[s1010]["incidencia_fgts"],
                        "N"
                    ))
                elif(len(lista_relacoes)==1):
                    linhas_excel_relacionado.add((
                        self.dicionario_s1010[s1010]["codigo_rubrica"],
                        self.dicionario_s1010[s1010]["descricao"],
                        self.dicionario_s1010[s1010]["natureza_rubrica"],
                        self.dicionario_s1010[s1010]["incidencia_previdencia"],
                        self.dicionario_s1010[s1010]["incidencia_irrf"],
                        self.dicionario_s1010[s1010]["incidencia_fgts"],
                        lista_relacoes[0],
                        "X"
                    ))

                    if(relacao_dominio_esocial.get(lista_relacoes[0])==None): relacao_dominio_esocial[lista_relacoes[0]] = []
                    relacao_dominio_esocial[lista_relacoes[0]].append(s1010)
                    
                elif(len(lista_relacoes)>1):
                    linha = [
                        self.dicionario_s1010[s1010]["codigo_rubrica"],
                        self.dicionario_s1010[s1010]["descricao"],
                        self.dicionario_s1010[s1010]["natureza_rubrica"],
                        self.dicionario_s1010[s1010]["incidencia_previdencia"],
                        self.dicionario_s1010[s1010]["incidencia_irrf"],
                        self.dicionario_s1010[s1010]["incidencia_fgts"],
                        ""
                    ]

                    relacionamento_atual = 0
                    
                    while relacionamento_atual < 10:
                        if(relacionamento_atual < len(lista_relacoes)):
                            if(self.dicionario_rubricas_esocial.get(int(lista_relacoes[relacionamento_atual]))!=None):
                                linha.append(lista_relacoes[relacionamento_atual])
                                linha.append(self.dicionario_rubricas_esocial.get(int(lista_relacoes[relacionamento_atual])).get("nome"))

                                if(relacao_dominio_esocial.get(lista_relacoes[0])==None):
                                    relacao_dominio_esocial[lista_relacoes[0]] = []
                                
                                if(s1010 not in relacao_dominio_esocial[lista_relacoes[0]]): 
                                    relacao_dominio_esocial[lista_relacoes[0]].append(s1010)
                        else:
                            linha.append("")
                            linha.append("")

                        relacionamento_atual = relacionamento_atual + 1
                    
                    linhas_excel_multirelacionado.add(tuple(linha))
                    
        for relacao in relacao_dominio_esocial:
            if(len(relacao_dominio_esocial[relacao])>1):
                for rubrica in relacao_dominio_esocial[relacao]:
                    linhas_excel_alerta.add((
                        self.dicionario_s1010[rubrica]["codigo_rubrica"],
                        self.dicionario_s1010[rubrica]["descricao"],
                        self.dicionario_s1010[rubrica]["natureza_rubrica"],
                        self.dicionario_s1010[rubrica]["incidencia_previdencia"],
                        self.dicionario_s1010[rubrica]["incidencia_irrf"],
                        self.dicionario_s1010[rubrica]["incidencia_fgts"],
                        relacao,
                        "X"
                    ))

        cabecalho_padrao = ['Código','Descrição','natureza_tributaria_rubrica','codigo_incidencia_inss_esocial','codigo_incidencia_irrf_esocial','codigo_incidencia_fgts_esocial']
        cabecalho_relacionado = cabecalho_padrao + ['Código Domínio','"X" para manter o relacionamento \nou \nInforme a rúbrica equivalente \nou \n"N" para cadastrar a rúbrica']
        cabecalho_multirelacionado = cabecalho_padrao + ['Informe a rúbrica equivalente \nou \n"N" para cadastrar a rúbrica','Opção 1','Descrição 1','Opção 2','Descrição 2','Opção 3','Descrição 3','Opção 4','Descrição 4','Opção 5','Descrição 5','Opção 6','Descrição 6','Opção 7','Descrição 7','Opção 8','Descrição 8','Opção 9','Descrição 9','Opção 10','Descrição 10']
        cabecalho_nao_relacionado =  cabecalho_padrao + ['Informe a rúbrica equivalente \nou \n"N" para cadastrar a rúbrica']
        cabecalho_alerta = cabecalho_padrao + ['Código Domínio', '"X" para somar as rúbricas \nou \n"D" para desconsiderar as rúbricas duplicadas \nou \nInforme a rúbrica equivalente \nou \n"N" para cadastrar a rúbrica']

        self.imprime_excel(
            f'{self.DIRETORIO_XML}\\relacao_rubricas.xlsx', 
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

        except:
            print(f'Erro na aba "Relacionado": {str(e)}')
            pass
        
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
        except:
            print(f'Erro na aba "+ de 1 result.": {str(e)}')
            pass
        
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
        except:
            print(f'Erro na aba "Sem result.": {str(e)}')
            pass

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

        writer.save()

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
    
    def normalizador(self, texto):
        texto = texto.strip()
        texto = re.sub('[\u0096º°ª]','',texto)
        return texto

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

    def relaciona_rubricas(self, rubric, dicionario_relacoes, conversor):
        '''Recebe como parâmetro uma rúbrica do concorrente e uma lista de rúbricas da Domínio,
        e faz uma série de validações para relacionar a rúbrica do concorrente com alguma correspondente da Domínio.'''
        result = []
        
        # aplicação de depara
        if(dicionario_relacoes.get(conversor).get(rubric["codigo_rubrica"])): result.append(str(dicionario_relacoes.get(conversor).get(rubric["codigo_rubrica"])))
        
        # Comparação através do algoritmo de Levenshtein
        menor_distancia_levenshtein = 50
                
        for rubrica_dominio in self.dicionario_rubricas_esocial:
            distancia_levenshtein = Levenshtein.distance(
                rubric["descricao"].upper(),
                self.dicionario_rubricas_esocial[rubrica_dominio]["nome"]
            )

            if (distancia_levenshtein < menor_distancia_levenshtein):
                menor_distancia_levenshtein = distancia_levenshtein
                lista_relacoes_levenshtein = []
                if(menor_distancia_levenshtein<3):
                    lista_relacoes_levenshtein.append(str(rubrica_dominio))
            elif (distancia_levenshtein==menor_distancia_levenshtein):
                if(menor_distancia_levenshtein<3):
                    lista_relacoes_levenshtein.append(str(rubrica_dominio))

        for relacao in lista_relacoes_levenshtein:
            result.append(str(relacao))

        # Comparação de dados das rubricas para rubricas não relacionadas
        if(len(result)==0):
            rubesocial = rubric['natureza_rubrica']
            tpbaseinss = rubric['incidencia_previdencia']
            tpbaseirrf = rubric['incidencia_irrf']
            tpbasefgts = rubric['incidencia_fgts']
            
            for item in self.dicionario_rubricas_esocial:
                if str(rubesocial) in str(self.dicionario_rubricas_esocial[item]['NATUREZA_FOLHA_MENSAL']):
                    if str(tpbaseinss) in str(self.dicionario_rubricas_esocial[item]['CODIGO_INCIDENCIA_INSS_ESOCIAL']):
                        if str(tpbaseirrf) in str(self.dicionario_rubricas_esocial[item]['CODIGO_INCIDENCIA_IRRF_ESOCIAL']):
                            if str(tpbasefgts) in str(self.dicionario_rubricas_esocial[item]['CODIGO_INCIDENCIA_FGTS_ESOCIAL']):
                                result.append(str(self.dicionario_rubricas_esocial[item]['i_eventos']))

        return list(set(result))
    
    def atribui_nova_rubrica(self, rubrica_concorrente, natureza):
        '''Gera código de nova rubrica caso seja uma que necessita ser cadastrada para a importação de médias'''

        dados_rubrica_nova = self.preenchimento_padrao_por_natureza(natureza)
        if not dados_rubrica_nova:
            return False

        if ((dados_rubrica_nova["soma_med_13"]=="N")|(dados_rubrica_nova["soma_med_fer"]=="N")):
            return False

        if (rubrica_concorrente not in self.rubricas_cadastrar):
            self.rubricas_cadastrar.append(rubrica_concorrente)
        
        rubrica_nova = 201 + self.rubricas_cadastrar.index(rubrica_concorrente)
        if rubrica_nova <= 250:
            self.rubricas_novas.append(rubrica_nova)
            return rubrica_nova
        else:
            return False

    def preenchimento_padrao_por_natureza(self,natureza):
        '''Seleciona dados padrão de acordo com a natureza da rubrica no e-Social'''

        dados_rubrica = False

        for rubrica in self.dicionario_rubricas_esocial:
            if str(natureza) == str(self.dicionario_rubricas_esocial[rubrica]["NATUREZA_FOLHA_MENSAL"]):
                if(self.dicionario_rubricas_esocial[rubrica]["soma_med_13"]=="S")|(self.dicionario_rubricas_esocial[rubrica]["soma_med_fer"]=="S"):
                    return self.dicionario_rubricas_esocial[rubrica]
                else:
                    dados_rubrica = self.dicionario_rubricas_esocial[rubrica]
        
        return dados_rubrica