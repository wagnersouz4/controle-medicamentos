# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])


## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True


#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
Pacientes = db.define_table('pacientes',
                            Field('nome'),
                            Field('instituicao','reference auth_user',label='Instituição'),
                            Field('rg',label='RG'),
                            Field('cpf',unique=True,label='CPF'),
                            Field('data_nascimento','date',label='Data de nascimento'),
                            Field('peso','double'),
                            Field('altura','double'))
                            
Pacientes.nome.requires = IS_NOT_EMPTY()
Pacientes.altura.requires = IS_NOT_EMPTY()
Pacientes.peso.requires = IS_NOT_EMPTY()
Pacientes.data_nascimento.requires = [IS_NOT_EMPTY(),IS_DATE()]

Medicamentos = db.define_table('medicamentos', 
                                Field('farmaco',label='Fármaco'),
                                Field('detentor'),
                                Field('classificacao',label='Classificação'),
                                Field('concentracao', label='Concentração'),
                                Field('medicamento_referencia',label='Medicamento de referência'),
                                Field('forma_farmaceutica', label='Forma farmacêutica'))

Medicamentos.farmaco.requires = IS_NOT_EMPTY()
Medicamentos.detentor.requires = IS_NOT_EMPTY()
Medicamentos.classificacao.requires = IS_NOT_EMPTY()
Medicamentos.concentracao.requires = IS_NOT_EMPTY()
Medicamentos.medicamento_referencia.requires = IS_NOT_EMPTY()
Medicamentos.forma_farmaceutica.requires = IS_NOT_EMPTY()

class IS_TIME_LIST(object):
    def __init__(self, error_message="Horario %s é inválido.", sep=","):
        self.error_message = error_message
        self.sep = sep

    def __call__(self, value):
            print value
            times = value.strip().replace('\n','').replace('\t','').split(self.sep)
            for time in times:
                time = time.strip()
                if IS_TIME()(time)[1]!= None:
                    return (time, self.error_message % time)
            return (times, None)

Estoque = db.define_table('estoque',
                           Field('id_instituicao', 'reference auth_user'),
                           Field('id_medicamento',db.medicamentos),
                           Field('quantidade', 'integer'))
                           
Estoque.quantidade.requires = [IS_NOT_EMPTY(), IS_LENGTH(minsize=0)]
Estoque.id_medicamento.requires = IS_IN_DB(db, 'medicamentos.id', '%(farmaco)s %(concentracao)s',
                                 zero=T('Escolha um'))

PacienteMedicamento = db.define_table('paciente_medicamento',
                                       Field('id_paciente', 'reference pacientes'),
                                       Field('id_medicamento', 'reference medicamentos'),
                                       Field('horarios', 'list:string'),
                                       Field('posologia'))
                                       
PacienteMedicamento.id_paciente.requires = IS_IN_DB(db,'pacientes.id','%(nome)s')   
PacienteMedicamento.id_medicamento.requires = IS_IN_DB(db,'medicamentos.id','%(farmaco)s')                                    
PacienteMedicamento.posologia.requires = IS_NOT_EMPTY()
PacienteMedicamento.horarios.requires = IS_TIME_LIST()
