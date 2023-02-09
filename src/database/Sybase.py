from pyodbc import connect
from src.utils.functions import *

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

    def select_dependents(self, connection):
        """
        Seleciona os dependentes que não possuem data de nascimento preenchida
        """
        cursor = connection.cursor()

        try:
            cursor.execute(f"""SELECT
                                CODI_EMP,
                                I_EMPREGADOS,
                                I_FILHOS,
                                NOME
                            FROM bethadba.fofilhos
                            WHERE data_nascto is null
                            """)

            header = [i[0] for i in cursor.description]
            rows = cursor.fetchall()

            result = []
            if len(rows) > 0:
                for row in rows:
                    result.append(dict(zip(header, row)))

                return result
            else:
                return False

        except:
            return False

    def select_services(self, connection):
        """
        Seleciona os serviços que estão vinculados a algum empresa e que
        não possuem o campo FPAS preenchido
        """
        cursor = connection.cursor()

        try:
            cursor.execute(f"""SELECT
                                    S.CODI_EMP,
                                    S.I_SERVICOS,
                                    S.VIGENCIA,
                                    S.CGC
                                FROM bethadba.FOVIGENCIAS_SERVICO AS S
                                WHERE S.CODIGO_FPAS = '' AND EXISTS(
                                                                    SELECT 1
                                                                    FROM bethadba.FOEMPREGADOS AS E
                                                                    WHERE S.CODI_EMP = E.CODI_EMP AND
                                                                          S.I_SERVICOS = E.I_SERVICOS)
                                ORDER BY 1, 2, 3
                            """)

            header = [i[0] for i in cursor.description]
            rows = cursor.fetchall()

            result = []
            if len(rows) > 0:
                for row in rows:
                    result.append(dict(zip(header, row)))

                return result
            else:
                return False

        except:
            return False

    def select_invalid_resp_leval(self, connection):
        """
        Seleciona as empresas que são do tipo CPF e que não possuem responsável legal informado
        """
        cursor = connection.cursor()

        try:
            cursor.execute("""SELECT CODI_EMP
                              FROM BETHADBA.GEEMPRE
                              WHERE TINS_EMP = 2 AND 
                              (CPF_LEG_EMP = '' OR CPF_LEG_EMP IS NULL)
                           """)

            header = [i[0] for i in cursor.description]
            rows = cursor.fetchall()

            result = []
            if len(rows) > 0:
                for row in rows:
                    result.append(dict(zip(header, row)))

                return result
            else:
                return False
        except:
            return False

    def close_connection(self, connection):
        connection.close()
        return

    def select_rubrics_generated(self, connection, company_filter, competence_filter):
        cursor = connection.cursor()

        query = f"""SELECT FOMOVTOSERV.CODI_EMP AS CP_EMPRESA,
	                   FOMOVTOSERV.I_EMPREGADOS AS CP_EMPREGADO,
                       FOMOVTOSERV.DATA AS CP_DATA,
                       (SELECT FOBASES.data_pagto 
                        FROM BETHADBA.FOBASES AS FOBASES
                        WHERE FOMOVTOSERV.CODI_EMP IN(FOBASES.CODI_EMP) AND 
                              FOMOVTOSERV.I_EMPREGADOS IN(FOBASES.I_EMPREGADOS) AND 
                              FOMOVTOSERV.DATA IN(FOBASES.competencia) AND 
                              FOMOVTOSERV.TIPO_PROCES IN(FOBASES.TIPO_PROCESS)) AS CP_DATA_PAGAMENTO,
	                   FOMOVTOSERV.TIPO_PROCES AS CP_PROCESSO,
                       FOMOVTOSERV.I_EVENTOS AS CP_EVENTO,
                       FOMOVTOSERV.VALOR_INF AS CP_VALOR_INFORMADO,
                       FOMOVTOSERV.RATEIO AS CP_RATEIO,
		               FOMOVTOSERV.ORIGEM AS CP_ORIGEM,
                       FOMOVTOSERV.I_CALCULOS AS CP_CALCULO,
                       CP_RESCISAO = CASE WHEN (SELECT 1 
                                                FROM BETHADBA.forescisoes AS forescisoes 
                                                WHERE forescisoes.codi_emp = CP_EMPRESA AND
                                                      forescisoes.i_empregados = CP_EMPREGADO AND
                                                      forescisoes.I_CALCULOS = CP_CALCULO) = 1 THEN 'TRUE'
                          ELSE 'FALSE' END
                    FROM BETHADBA.FOMOVTOSERV AS FOMOVTOSERV
                    WHERE NOT EXISTS (SELECT 1 
                                      FROM BETHADBA.FOLANCAMENTOS_EVENTOS 
                                      WHERE FOLANCAMENTOS_EVENTOS.CODI_EMP IN(CP_EMPRESA) AND 
                                            FOLANCAMENTOS_EVENTOS.I_EMPREGADOS IN(CP_EMPREGADO) AND 
                                            FOLANCAMENTOS_EVENTOS.COMPETENCIA_INICIAL IN(CP_DATA) AND 
                                            FOLANCAMENTOS_EVENTOS.TIPO_PROCESSO IN(CP_PROCESSO) AND 
                                            FOLANCAMENTOS_EVENTOS.I_EVENTOS IN(CP_EVENTO))
                    AND CP_PROCESSO IN (51, 41, 52, 11, 70, 42)
                    AND CP_EMPRESA IN ('{company_filter}')
                    AND CP_ORIGEM NOT IN ('F')
                    AND CP_RATEIO IN ('0')
                    AND CP_EVENTO NOT IN ('9176', '9177', '9178')
                    ORDER BY CP_EMPRESA, CP_EMPREGADO, CP_DATA, CP_PROCESSO
                """

        query_vacation = f"""SELECT FOMOVTOSERV.CODI_EMP AS CP_EMPRESA,
		                    FOMOVTOSERV.I_EMPREGADOS AS CP_EMPREGADO,
                            FOMOVTOSERV.DATA AS CP_DATA,
                            CP_DATA_PAGAMENTO = (SELECT FOBASES.data_pagto
                                                 FROM BETHADBA.FOBASES AS FOBASES
                                                 WHERE FOMOVTOSERV.CODI_EMP IN(FOBASES.CODI_EMP) AND
                                                       FOMOVTOSERV.I_EMPREGADOS IN(FOBASES.I_EMPREGADOS) AND 
                                                       FOMOVTOSERV.DATA IN(FOBASES.competencia) AND 
                                                       FOMOVTOSERV.TIPO_PROCES IN(FOBASES.TIPO_PROCESS) 
								                ),
                            FOMOVTOSERV.TIPO_PROCES AS CP_PROCESSO,
                            FOMOVTOSERV.I_EVENTOS AS CP_EVENTO,
                            FOMOVTOSERV.VALOR_INF AS CP_VALOR_INFORMADO,
                            FOMOVTOSERV.RATEIO AS CP_RATEIO,
                            CP_GOZO = (SELECT FOFERIAS_GOZO.I_FERIAS_GOZO
		                               FROM BETHADBA.FOFERIAS_GOZO AS FOFERIAS_GOZO
                                       WHERE FOFERIAS_GOZO.CODI_EMP = CP_EMPRESA AND
                                                                      FOFERIAS_GOZO.I_EMPREGADOS = CP_EMPREGADO AND
                                                                      CP_DATA >= FOFERIAS_GOZO.GOZO_INICIO AND
                                                                      CP_DATA <= FOFERIAS_GOZO.GOZO_FIM),
                            CP_INICIO_GOZO = (SELECT FOFERIAS_GOZO.GOZO_INICIO
		                               FROM BETHADBA.FOFERIAS_GOZO AS FOFERIAS_GOZO
                                       WHERE FOFERIAS_GOZO.CODI_EMP = CP_EMPRESA AND
                                                                      FOFERIAS_GOZO.I_EMPREGADOS = CP_EMPREGADO AND
                                                                      CP_DATA >= FOFERIAS_GOZO.GOZO_INICIO AND
                                                                      CP_DATA <= FOFERIAS_GOZO.GOZO_FIM)
                            FROM BETHADBA.FOMOVTOSERV AS FOMOVTOSERV
                            WHERE NOT EXISTS (SELECT 1 
                                              FROM BETHADBA.FOFERIAS_LANCAMENTOS
                                              WHERE FOFERIAS_LANCAMENTOS.CODI_EMP IN(CP_EMPRESA) AND 
                                                    FOFERIAS_LANCAMENTOS.I_EMPREGADOS IN(CP_EMPREGADO) AND
                                                    FOFERIAS_LANCAMENTOS.I_FERIAS_GOZO IN(CP_GOZO) AND 
                                                    FOFERIAS_LANCAMENTOS.I_EVENTOS IN(CP_EVENTO))
                                  AND CP_PROCESSO IN (60, 61)
                                  AND CP_EMPRESA IN ('{company_filter}')
                                  AND CP_EVENTO NOT IN ('9178')
                                  AND CP_INICIO_GOZO IS NOT NULL
                            ORDER BY CP_EMPRESA, CP_EMPREGADO, CP_DATA, CP_PROCESSO
                        """

        # dados de calculo de folhas
        cursor.execute(query)
        rows = cursor.fetchall()

        result = {}
        for row in rows:
            competence = row[2].strftime('%d/%m/%Y')
            payment_day = row[3].strftime('%Y-%m-%d')

            if competence == competence_filter:
                if row[10] == 'FALSE':
                    if int(row[4]) not in result.keys():
                        result[int(row[4])] = {}
                    if payment_day not in result[int(row[4])].keys():
                        result[int(row[4])][payment_day] = []

                    if int(row[1]) not in result[int(row[4])][payment_day]:
                        result[int(row[4])][payment_day].append(int(row[1]))
                else:
                    if int(row[4]) == 42:
                        if 42 not in result.keys():
                            result[42] = []

                        if int(row[1]) not in result[42]:
                            result[42].append(int(row[1]))
                    else:
                        if 100 not in result.keys():
                            result[100] = []

                        if int(row[1]) not in result[100]:
                            result[100].append(int(row[1]))

        # dados de calculo de férias
        cursor.execute(query_vacation)
        rows = cursor.fetchall()

        for row in rows:
            competence = datetime.strftime(row[9], '%d/%m/%Y')
            competence = datetime.strptime(competence, '%d/%m/%Y').replace(day=1)
            competence = datetime.strftime(competence, '%d/%m/%Y')
            inicio_gozo_converted = format_date(row[9], '%Y-%m-%d')

            if competence == competence_filter:
                i_empregados = int(row[1])
                if 60 not in result.keys():
                    result[60] = {}
                if i_empregados not in result[60].keys():
                    result[60][i_empregados] = []

                data = {'inicio_gozo': inicio_gozo_converted}
                if data not in result[60][i_empregados]:
                    result[60][i_empregados].append(data)

        return result

    def select_gozo_ferias(self, connection):
        cursor = connection.cursor()
        query = """SELECT CODI_EMP,
	                   I_EMPREGADOS,
                       GOZO_INICIO,
                       I_FERIAS_GOZO,
                       INICIO_AQUISITIVO
                    FROM BETHADBA.FOFERIAS_GOZO
                """

        try:
            cursor.execute(query)
            rows = cursor.fetchall()

            result = {}
            for row in rows:
                init_aqui = row[4].strftime('%d/%m/%Y')
                init_gozo = row[2].strftime('%d/%m/%Y')

                if int(row[0]) not in result.keys():
                    result[int(row[0])] = {}
                if int(row[1]) not in result[int(row[0])].keys():
                    result[int(row[0])][int(row[1])] = {}
                if init_gozo not in result[int(row[0])][int(row[1])].keys():
                    result[int(row[0])][int(row[1])][init_gozo] = {
                        'i_ferias_gozo': int(row[3]),
                        'inicio_aquisitivo': init_aqui
                    }

            return result

        except:
            return False

    def select_acquisition_data(self, connection, company, employee):
        cursor = connection.cursor()
        query = f"""
            SELECT TOP 1 DATA_FIM
            FROM BETHADBA.FOFERIAS_AQUISITIVOS
            WHERE CODI_EMP = '{company}' AND I_EMPREGADOS = '{employee}' AND SITUACAO != '3'
            ORDER BY DATA_INICIO
        """

        try:
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                end_acquisition = datetime.strftime(row[0], '%d/%m/%Y')
                return end_acquisition

        except:
            return False

    def select_data_vacation(self, connection):
        cursor = connection.cursor()

        try:
            # extrair gozos de férias
            cursor.execute("""SELECT CODI_EMP, 
                                    I_EMPREGADOS, 
                                    (SELECT MAX(I_FERIAS_GOZO) 
                                    FROM BETHADBA.FOFERIAS_GOZO AS TABLE02 
                                    WHERE TABLE01.CODI_EMP = TABLE02.CODI_EMP AND 
                                            TABLE01.I_EMPREGADOS = TABLE02.I_EMPREGADOS)
                            FROM BETHADBA.FOFERIAS_GOZO AS TABLE01
                            GROUP BY CODI_EMP, I_EMPREGADOS
                            ORDER BY CODI_EMP, I_EMPREGADOS
            """)
            rows = cursor.fetchall()

            result = {}
            for row in rows:
                if str(row[0]) not in result.keys():
                    result[str(row[0])] = {}

                if str(row[1]) not in result[str(row[0])].keys():
                    result[str(row[0])][str(row[1])] = int(row[2])

            return result

        except:
            return False

    def select_users(self, connection, base_name):
        cursor = connection.cursor()

        try:
            cursor.execute(f"SELECT i_confusuario FROM bethadba.usConfUsuario WHERE i_usuario like '{base_name}%'")
            rows = cursor.fetchall()

            result = []
            for row in rows:
                result.append(row[0])

            return result

        except:
            return False

    def select_employees(self, connection):
        """
        Seleciona os CPFs dos empregados do banco
        """
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT CODI_EMP, I_EMPREGADOS, CPF FROM BETHADBA.FOEMPREGADOS')

            header = [i[0] for i in cursor.description]
            rows = cursor.fetchall()

            result = []
            for row in rows:
                result.append(dict(zip(header, row)))

            return result
        except:
            return False
