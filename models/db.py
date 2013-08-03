# -*- coding: utf-8 -*-

#
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
#

# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    # if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite', pool_size=1, check_reserved=['all'])
else:
    # connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    # store sessions and tickets there
    session.connect(request, response, db=db)
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))

# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
# (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
#

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

# configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

# configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True


class IS_CPF(object):

    def __init__(self, format=True, error_message='Digite apenas os números!'):
        self.format = format
        self.error_message = error_message

    def __call__(self, value):

        def valida(value):

            def calcdv(numb):

                result = int()
                seq = reversed(((range(9, id_type[1], -1) * 2)[:len(numb)]))
                # return (value,'to fundo1')
                for digit, base in zip(numb, seq):
                    result += int(digit) * int(base)

                dv = result % 11
                # return (value,'to fundo1'+str(dv))
                return (dv - 10) and dv or 0

            id_type = ['CPF', -1]

            numb, xdv = value[:-2], value[-2:]

            dv1 = calcdv(numb)
            # return (value,'entrei'+str(dv1))
            dv2 = calcdv(numb + str(dv1))
            return (('%d%d' % (dv1, dv2) == xdv and True or False), id_type[0])

        try:
            cpf = str(value)
            # return(cpf,'aquiok'+str(len(cpf)==11))
            if len(cpf) >= 11:

                # return (value, 'cpf acima de 11')
                c = []
                for d in cpf:
                    if d.isdigit():
                        c.append(d)
                cl = str(''.join(c))
                # return (value, 'cpf incorreto'+str(cl))
                if len(cl) == 11:
                    if valida(cl)[0]:
                        return(value, None)
                    else:
                        return (value, 'cpf inválido')
                elif len(cl) < 11:
                    return (value, 'cpf incompleto')
                else:
                    return (value, 'cpf tem mais de 11 dígitos')
                if cpf[3] != '.' or cpf[7] != '.' or cpf[11] != '-':
                    return (value, 'cpf deve estar no formato 00000000000' + cpf[11])
            else:
                return (value, 'cpf deve estar no formato 00000000000')
            # return(cpf,'aquiok'+str(len(cpf)==11))

        except:
            return (value, 'algum erro' + str(value))

    def formatter(self, value):

        formatado = value[0:3] + '.' + value[
            3:6] + '.' + value[6:9] + '-' + value[9:11]
        # formatado = value
        return formatado

Pacientes = db.define_table('pacientes',
                            Field('nome'),
                            Field(
                                'instituicao', 'reference auth_user', label='Instituição'),
                            Field('rg', label='RG'),
                            Field('cpf', 'integer', unique=True, label='CPF'),
                            Field(
                                'data_nascimento', 'date', label='Data de nascimento', widget=SQLFORM.widgets.string.widget),
                            Field('peso', 'double', label='Peso (kg)'),
                            Field('altura', 'double', label='Altura (metros)'))

Pacientes.cpf.requires = IS_CPF()
Pacientes.nome.requires = IS_NOT_EMPTY()
Pacientes.altura.requires = [IS_NOT_EMPTY(), IS_LENGTH(minsize=1)]
Pacientes.peso.requires = [IS_NOT_EMPTY(), IS_LENGTH(minsize=1)]
Pacientes.data_nascimento.requires = [IS_NOT_EMPTY(), IS_DATE(
    format=('%d-%m-%Y'), error_message='Data inválida')]

Medicamentos = db.define_table('medicamentos',
                               Field('farmaco', label='Fármaco'),
                               Field('detentor'),
                               Field('classificacao', label='Classificação'),
                               Field('concentracao', label='Concentração'),
                               Field('medicamento_referencia',
                                     label='Medicamento de referência'),
                               Field('via_administracao',
                                     label='Via de administração'),
                               Field('forma_farmaceutica',
                                     label='Forma farmacêutica'))

vias = ('oral', 'sublingual', 'injetável', 'cutânea', 'nasal',
        'oftálmica', 'auricular', 'pulmonar', 'vaginal', 'retal')
formas = ('comprimido', 'cápsula', 'pastilha', 'drágea', 'pós para reconstituição', 'gotas', 'xarope', 'solução oral', 'suspensão',  # oral
          'comprimidos sublinguais',  # sublingual
          'soluções e suspenções injetáveis',  # injetável
          'soluções tópicas', 'pomadas', 'cremes', 'loção', 'gel', 'adesivo',
          # cutânea
          'spray nasal', '  gotas nasais',  # nasal
          'colírios ofltalmicos', '  pomadas oftalmicas',  # oftamológica
          'gotas auriculares ou otológicas', 'pomadas auriculares',
          # auricular
          'aerossol',  # pulmonar
          'comprimidos vaginais', 'cremes', 'pomadas', 'óvulos',  # vaginal
          'supositórios', ' enemas',  # retal
          )

classificacoes = ('alopático', 'fitoterápico', 'homeopático')

Medicamentos.farmaco.requires = IS_NOT_EMPTY()
Medicamentos.detentor.requires = IS_NOT_EMPTY()
Medicamentos.via_administracao.requires = IS_IN_SET(vias, zero=T('Escolha um'))
Medicamentos.classificacao.requires = IS_IN_SET(
    classificacoes, zero=T('Escolha um'))
Medicamentos.concentracao.requires = IS_NOT_EMPTY()
Medicamentos.medicamento_referencia.requires = IS_NOT_EMPTY()
Medicamentos.forma_farmaceutica.requires = IS_IN_SET(
    formas, zero=T('Escolha um'))


Estoque = db.define_table('estoque',
                          Field('id_instituicao', 'reference auth_user'),
                          Field('id_medicamento', db.medicamentos),
                          Field('quantidade', 'integer'),
                          Field('unidade'))

unidades = ('caixas', 'frascos', 'cartelas', 'ampolas', 'unidades')

Estoque.unidade.requires = IS_IN_SET(unidades, zero=T('Escolha um'))
Estoque.id_instituicao.requires = IS_IN_DB(
    db, 'auth_user.id', '%(first_name)s',
    zero=T('Escolha um'))
Estoque.quantidade.requires = [IS_NOT_EMPTY(), IS_LENGTH(minsize=0)]
Estoque.id_medicamento.requires = IS_IN_DB(
    db, 'medicamentos.id', '%(farmaco)s %(concentracao)s',
    zero=T('Escolha um'))

PacienteMedicamento = db.define_table('paciente_medicamento',
                                      Field(
                                      'id_paciente', 'reference pacientes'),
                                      Field(
                                      'id_medicamento', 'reference medicamentos'),
                                      Field('horarios', 'time'),
                                      Field('posologia'))

PacienteMedicamento.id_paciente.requires = IS_IN_DB(
    db, 'pacientes.id', '%(nome)s')
PacienteMedicamento.id_medicamento.requires = IS_IN_DB(
    db, 'medicamentos.id', '%(farmaco)s')
PacienteMedicamento.posologia.requires = IS_NOT_EMPTY()


# Criando funções de validação

# Validação para CEP
class IS_VALID_CEP(object):

    def __init__(self, error_message=T('CEP INVÁLIDO')):
        self.error_message = error_message

    def __call__(self, value):
        error = None
        cep_temp = []
        try:
        # Coletando todos os números
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

    # Formata para ddddd-ddd
    def to_cep(self, cep):
        cep = ''.join(cep)
        return cep[0:5] + '-' + cep[5:]

# Validação CNPJ


class IS_VALID_CNPJ(object):

    def __init__(self, error_message=T('CNPJ INVÁLIDO')):
        self.error_message = error_message

    def format(self, value):
        return value[:2]+"."+value[2:5]+"."+value[5:8]+"/"+value[8:12]+"-"+value[-2:]

    def __call__(self, value):
        
        if len(value) != 14:
            return(value, "Tamanho inválido")

        digito1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        digito2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        mult_digito1 = []

        for i, j in zip(value[:12], digito1):
            mult_digito1.append(int(i) * j)


        # somando valores
        sum_digito1 = 0
        for i in mult_digito1:
            sum_digito1 = sum_digito1 + i

        resto = sum_digito1 % 11
        if resto < 2:
            digito1 = 0
        else:
            digito1 = 11 - resto

        digito1 = str(digito1)
        #if value[12] != digito1:
        #   return(value, "erro1")

        
        mult_digito2 = []

        for i, j in zip(value[:13], digito2):
            mult_digito2.append(int(i) * j)

        sum_digito2 = 0
        for i in mult_digito2:
            sum_digito2 = sum_digito2 + i

        resto = sum_digito2 % 11

        if resto < 2:
            digito2 = 0
        else:
            digito2 = 11 - resto

        digito2 = str(digito2)

        verificador = value[-2:]

        if verificador == digito1 + digito2:
            value = self.format(value)
            return(value, None)
        else:
            return (value, self.error_message)


# Adicionando campos extras na table auth_user
auth.settings.extra_fields['auth_user'] = [
    Field("endereco", label='Endereço'),
    Field("cidade", length=100),
    Field("cep", length=9, label='CEP'),
    Field("telefone", length=13),
    Field("cnpj", length=18, label='CNPJ'),
    Field("pais", length=6, default='Brasil', label='País')]

# Campos que irão aparecer na tela de registro
auth.settings.register_fields = [
    'first_name', 'email', 'password', 'telefone', 'endereco',
    'cidade', 'cep', 'pais', 'cnpj']

# create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

# Aterando nomes de campos default da tabela auth_user
db.auth_user.first_name.label = "Instituição"

# Criando validações
db.auth_user.endereco.requires = IS_NOT_EMPTY()
db.auth_user.cidade.requires = IS_NOT_EMPTY()
db.auth_user.cep.requires = [IS_NOT_EMPTY(), IS_VALID_CEP()]
db.auth_user.telefone.requires = IS_NOT_EMPTY()
db.auth_user.cnpj.requires = [IS_NOT_EMPTY(), IS_VALID_CNPJ()]
db.auth_user.pais.requires = IS_NOT_EMPTY()
