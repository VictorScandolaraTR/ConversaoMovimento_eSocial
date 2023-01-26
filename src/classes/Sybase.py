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
        

    def select(self, connection, query):
        cursor = connection.cursor()

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

    
    def select_empresas(self, connection):
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT codi_emp, cgce_emp FROM BETHADBA.GEEMPRE')
            rows = cursor.fetchall()

            result = {}
            for row in rows:
                result[row[1]] = row[0]
                
            return result

        except:
            return False

    
    def select_rubrics(self, connection):
        cursor = connection.cursor()

        try: 
            # extrair rúbricas da empresa
            cursor.execute('SELECT CODI_EMP, I_EVENTOS FROM BETHADBA.FOEVENTOS ORDER BY 1, 2')
            rows = cursor.fetchall()

            result = {}
            for row in rows:
                if row[0] not in result.keys():
                    result[row[0]] = []
                    result[row[0]].append(row[1])
                else:
                    result[row[0]].append(row[1])
            

            # como as empresas podem utilizar eventos de outras empresas é necessário 
            # validar se a empresa possui essa configuração e coletar o código dessa empresa também
            cursor.execute('SELECT CODI_EMP, CODI_EMP_EVE FROM BETHADBA.FOPARMTO')
            rows = cursor.fetchall()

            for row in rows:
                if row[1]:
                    if row[0] not in result.keys():
                        result[row[0]] = result[row[1]]
                    else:
                        result[row[0]] += result[row[1]]

            return result

        except:
            return False

    
    def close_connection(self, connection):
        connection.close()
        return
