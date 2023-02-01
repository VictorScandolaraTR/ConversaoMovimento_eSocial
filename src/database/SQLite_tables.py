import peewee

db = peewee.SqliteDatabase(None)


class DominioRescisao(peewee.Model):
    codi_emp = peewee.IntegerField(null=True)
    i_empregados = peewee.IntegerField(null=True)
    competencia = peewee.DateField(null=True)
    data_demissao = peewee.DateField(null=True)
    motivo = peewee.CharField(max_length=1, null=True)
    data_pagamento = peewee.DateField(null=True)
    aviso_previo = peewee.BooleanField(null=True)
    data_aviso = peewee.DateField(null=True)
    dias_projecao_aviso = peewee.FloatField(null=True)

    class Meta:
        database = db
        db_table = 'dominio_rescisao'

    def connect(self, db_file):
        sqlite_db = peewee.SqliteDatabase(db_file)
        self.bind(sqlite_db)
        try:
            DominioRescisao.create_table()
        except peewee.OperationalError:
            pass


class DominioFerias(peewee.Model):
    codi_emp = peewee.CharField(max_length=4, null=True)
    i_empregados = peewee.CharField(max_length=8, null=True)
    competencia = peewee.CharField(max_length=10, null=True)
    inicio_aquisitivo = peewee.CharField(max_length=10, null=True)
    fim_aquisitivo = peewee.CharField(max_length=10, null=True)
    inicio_gozo = peewee.CharField(max_length=10, null=True)
    fim_gozo = peewee.CharField(max_length=10, null=True)
    abono_paga = peewee.CharField(max_length=1, null=True)
    inicio_abono = peewee.CharField(max_length=10, null=True)
    fim_abono = peewee.CharField(max_length=10, null=True)
    data_pagamento = peewee.CharField(max_length=10, null=True)
    i_eventos = peewee.CharField(max_length=4, null=True)
    valor_informado = peewee.CharField(max_length=20, null=True)
    valor_calculado = peewee.CharField(max_length=20, null=True)

    class Meta:
        database = db
        db_table = 'dominio_ferias'

    def connect(self, db_file):
        sqlite_db = peewee.SqliteDatabase(db_file)
        self.bind(sqlite_db)
        try:
            DominioFerias.create_table()
        except peewee.OperationalError:
            pass
