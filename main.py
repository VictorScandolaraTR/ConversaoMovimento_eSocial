import os, json
from classes.esocial import eSocialXML

os.system("cls")
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