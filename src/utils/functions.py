from os import replace, remove, system
import re
import tempfile
import shutil
import chardet

def print_to_import(output_file, data):
    """
    Recebe como parâmetro o arquivo de saída e um dicionário, e imprime os valores do dicionário em um arquivo txt
    """
    try:
        with open(output_file, 'w') as output:
            for linha in data:
                for column in linha.keys():
                    output.write(f'{linha[column]}\t')
                
                output.write('\n')
        return True
    except:
        print("Erro arquivo: "+output_file)
        return False

def remove_caracter(arquivo, stringAremover, stringAinserir):
    arquivo_open = open (arquivo, "r", encoding=predict_encoding(arquivo))
    arquivo_read = arquivo_open.read()
    arquivo_open.close()
    arquivo_open = open (arquivo, "w")
    arquivo_open.write(arquivo_read.replace(stringAremover,stringAinserir))
    arquivo_open.close()

def insere_layout(arquivo, layout):
    enco = predict_encoding(arquivo)
    print(arquivo +' '+predict_encoding(arquivo))
    arquivo_open = open (arquivo, "r", encoding=predict_encoding(arquivo))
    arquivo_read = arquivo_open.read()
    arquivo_open.close()
    layout_open = open (layout, "r", encoding=predict_encoding(layout))
    layout_read = layout_open.read().replace("[","").replace("]","")
    layout_open.close()
    if layout_read not in arquivo_read:
        remove(arquivo)
        arquivo_open = open (arquivo, "w")
        arquivo_open.write(layout_read + "\n" + arquivo_read)
        arquivo_open.close()

def verifica_int(string):
    try:
        int(string)
        return True
    except:
        return False

def remove_enter(arquivo):
    menor = 1
    while menor > 0:
        menor = 0
        arquivo_open = open (arquivo, "r")
        arquivo_read_line = arquivo_open.readlines()
        arquivo_open.close()
        new_arquivo = []
        for linha in arquivo_read_line:
            if arquivo_read_line.index(linha) == 0: 
                new_arquivo.append(linha)
                continue
            if len(linha.split('";"')) < len(arquivo_read_line[0].split('";"')) and verifica_int(linha[1:(len(linha)-2)].split('";"')[0]):
                new_arquivo.append(linha.replace("\n",""))
                menor = 1
            else:
                new_arquivo.append(linha)
            # os.system("pause")
        arquivo_open = open (arquivo, "w")
        arquivo_open.writelines(new_arquivo)
        arquivo_open.close()

def predict_encoding(file_path, n_lines=100):
    encodings = ['utf-8', 'ANSI']
    encoding = ''
    for e in encodings:
        try:
            fh = open(file_path, 'r', encoding=e)
            fh.readlines()
            fh.seek(0)
        except UnicodeDecodeError:
            False
            #print('got unicode error with %s , trying different encoding' % e)
        else:
            #print('opening the file with encoding:  %s ' % e)
            encoding = e
            break
    return encoding

def remove_caracter_out_of_cp1252(string):
    '''
    Remove os caracteres que não estão no padrão cp1252 causam erro de encode
    '''
    retorno = ''
    for s in string:
        try:
            s = str(s).encode('cp1252')
            s = s.decode("cp1252", "strict") 
            retorno = retorno + s
        except:
            pass
    return retorno