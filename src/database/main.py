from sqlite3 import connect
from os.path import exists
from os import remove
from os import system

from Sybase import Sybase

database_def = '..\\database\\def.db'

# lista com tabelas que serão exportadas
table_list = [
    'CTCCUSTO',
    'CTCONTAS',
    'CTDEPTO',
    'CTHISPAD',
    'EFCLIENTES',
    'EFFORNECE',
    'FOAFASTAMENTOS',
    'FOAFASTAMENTOS_ENVIOS_ESOCIAL',
    'FOAFASTAMENTOS_IMPORTACAO',
    'FOAGENTES_INTEGRACAO',
    'FOAGENTES_INTEGRACAO_ALTERACAO',
    'FOALTESAL',
    'FOALTESAL_IMPORTACAO',
    'FOBANCOS',
    'FOBASESIRRF',
    'FOBASESSERV',
    'FOBASESSERVIRRF',
    'FOCARGOS',
    'FOCARGOS_ALTERACAO_ENVIOS_ESOCIAL',
    'FOCARGOS_ENVIOS_ESOCIAL',
    'FOCAT',
    'FOCCUSTOS',
    'FOCODIGOS_TERCEIROS',
    'FOCONTRRPA',
    'FOCONTRRPAIRRF',
    'FOCONTRRPASERV',
    'FOCOORDENADOR_ESTAGIO',
    'FOCOORDENADOR_ESTAGIO_ALTERACAO',
    'FODEPTO',
    'FOEMPREGADOS',
    'FOEMPREGADOS_ATESTADOS_OCUPACIONAIS',
    'FOEMPREGADOS_CERTIDAO_CIVIL',
    'FOEMPREGADOS_CONSELHOS_REGIONAIS',
    'FOEMPREGADOS_DADOS_EVENTOS_ESOCIAL',
    'FOEMPREGADOS_ENVIOS_ESOCIAL',
    'FOEMPREGADOS_PLANO_SAUDE',
    'FOEMPREGADOS_TRANSF',
    'FOEMPREG_CONTRSIND',
    'FOESOCIAL_DADOS_EVENTOS',
    'FOESOCIAL_LOTES',
    'FOESOCIAL_LOTES_ENVIOS',
    'FOFERIAS_AQUISITIVOS',
    'FOFERIAS_COLETIVAS',
    'FOFERIAS_GOZO',
    'FOFERIAS_GOZO_DIASDESCONSIDERAR',
    'FOFERIAS_GOZO_TIPO',
    'FOFILHOS',
    'FOFILHOS_PLANO_SAUDE',
    'FOFILIAIS',
    'FOFILIAIS_FAP',
    'FOFILIAIS_SINDICATOS_PATRONAIS',
    'FOFUNCOES',
    'FOHORAFOLHA',
    'FOHORAFOLHASEM',
    'FOHORARIOS',
    'FOHORARIOS_ALTERACAO_ENVIOS_ESOCIAL',
    'FOHORARIOS_INTERVALOS',
    'FOINSTITUICAO_ENSINO',
    'FOINSTITUICAO_ENSINO_ALTERACAO',
    'FOJORNADAS',
    'FOJORNADAS_HORARIOS',
    'FOMEDICOS',
    'FOMEDIDAS_PROTECAO_EMPREGO_COVID_19',
    'FOMEDIDAS_PROTECAO_EMPREGO_COVID_19_AFASTAMENTOS',
    'FOOPERADORAPLANOSAUDE',
    'FOPARMTO',
    'FOPARMTO_ALTERACAO',
    'FOPARMTO_ALTERACAO_ENVIOS_ESOCIAL',
    'FOPARMTO_CONFIGURACAO_DATA_PAGAMENTO',
    'FOPARMTO_ENVIOS_ESOCIAL',
    'FORESCISOES',
    'FORESCISOES_ENVIOS_ESOCIAL',
    'FOSERVICOS',
    'FOSINDICATOS',
    'FOSINDICATOSPATRONAL',
    'FOSINDICATOS_EMPRESAS',
    'FOTABCALCFAP',
    'FOTABCALC_PATRONAL',
    'FOTABCALC_PATRONAL_FAIXAS',
    'FOTABELAS',
    'FOTROCAS_CAMPOS',
    'FOTROCAS_CAMPOS_IMPORTACAO',
    'FOTROCAS_CARGOS',
    'FOTROCAS_CARGOS_IMPORTACAO',
    'FOTROCAS_CCUSTOS',
    'FOTROCAS_CCUSTOS_IMPORTACAO',
    'FOTROCAS_DEPTO',
    'FOTROCAS_DEPTO_IMPORTACAO',
    'FOTROCAS_FUNCOES',
    'FOTROCAS_HORAFOLHA_IMPORTACAO',
    'FOTROCAS_HORAS',
    'FOTROCAS_JORNADAS',
    'FOTROCAS_JORNADAS_IMPORTACAO',
    'FOTROCAS_SERVICOS',
    'FOTROCAS_SERVICOS_IMPORTACAO',
    'FOTROCAS_SINDICATOS',
    'FOTROCAS_SINDICATOS_IMPORTACAO',
    'FOVIGENCIAS_SERVICO',
    'FOVIGENCIAS_SERVICO_ENVIOS_ESOCIAL',
    'FOVIGENCIA_REGIME',
    'FOVIGENCIA_UNIDADE_CALCULO',
    'GEATVSECUNDARIA',
    'GEATVSECUNDARIA_VIGENCIA',
    'GECONTADOR',
    'GEEMPRE',
    'GEQUADROSOCIETARIO',
    'GEQUADROSOCIETARIO_SOCIOS',
    'GESOCIOS',
    'FOEVENTOS',
    'FOLANCTOMEDIAS'
]


# cria a estrutura das tabelas no banco SQLite
def create_tables(bancoDados):
    if exists(bancoDados):
        remove(bancoDados)

    conexao = connect(bancoDados)
    cursor = conexao.cursor()

    for table in table_list:

        cursor.execute(f"""
            CREATE TABLE {table} (
                CAMPO_ID INTEGER,
                CAMPO_NOME VARCHAR(128),
                CAMPO_DESCRICAO VARCHAR(128),
                CAMPO_TIPO VARCHAR(128),
                CAMPO_TAMANHO INTEGER,
                CAMPO_DECIMAL INTEGER,
                CAMPO_PRIMARIA VARCHAR(1),
                CAMPO_NULO VARCHAR(1),
                CAMPO_PADRAO VARCHAR(128)
            )
        """)

    conexao.commit()
    conexao.close()


# Insere os dados extraidos da Domínio no banco SQLite
def insert_data(databasedef, database, username, password):
    conexao = connect(databasedef)
    cursor = conexao.cursor()

    sybase = Sybase(database, username, password)
    sybase_connection = sybase.connect()

    if not sybase_connection:
        print('Erro na conexão com banco de dados Domínio!')
        return

    for table in table_list:
        table_columns = sybase.select_def_table(sybase_connection, table)

        for index in table_columns:
            valor_padrao = str(table_columns[index]['CAMPO_PADRAO']).replace('"NEWID"()','')
            cursor.execute(f"""INSERT INTO {table} (CAMPO_ID, 
                                                    CAMPO_NOME,
                                                    CAMPO_DESCRICAO,
                                                    CAMPO_TAMANHO,
                                                    CAMPO_DECIMAL,
                                                    CAMPO_PRIMARIA,
                                                    CAMPO_NULO,
                                                    CAMPO_PADRAO)
                               VALUES ({int(table_columns[index]['CAMPO_ID'])}, 
                               '{str(table_columns[index]['CAMPO_NOME']).upper()}',
                               '{table_columns[index]['CAMPO_DESCRICAO']}',
                               {table_columns[index]['CAMPO_TAMANHO']},
                               {table_columns[index]['CAMPO_DECIMAL']},
                               '{table_columns[index]['CAMPO_PRIMARIA']}',
                               '{table_columns[index]['CAMPO_NULO']}',
                               '{valor_padrao}')
                            """)
            
    conexao.commit()
    conexao.close()
    return True


# Atualiza os campos da DEF caso tenha mudado
def update_data(databasedef, database, username, password):
    conexao = connect(databasedef)
    cursor = conexao.cursor()
        
    sybase = Sybase(database, username, password)
    sybase_connection = sybase.connect()

    if not sybase_connection:
        return False

    for table in table_list:
        table_columns = sybase.select_def_table(sybase_connection, table)

        for index in table_columns:
            valor_padrao = table_columns[index]['CAMPO_PADRAO']
            

            cursor.execute(f"""UPDATE {table} SET CAMPO_ID = {int(table_columns[index]['CAMPO_ID'])},
                               CAMPO_NOME = '{table_columns[index]['CAMPO_NOME']}',
                               CAMPO_DESCRICAO = '{table_columns[index]['CAMPO_DESCRICAO']}',
                               CAMPO_TAMANHO = {table_columns[index]['CAMPO_TAMANHO']},
                               CAMPO_DECIMAL = {table_columns[index]['CAMPO_DECIMAL']},
                               CAMPO_PRIMARIA = '{table_columns[index]['CAMPO_PRIMARIA']}',
                               CAMPO_NULO = '{table_columns[index]['CAMPO_NULO']}',
                               CAMPO_PADRAO = '{valor_padrao}'
                               WHERE CAMPO_NOME = '{table_columns[index]['CAMPO_NOME']}'
                            """)
   
    conexao.commit()
    conexao.close()
    return True


def main(opcao):
    
    database = input('Informe o nome do banco Domínio: ')
    username = input('Informe o usuário externo: ')
    password = input('Informe a senha do usuário externo: ')

    if opcao == 1:
        create_tables(database_def)
        insert_data(database_def, database, username, password)
        system('echo Processo finalizado, pressione qualquer tecla para encerrar...')
        system('pause > nul')
    elif opcao == 2:
        update_data(database_def, database, username, password)
        system('echo Processo finalizado, pressione qualquer tecla para encerrar...')
        system('pause > nul')


def menu():
    print('Você deseja realizar qual ação?')
    print('1 - Recriar DEF(adicionou tabelas novas)')
    print('2 - Atualizar DEF')
    opcao = input('selecione um opção: ')

    return int(opcao)


if __name__ == '__main__':
    opcao = menu()
    main(opcao)
