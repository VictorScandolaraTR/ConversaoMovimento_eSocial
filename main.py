import os, json, sys
from src.esocial import eSocialXML
from src.rpa.rpa import RPA

os.system("cls")
esocial = eSocialXML("xml")
esocial.carregar_informacoes_xml()

relacao_empresas = esocial.relaciona_empresas()
relacao_empregados = esocial.relaciona_empregados()

esocial.gera_excel_relacao(relacao_empresas)

# gerar arquivos cadastrais
esocial.gerar_afastamentos_importacao(relacao_empresas, relacao_empregados)
esocial.gerar_ferias_importacao(relacao_empresas, relacao_empregados)

# gerar arquivos para importação de lançamentos
data_vacation = esocial.gerar_arquivos_saida(relacao_empresas, relacao_empregados)

# gerar férias e rescisões que irão ser calculadas pelo RPA
esocial.save_rescission(relacao_empresas, relacao_empregados)
esocial.save_vacation(data_vacation)

# Iniciar o RPA
rpa = RPA()

'''f = open("s1010.json","w")
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