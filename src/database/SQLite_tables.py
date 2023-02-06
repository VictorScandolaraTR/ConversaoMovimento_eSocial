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
    codi_emp = peewee.IntegerField(null=True)
    i_empregados = peewee.IntegerField(null=True)
    competencia = peewee.DateField(null=True)
    inicio_aquisitivo = peewee.DateField(null=True)
    fim_aquisitivo = peewee.DateField(null=True)
    inicio_gozo = peewee.DateField(null=True)
    fim_gozo = peewee.DateField(null=True)
    abono_paga = peewee.CharField(null=True)
    inicio_abono = peewee.DateField(null=True)
    fim_abono = peewee.DateField(null=True)
    data_pagamento = peewee.DateField(null=True)
    rubrica = peewee.IntegerField(null=True)
    valor_informado = peewee.FloatField( null=True)
    valor_calculado = peewee.FloatField(null=True)

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
