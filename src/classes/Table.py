from sqlite3 import connect
import sys
from src.utils.functions import remove_caracter_out_of_cp1252

class Table:

    def __init__(self, table):
        self.__object = self.init(table)


    def init(self, table):
        connection = connect('.\\src\\database\\def.db')
        cursor = connection.cursor()
        cursor.execute(f'select * from {table}')

        data = cursor.fetchall()

        result = {}
        for column in data:
            result[column[1]] = column[8]
        
        connection.close()
        return result

    
    def set_value(self, column, value):
        if type(value) is str:
            value = remove_caracter_out_of_cp1252(value)
        self.__object[column] = value

    def get_value(self, column):
        return self.__object[str(column).upper()]
        
    def do_output(self):
        return self.__object
