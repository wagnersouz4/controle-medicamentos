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

#Criando funções de validação

#Validação para CEP
class IS_VALID_CEP(object):
    def __init__(self, error_message=T('CEP INVÁLIDO')):
        self.error_message=error_message
        
    def __call__(self, value):
        error=None
        cep_temp = []
        try:
            #Coletando todos os números
            for cp in value:
                if cp.isdigit():
                    cep_temp.append(cp)
            if len(cep_temp) == 8:
                return (self.to_cep(cep_temp), None)
            error = self.error_message
            return (value, error)
        except e:
            self.error_message = e
            return(value, self.error_message)
        
    #Formata para ddddd-ddd
    def to_cep(self, cep):
        return str(cep[0:5])+'-'+str(cep[5:])

#Validação CNPJ
class IS_VALID_CNPJ(object):
    def __init__(self, error_message=T('CNPJ INVÁLIDO')):
        self.error_message = error_message
        
    def __call__(self, value):
        error=None
        
        if len(value) != 14:
            return(value, self.error_message)
           
        digito1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        digito2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        
        mul_digito1 = []
        
        for i,j in zip(value[:12],digito1):
            mul_digito1.append(int(i)*j)
        
        #somando valores
        sum_digito1 = 0
        for i in mul_digito1:
            sum_digito1 = sum_digito1 + i
            
        resto = sum_digito1%11
        if resto<2:
           digito1 = 0
        else:
           digito1 = 11 - resto
           
        if value[12] !=  digito1:
            return(value, self.error_message)
            
        novo_value = value[:12]+digito1
        
        mult_digito2 = []
        
        for i,j in zip(novo_value,digito2):
            mult_digito2.append(int(i)*j)
       
        sum_digito2 = 0
        for i in mul_digito2:
            sum_digito2 = sum_digito2+i
            
        resto = sum_digito2%11
            
        if resto<2:
            digito2 = 0
        else:
            digito2 = 11 - resto
        
        if value[13] == digito2:
            return(value, None)
        else:
            return (value, self.error_message)
         
            
           
       
        
        

#Adicionando campos extras na table auth_user
auth.settings.extra_fields['auth_user']= [
    Field("endereco", label='Endereço'),
    Field("cidade", length=100),
    Field("cep", length=9, label='CEP'),
    Field("telefone", length=13),
    Field("cnpj", length=18, label='CNPJ'),
    Field("pais", length=6, default='Brasil', label='País')]

#Campos que irão aparecer na tela de registro
auth.settings.register_fields = [
    'first_name', 'email', 'password', 'telefone', 'endereco', 
    'cidade', 'cep', 'pais', 'cnpj']

## create all tables needed by auth if not custom tables    
auth.define_tables(username=False, signature=False)

#Aterando nomes de campos default da tabela auth_user
db.auth_user.first_name.label = "Instituição"

#Criando validações
db.auth_user.endereco.requires = IS_NOT_EMPTY()
db.auth_user.cidade.requires = IS_NOT_EMPTY()
db.auth_user.cep.requires = [IS_NOT_EMPTY(), IS_VALID_CEP()]
db.auth_user.telefone.requires = IS_NOT_EMPTY()
db.auth_user.cnpj.requires = [IS_NOT_EMPTY(), IS_VALID_CNPJ()]
db.auth_user.pais.requires = IS_NOT_EMPTY()
