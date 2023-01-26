from os import replace, remove, system
import re
import tempfile
import shutil
import chardet
from datetime import datetime, timedelta
import json

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


def format_date(date, date_format):
    try:
        return datetime.strptime(date, date_format)
    except:
        return None


def transform_date(date, old_format, new_format, default_value_error=None):
    """
    Mudar formato de uma data
    """
    try:
        return datetime.strftime(format_date(date, old_format), new_format)
    except:
        return default_value_error


def convert_date(str_date, date_format, default_value_error='NULO'):
    """
    Converter uma String para data
    """
    try:
        if isinstance(str_date, str):
            return datetime.strptime(str_date, date_format).date()
        else:
            return str_date.date()
    except:
        return default_value_error


def is_null(field, check_int=False, date=False):
    """
    Verifica se o valor presente no campo é válido ou não
    """
    result = False
    if type(field) == str:
        if str(field).strip().upper() == '':
            result = True
        elif str(field).strip().upper() == 'NULO':
            result = True
        elif str(field).strip().upper() == 'NULL':
            result = True

    if field == None:
        result = True

    if field == False:
        result = True

    if check_int:
        try:
            if int(field) == 0:
                return True
        except:
            return True

    if date:
        if field == '01/01/1900':
            return True

    return result


def add_day_to_date(str_date, date_format, days, default_value_error='NULO'):
    """
    Adiciona dias(int) a uma string de data e retorna uma string no formato DD/MM/YYYY
    """
    try:
        new_date = default_value_error
        if not is_null(str_date):
            date = convert_date(str_date, date_format)
            new_date = (date + timedelta(days=days)).strftime("%d/%m/%Y")

        return new_date
    except:
        return default_value_error


def get_keys(key):
    """
    Retorna valores do arquivo depara.json
    """
    with open('.\\src\\database\\depara.json') as file:
        dicionario = json.load(file)

    if str(key).upper() in dicionario.keys():
        return dicionario[str(key).upper()]
    elif str(key).lower() in dicionario.keys():
        return dicionario[str(key).lower()]
    elif str(key).capitalize() in dicionario.keys():
        return dicionario[str(key).capitalize()]
    else:
        return False


def get_current_day():
    """
    Retorna a data atual
    """
    return datetime.today()


def difference_between_dates(str_start_date, str_end_date, date_format):
    """
    Retorna a diferença em dias entre duas datas
    """
    result = False
    if not is_null(str_start_date) and not is_null(str_end_date):
        start_date = convert_date(str_start_date, date_format)
        end_date = convert_date(str_end_date, date_format)
        if end_date < start_date:
            result = 0
        else:
            result = abs((start_date - end_date).days)

    return result
