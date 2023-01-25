from pyodbc import connect

class Sybase:

    def __init__(self, database, username, password):
        self.__database = database
        self.__username = username
        self.__password = password

    def connect(self):
        try:
            conn = connect(
                DSN=self.__database,
                UID=self.__username,
                PWD=self.__password
            )
            
        except:
            return False
        
        return conn
        

    def select_def_table(self, connection, table):
        cursor = connection.cursor()
        query = f"""
            SELECT CAMPO_ID = SYSCOLUMN.COLUMN_ID,
                CAMPO_NOME = SYSCOLUMN.COLUMN_NAME,
                CAMPO_DESCRICAO = ISNULL(CONVERT(VARCHAR(32767), SYSCOLUMN.REMARKS),''),
                CAMPO_TIPO = SYSCOLUMNS.COLTYPE,
                CAMPO_TAMANHO = STRING(SYSCOLUMN.WIDTH),
                CAMPO_DECIMAL = STRING(SYSCOLUMNS.SYSLENGTH),
                CAMPO_PRIMARIA = SYSCOLUMN.PKEY,
                CAMPO_NULO = SYSCOLUMN.NULLS,
                CAMPO_PADRAO = ISNULL(CONVERT(VARCHAR(32767),REPLACE(SYSCOLUMNS.DEFAULT_VALUE,CHAR(39),'')),'')
            FROM SYSTABLE,
                SYSCOLUMN,
                SYS.SYSCOLUMNS
            WHERE SYSTABLE.TABLE_ID = SYSCOLUMN.TABLE_ID
                AND SYSCOLUMN.COLUMN_NAME = SYSCOLUMNS.CNAME
                AND SYSTABLE.TABLE_NAME = SYSCOLUMNS.TNAME
                AND SYSTABLE.TABLE_NAME = '{table}'
            ORDER BY 1
        """

        try:
            cursor.execute(query)
            header = [i[0] for i in cursor.description]
            rows = cursor.fetchall()

            result = {}
            cont = 0
            for row in rows:
                result[cont] = dict(zip(header, row))
                cont += 1
                
            return result

        except:
            return False