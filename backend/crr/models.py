from django.db import models
from datetime import timedelta
import secrets
from django.contrib.auth.models import User
from .choices import STATUS_CHOICES,CATEGORIA_CHOICES,ESTADO_CHOICES,STATUS_CHOICES,ESPECIE_CHOICES

# ---------------- VEÍCULO ---------------- #
def upload_path(instance, filename):
    numeroCrr = instance.crr.numeroCrr if instance.crr.numeroCrr else "sem_identificacao"
    return f"notificacoes/{numeroCrr}/{filename}"




class Crr(models.Model):  
    numeroCrr = models.CharField(max_length=10, unique=True, blank=False, null=True, verbose_name='número do crr')
    localFiscalizacao = models.CharField(max_length=100, blank=False, null=False,verbose_name='Local da Fiscalização')
    municipioEstadoFiscalizacao = models.CharField(max_length=50,default='São Sebastião - SP' ,blank=True, null=True,verbose_name='Município da Fiscalização')
    dataFiscalizacao = models.DateField(blank=False, null=False,verbose_name='Data da fiscalização')
    horaFiscalizacao = models.TimeField(blank=False, null=False,verbose_name='Hora da fiscalização')
    observacao = models.CharField(max_length=300, blank=True, null=False,verbose_name='Observação')
    matriculaAgente = models.CharField(max_length=10, blank=False, null=False, verbose_name='Matrícula do agente')
    medidaAdministrativa  = models.CharField(max_length=100, blank=True,default='Remoção do veículo ao Depósito', null=True,verbose_name='Medida Administrativa')
    localPatio = models.CharField(max_length=100, default='AV ODISSEU 750 - CANTO DO MAR - SÃO SEBASTIÃO/SP', blank=True, null=False, verbose_name='Pátio')
    placaGuincho = models.CharField(max_length=7, blank=True, null=False,verbose_name='Placa do guicho')
    encarregado = models.CharField(max_length=50, blank=True, null=False,verbose_name='encarregado do guincho')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,default='pendente',help_text="Status atual do veículo (Retido/Liberado)")
    SITUACAO_ENTREGA_CHOICES = [
        ('assinou e recebeu 2a via',           'Assinou e recebeu 2ª via'),
        ('recusou assinar e recebeu 2a via',   'Recusou assinar e recebeu 2ª via'),
        ('recusou assinar e a receber 2a via', 'Recusou assinar e a receber 2ª via'),
        ('condutor ausente',                   'Condutor ausente'),
    ]
    situacaoEntrega = models.CharField(
        max_length=50, blank=True, null=False, default='',
        choices=SITUACAO_ENTREGA_CHOICES,
        verbose_name='Situação de Entrega',
    )
    not_gerada = models.BooleanField(default=False,verbose_name='Status da Notificação')
    edital_emitido = models.BooleanField(default=False) 
    criado_em = models.DateTimeField(auto_now_add=True)
    editado_em = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Definir os campos que devem ser convertidos para minúsculas
        lower_fields = [
             'numeroCrr','localFiscalizacao','municipioEstadoFiscalizacao','observacao',
             'medidaAdministrativa','localPatio','placaGuincho','encarregado',
        ]
        
        # Aplicar normalização para minúsculas
        for field in lower_fields:
            value = getattr(self, field)
            if value and isinstance(value, str):
                setattr(self, field, value.lower())
                                        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "CRR"
        verbose_name_plural = "CRRs"
    def __str__(self):
         return self.numeroCrr 
    
    def atualizar_status_not_gerada(self):
        """Atualiza automaticamente se a notificação já foi gerada."""
        if hasattr(self, 'notificacao'):  # Verifica se já há uma Notificação vinculada
            self.not_gerada = False
        else:
            self.not_gerada = self.dataFiscalizacao <= (date.today() - timedelta(days=10))
        self.save()

    def calcular_prazo_leilao(self):
        """Retorna a data de leilão (60 dias após a remoção)."""
        if self.dataFiscalizacao:
            return self.dataFiscalizacao + timedelta(days=60)
        return None


class Veiculo(models.Model):
    crr = models.ForeignKey(Crr, on_delete=models.CASCADE, related_name='veiculo')
    placa = models.CharField( max_length=7,blank=True,null=False)
    chassi = models.CharField( max_length=20,blank=True, null=False)
    marca = models.CharField(max_length=20, blank=True, null=False)
    modelo = models.CharField(max_length=20, blank=True, null=False)
    cor = models.CharField( max_length=20,blank=True, null=False)
    especie = models.CharField(max_length=20 ,choices=ESPECIE_CHOICES, blank=True, null=False,verbose_name='espécie')
    categoria = models.CharField(max_length=20,choices=CATEGORIA_CHOICES, blank=True, null=False)
    ufVeiculo = models.CharField(max_length=6, choices=ESTADO_CHOICES, blank=True, null=False,verbose_name='UF do veículo')
    municipioVeiculo = models.CharField(max_length=30, blank=True, null=False,verbose_name='Município do veículo')

    def __str__(self):
        return self.placa or "Veículo sem placa"
    def save(self, *args, **kwargs):
        # Definir os campos que devem ser convertidos para minúsculas
        lower_fields = [ 'placa','chassi','marca', 'modelo','cor' ,
                        'especie','categoria','ufVeiculo','municipioVeiculo',
                       ]
        
        # Aplicar normalização para minúsculas
        for field in lower_fields:
            value = getattr(self, field)
            if value and isinstance(value, str):
                setattr(self, field, value.lower())
                                        
        super().save(*args, **kwargs)
    
    
class TabelaArrendatario(models.Model):
    nome_arrendatario = models.CharField(max_length=50, unique=True,blank=True,null=False,verbose_name='Nome do arrendatário')
    cnpj_arrendatario = models.CharField(max_length=20,blank=True,null=False,verbose_name='CNPJ')
    endereco_arrendatario = models.CharField(max_length=25,blank=True,null=False,verbose_name='Endereço')
    numero_arrendatario = models.CharField(max_length=6,blank=True,null=False,verbose_name='número')
    complemento_arrendatario = models.CharField(max_length=10, blank=True,null=False,verbose_name='Complemento')
    bairro_arrendatario = models.CharField(max_length=25,blank=True,null=False,verbose_name='Bairro')
    cidade_arrendatario = models.CharField(max_length=25,blank=True,null=False,verbose_name='Cidade')
    uf_arrendatario = models.CharField(max_length=6, choices=ESTADO_CHOICES,blank=True,null=False,verbose_name='UF')
    cep_arrendatario = models.CharField(max_length=9,blank=True,null=False,verbose_name='CEP')

    def __str__(self):
        return f"{self.nome_arrendatario} - {self.cnpj_arrendatario}"

    def save(self, *args, **kwargs):
        campos_minusculos = [
            'nome_arrendatario','endereco_arrendatario','complemento_arrendatario','bairro_arrendatario','cidade_arrendatario',
        ]
        for field in campos_minusculos:
            valor = getattr(self, field)
            if valor and isinstance(valor, str):
                setattr(self, field, valor.lower())

        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Arrendatário"
        verbose_name_plural = "Arrendatários"

class Arrendatario(models.Model):
    crr = models.ForeignKey(Crr, on_delete=models.CASCADE, related_name='arrendatarios')
    arrendatario = models.ForeignKey(TabelaArrendatario, on_delete=models.PROTECT, verbose_name="Arrendatário")

    def __str__(self):
        return f"{self.arrendatario.nome_arrendatario} - {self.arrendatario.cnpj_arrendatario}"

    class Meta:
        verbose_name = "Arrendatário"
        verbose_name_plural = "Arrendatários"


class Condutor(models.Model):
    crr = models.ForeignKey(Crr, on_delete=models.CASCADE, related_name='condutores')
    cnh = models.CharField(max_length=11, blank=True, null=False, verbose_name='cnh')
    cnhEstrangeira = models.CharField(max_length=11, blank=True, null=False, verbose_name='cnh estrangeira')
    ufCnh = models.CharField(max_length=6, choices=ESTADO_CHOICES, blank=True, null=False, verbose_name='UF da CNH')
    cpfCondutor = models.CharField(max_length=14, blank=True, null=False, verbose_name='CPF')
    nomeCondutor = models.CharField(max_length=50, blank=True, null=False, verbose_name='Nome do Condutor')
    assinaturaCondutor = models.TextField(blank=True, default='', verbose_name='Assinatura do Condutor (base64)')


    def __str__(self):
        return f"{self.nomeCondutor} ({self.cpfCondutor})"
    
    def save(self, *args, **kwargs): # normaliza banco de dados
        lower_fields = [
            'cnhEstrangeira','ufCnh','nomeCondutor',
        ]
        
        # Aplicar normalização para minúsculas
        for field in lower_fields:
            value = getattr(self, field)
            if value and isinstance(value, str):
                setattr(self, field, value.lower())
                                 
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Condutor"
        verbose_name_plural = "Condutor"


class Ait(models.Model):
    crr = models.ForeignKey(Crr,on_delete=models.CASCADE,related_name='aits')
    ait = models.CharField(max_length=11,verbose_name='Código de AIT', blank=True, null=False)   
    
    def __str__(self):
        return self.ait
    
    def save(self, *args, **kwargs): # normaliza banco de dados
        lower_fields = [
            'ait',
        ]
        
        # Aplicar normalização para minúsculas
        for field in lower_fields:
            value = getattr(self, field)
            if value and isinstance(value, str):
                setattr(self, field, value.lower())
                                 
        super().save(*args, **kwargs)


class TabelaEnquadramento(models.Model):
    codigo = models.CharField(max_length=6, unique=True,verbose_name='Código')
    amparo_legal = models.CharField(max_length=100)
    descricao_infracao = models.CharField(max_length=500,verbose_name='Descrição da informação')

    def __str__(self):
        return f"{self.codigo} - {self.descricao_infracao}"

    def save(self, *args, **kwargs): # normaliza banco de dados
        lower_fields = [
            'amparo_legal','descricao_infracao',
        ]
        
        # Aplicar normalização para minúsculas
        for field in lower_fields:
            value = getattr(self, field)
            if value and isinstance(value, str):
                setattr(self, field, value.lower())
                                 
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Enquadramento"
        verbose_name_plural = "Enquadramentos"

class Enquadramento(models.Model):
    crr = models.ForeignKey(Crr, on_delete=models.CASCADE, related_name='enquadramentos')
    enquadramento = models.ForeignKey(TabelaEnquadramento, on_delete=models.PROTECT, verbose_name="Enquadramento",null=True)

    def __str__(self):
        return f"{self.enquadramento.codigo} - {self.enquadramento.descricao_infracao[:30]}"


class ImagemCrr(models.Model):
    crr = models.ForeignKey('Crr', on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to=upload_path, blank=True, null=True, verbose_name="Imagem (upload via Admin)")
    nomeArquivo = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(max_length=1000, blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Atualiza os campos com base na imagem enviada
        if self.imagem and (not self.url or not self.nomeArquivo):
            self.nomeArquivo = self.imagem.name
            self.url = self.imagem.url
            super().save(update_fields=['nomeArquivo', 'url'])

    def __str__(self):
        return self.url or f"Imagem {self.id} para {self.crr.numeroCrr}"


# ==================== AGENTES ==================== #

class Agente(models.Model):
    """Agente autorizado a usar o app mobile"""
    matricula = models.CharField(max_length=20, unique=True, verbose_name='Matricula')
    nome = models.CharField(max_length=100, verbose_name='Nome do Agente')
    senha = models.CharField(max_length=128, default='', blank=True, verbose_name='Senha (hash)')
    senha_alterada = models.BooleanField(default=False, verbose_name='Senha alterada')
    assinatura = models.ImageField(upload_to='assinaturas/', blank=True, null=True, verbose_name='Assinatura')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Agente'
        verbose_name_plural = 'Agentes'
        ordering = ['nome']

    def __str__(self):
        return f"{self.matricula} - {self.nome}"

    def set_senha(self, raw_password):
        from django.contrib.auth.hashers import make_password
        self.senha = make_password(raw_password)

    def check_senha(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.senha)

    def save(self, *args, **kwargs):
        if not self.pk and not self.senha:
            from django.contrib.auth.hashers import make_password
            self.senha = make_password('admin')
        super().save(*args, **kwargs)


# ==================== DISPOSITIVOS MOBILE ==================== #

class DispositivoMobile(models.Model):
    """Dispositivo mobile autorizado a criar CRRs"""
    nome = models.CharField(max_length=100, verbose_name='Nome do Dispositivo')
    imei = models.CharField(max_length=20, unique=True, blank=True, null=True,
                           verbose_name='IMEI do Dispositivo',
                           help_text='Numero IMEI unico do dispositivo (15-17 digitos)')
    api_key = models.CharField(max_length=64, unique=True, verbose_name='API Key')
    codigo_ativacao = models.CharField(
        max_length=8, unique=True, blank=True,
        verbose_name='Codigo de Ativacao',
        help_text='Codigo de 6 digitos para ativar o dispositivo no app mobile'
    )
    ativado = models.BooleanField(default=False, verbose_name='Ativado',
                                   help_text='Indica se o dispositivo foi ativado via app mobile')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    criado_em = models.DateTimeField(auto_now_add=True)
    ultimo_acesso = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Dispositivo Mobile'
        verbose_name_plural = 'Dispositivos Mobile'

    def __str__(self):
        return f"{self.nome}"

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = secrets.token_hex(32)
        if not self.codigo_ativacao:
            self.codigo_ativacao = self._gerar_codigo_ativacao()
        super().save(*args, **kwargs)

    @staticmethod
    def _gerar_codigo_ativacao():
        """Gera um codigo de ativacao unico de 6 digitos"""
        import random
        while True:
            codigo = f"{random.randint(100000, 999999)}"
            if not DispositivoMobile.objects.filter(
                codigo_ativacao=codigo
            ).exists():
                return codigo

    @classmethod
    def gerar_api_key(cls):
        return secrets.token_hex(32)


# ==================== EDITAIS GERADOS ==================== #

class EditalGerado(models.Model):
    numero = models.CharField(max_length=10, verbose_name='Número do Edital')
    arquivo = models.FileField(upload_to='editais/', verbose_name='Arquivo DOCX')
    usuario = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Gerado por'
    )
    crrs = models.TextField(verbose_name='CRRs Incluídos')
    gerado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Edital Gerado'
        verbose_name_plural = 'Editais Gerados'
        ordering = ['-gerado_em']

    def __str__(self):
        return f"Edital nº {self.numero} — {self.gerado_em.strftime('%d/%m/%Y')}"
