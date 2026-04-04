from django.db import models,transaction
from crr.models import Crr
from crr.models import ESTADO_CHOICES
from django.contrib.auth.models import User


class Notificacao(models.Model):  
    crr = models.OneToOneField(Crr,unique=True, on_delete=models.CASCADE,related_name="notificacao",verbose_name='CRR')
    data_emissao = models.DateField(blank=False, null=False,verbose_name='Data de emissão')
    data_postagem = models.DateField(blank=False, null=False, verbose_name='Data de postagem')
    numero_controle = models.PositiveIntegerField(unique=True, blank=False, null=False,verbose_name='Numero de controle')  
    prazo_leilao = models.DateField(blank=False, null=False,verbose_name='Prazo p/ leilão')
    destinatario = models.CharField(max_length=50, blank=False, null=False,verbose_name='destinatário')
    endereco = models.CharField(max_length=50, blank=False, null=False,verbose_name='endereço')
    numero = models.CharField(max_length=6, blank=False, null=False,verbose_name='Número')
    complemento = models.CharField(max_length=10, blank=True, null=False,verbose_name='Complemento')
    bairro = models.CharField(max_length=25, blank=False, null=False,verbose_name='Bairro')
    cidade_destinatario = models.CharField(max_length=25, blank=False, null=False,verbose_name='Cidade do destinatário')
    uf_destinatario = models.CharField(max_length=6,choices=ESTADO_CHOICES, blank=False, null=False,verbose_name='UF do destinatário')
    cep = models.CharField(max_length=9,verbose_name='CEP')
    criado_em = models.DateTimeField(auto_now_add=True)
    editado_em = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # 1. Normalização dos campos de texto (minúsculas)
        lower_fields = [
            'destinatario', 'endereco', 'complemento', 
            'bairro', 'cidade_destinatario'
        ]
        
        for field in lower_fields:
            value = getattr(self, field)
            if value and isinstance(value, str):
                setattr(self, field, value.lower())
        
        # 2. Geração do número de controle (se não existir)
        if not self.numero_controle:
            with transaction.atomic():  
                ultimo = Notificacao.objects.select_for_update().order_by('-numero_controle').first()
                self.numero_controle = (ultimo.numero_controle + 1) if ultimo else 1
        
        # 3. Salva a instância
        super().save(*args, **kwargs)
        
        # 4. Atualiza o status no CRR relacionado
        self.crr.atualizar_status_not_gerada()

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"

def __str__(self):
    return f"Notificação {self.numero_controle} - {self.crr}"


class NumeroEdital(models.Model):
    numero = models.PositiveIntegerField(default=1)

    def incrementar(self):
        self.numero += 1
        self.save()

    def __str__(self):
        return f"Edital número {self.numero}" 
    
class LogGeracaoEdital(models.Model):
    numero_edital = models.CharField(max_length=20)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    data_hora = models.DateTimeField(auto_now_add=True)
    crrs_gerados = models.TextField(help_text="Lista de números dos CRRs incluídos no edital")

    def __str__(self):
        return f"Edital {self.numero_edital} por {self.usuario} em {self.data_hora.strftime('%d/%m/%Y %H:%M')}"