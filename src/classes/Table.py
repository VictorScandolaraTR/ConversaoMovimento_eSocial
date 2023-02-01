import sqlite3
from sqlite3 import connect
from os.path import isfile
from sys import exc_info
from os.path import split



class Table:

    def __init__(self, table, default_value=True, file=False, load_columns_first_line=False, columns=[],
                 path_def='.\\src\\database\\def.db'):
        self.__table = table
        self.__object = {}
        self.__list_objects = []
        self.__file = file
        self.__default_value = default_value
        self.__load_columns_first_line = load_columns_first_line
        self.__columns = columns
        self.__path_def = str(path_def)
        self.__default_def = '.\\src\\database\\def.db'

        if not self.__file:
            self.__object = self.init()
        else:
            if self.__load_columns_first_line:
                self.__columns = self.load_columns_first_line()
            self.__list_objects = self.init_multiple_tables()

    def init(self):
        result = {}

        if not self.__columns:
            try:
                connection = connect(self.__path_def)
                cursor = connection.cursor()
                cursor.execute(f'select * from {self.__table}')
            except sqlite3.OperationalError:
                if isfile(self.__default_def):
                    connection = connect(self.__default_def)
                    cursor = connection.cursor()
                    cursor.execute(f'select * from {self.__table}')


            data = cursor.fetchall()
            for column in data:
                if self.__default_value:
                    value = column[8]
                else:
                    value = ''

                result[str(column[1]).upper()] = value

            connection.close()
        else:
            for column in self.__columns:
                result[str(column).upper().replace('\n', '')] = ''

        return result

    def load_columns_first_line(self):
        result = {}
        with open(self.__file, encoding=predict_encoding(self.__file)) as input_file:
            first_line = input_file.readline()
            for column in first_line.split('\t'):
                result[str(column).upper().replace('\n', '')] = ''

        return result

    def init_multiple_tables(self):
        """
        A partir de um arquivo que esteja no padrão da DEF preenche um array,
        onde cada item do array será um dicionário referente a respectiva
        linha do arquivo, com o nome do campo e valor
        """
        self.__objects = []
        errors = []

        with open(self.__file, encoding=predict_encoding(self.__file)) as input_file:
            data = input_file.readlines()

            # remover primeira linha
            if self.__load_columns_first_line:
                data.pop(0)

            for line in data:
                split_line = line.split('\t')
                table = Table(self.__table, columns=self.__columns, path_def=self.__path_def)

                for column in enumerate(table.do_output().keys()):
                    try:
                        table.set_value(column[1], str(split_line[column[0]]).replace('\n', ''))

                    except IndexError as error:  # ocorre erro quando a DEF utilizada da conversão está desatualizada
                        table.set_value(column[1], '')  # Seta a coluna como vazia
                        if column[1] not in errors:
                            errors.append(column[1])

                self.__objects.append(table)

        return self.__objects

    def set_value(self, column, value):
        self.__object[str(column).upper()] = value

    def get_value(self, column):
        if str(column).upper() in self.__object.keys():
            return self.__object[str(column).upper()]
        else:
            return False

    def do_output(self):
        return self.__object

    def items(self):
        if self.__file:
            return self.__list_objects

    def values(self):
        return tuple(self.__object.values())

    def columns_output(self):
        return self.__object.keys()

    def exist_column(self, column):
        if str(column).upper() in self.columns_output():
            return True
        else:
            return False


def predict_encoding(file_path):
    """
    Retorna o tipo de encoding de uma arquivo
    """
    encodings = ['utf-8', 'ANSI']
    encoding = ''
    for encoding_option in encodings:
        try:
            file = open(file_path, encoding=encoding_option)
            file.readlines()
            file.seek(0)
        except UnicodeDecodeError:
            pass
        else:
            encoding = encoding_option
            break
    return encoding
