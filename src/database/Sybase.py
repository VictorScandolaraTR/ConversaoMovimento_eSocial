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

    def select_data_rubrics(self, connection, default_rubric):
        """
        Seleciona todos os dados das rúbricas de uma empresa da domínio(rubricas, bases de cálculo e formulas)
        """
        cursor = connection.cursor()

        cursor.execute(f"SELECT * FROM BETHADBA.FOEVENTOS WHERE CODI_EMP IN ('{default_rubric}') ORDER BY 1, 2")
        header = [i[0].upper() for i in cursor.description]
        rows = cursor.fetchall()

        rubrics = {}
        for row in rows:
            data = dict(zip(header, row))

            if data['NATUREZA_FOLHA_MENSAL'] not in rubrics.keys():
                rubrics[data['NATUREZA_FOLHA_MENSAL']] = [dict(zip(header, row))]
            else:
                rubrics[data['NATUREZA_FOLHA_MENSAL']].append(dict(zip(header, row)))

        # coletar bases de cálculo
        cursor.execute(f"SELECT * FROM BETHADBA.FOEVENTOSBASES WHERE CODI_EMP IN ('{default_rubric}')")
        header = [i[0].upper() for i in cursor.description]
        rows = cursor.fetchall()

        rubrics_base_calc = {}
        for row in rows:
            data = dict(zip(header, row))

            if data['I_EVENTOS'] not in rubrics_base_calc.keys():
                rubrics_base_calc[data['I_EVENTOS']] = [dict(zip(header, row))]
            else:
                rubrics_base_calc[data['I_EVENTOS']].append(dict(zip(header, row)))

        # coletar bases de cálculo
        cursor.execute(f"""SELECT * FROM BETHADBA.FOFORMULAS WHERE CODI_EMP IN ('{default_rubric}')""")
        header = [i[0].upper() for i in cursor.description]
        rows = cursor.fetchall()

        rubrics_formula = {}
        for row in rows:
            data = dict(zip(header, row))

            new_row = {}
            for key in data:
                value = data[key]
                if key == 'SCRIPT':
                    while True:
                        if '\r' in value:
                            value = str(value).replace('\r', '')
                        if '\n' in value:
                            value = str(value).replace('\n', '')
                        else:
                            break

                new_row[key] = value

            if data['I_EVENTOS'] not in rubrics_formula.keys():
                rubrics_formula[data['I_EVENTOS']] = new_row

        return rubrics, rubrics_base_calc, rubrics_formula

    def select_rubrics_averages(self, connection, default_rubric):
        """
        Seleciona quais rubricas de uma empresa da Domínio entram para médias
        """
        cursor = connection.cursor()

        cursor.execute(f"""SELECT I_EVENTOS 
                                    FROM BETHADBA.FOEVENTOS 
                                    WHERE CODI_EMP IN ('{default_rubric}') AND (
                                            SOMA_MEDIA_AVISO_PREVIO = 1 OR
                                            soma_med_13 = 'S' OR
                                            soma_med_fer = 'S' OR
                                            SOMA_MEDIA_LICENCA_PREMIO = 1 OR
                                            soma_med_afast = 'S' OR
                                            SOMA_MEDIA_SALDO_SALARIO = 1
                                    )""")
        rows = cursor.fetchall()

        rubrics_medias = []
        for row in rows:
            rubrics_medias.append(str(row[0]))

        return rubrics_medias

    def select_companies_to_use_rubrics(self, connection):
        """
        Seleciona de qual empresa a empresa usa rubricas
        """
        cursor = connection.cursor()

        result = {}
        cursor.execute('SELECT CODI_EMP, CODI_EMP_EVE FROM BETHADBA.FOPARMTO')
        rows = cursor.fetchall()

        for row in rows:
            codi_emp = row[0]
            codi_emp_eventos = row[1]

            if codi_emp_eventos:
                if codi_emp not in result.keys():
                    result[codi_emp] = codi_emp_eventos
            else:
                if codi_emp not in result.keys():
                    result[codi_emp] = codi_emp

        return result

    def select_rubrics(self, connection):
        """
        Cria um dicionário com os codigos das rubricas que as empresas
        já possuem
        """
        cursor = connection.cursor()

        cursor.execute('SELECT CODI_EMP, I_EVENTOS FROM BETHADBA.FOEVENTOS ORDER BY 1, 2')
        rows = cursor.fetchall()

        result = {}
        for row in rows:
            codi_emp = int(row[0])
            i_eventos = row[1]
            if codi_emp not in result.keys():
                result[codi_emp] = []

            result[codi_emp].append(i_eventos)

        return result

    def select_codigo_esocial_rubrics(self, connection):
        """
        Seleciona os códigos esocial de rúbricas já ocupados no banco.
        Necessário fazer isso pois a crição do código eSocial é obrigatória e ele
        deve ser gerado levando em conta a raiz CNPJ da empresa, não podendo ter
        o mesmo código eSocial para empresas com raiz CNPJ igual.
        """
        cursor = connection.cursor()

        query = 'SELECT (SELECT CGCE_EMP FROM BETHADBA.GEEMPRE WHERE GEEMPRE.CODI_EMP = FOEVENTOS.CODI_EMP) as CNPJ, CODIGO_ESOCIAL FROM BETHADBA.FOEVENTOS'
        cursor.execute(query)
        rows = cursor.fetchall()

        result = {}
        for row in rows:
            cgce_emp = str(row[0])
            codigo_esocial = row[1]

            if len(cgce_emp) > 12:
                cnpj_root = cgce_emp[0:8]
            else:
                cnpj_root = cgce_emp

            if cnpj_root not in result.keys():
                result[cnpj_root] = []

            result[cnpj_root].append(codigo_esocial)

        return result

    def select_cnpj_companies(self, connection):
        """
        Seleciona os CNPJs das empresas
        """
        cursor = connection.cursor()

        cursor.execute('SELECT CODI_EMP, CGCE_EMP FROM BETHADBA.GEEMPRE')
        rows = cursor.fetchall()

        result = {}
        for row in rows:
            codi_emp = int(row[0])
            cgce_emp = row[1]
            if codi_emp not in result.keys():
                result[codi_emp] = cgce_emp

        return result
