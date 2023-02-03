from src.database.Sybase import Sybase


def get_service(sybase, connection):
    """
    Coleta do banco de dados quais serviços não tem o código
    FPAS preenchido, pois isso impossibilita o cálculo
    """
    result = sybase.select_services(connection)
    result_list = []
    if result:
        for line in result:
            if int(line['CODI_EMP']) not in result_list:
                result_list.append(int(line['CODI_EMP']))

    return result_list


def check_companies_calc(database, username, password):
    """
    Checa se o banco possui algum ponto da parte cadastral errado
    que irá impossibilitar o cálculo
    """
    sybase = Sybase(database, username, password)
    connection = sybase.connect()

    ignore_companies = get_service(sybase, connection)

    return ignore_companies
