from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Crr, Ait, Condutor, Enquadramento, Arrendatario, Veiculo,
    TabelaEnquadramento, TabelaArrendatario, ImagemCrr,
    DispositivoMobile, Agente
)

from django import forms
from django.urls import reverse
from datetime import date, timedelta
from django.utils.timezone import now
from crr.template_edital import gerar_edital_docx
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.contrib import messages
import json


# Classe base para aplicar regras de leitura
class BaseReadOnlyInline(admin.StackedInline):  # ou admin.StackedInline
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        if obj is None or request.user.is_superuser:
            return []

        if obj.status == 'pendente':
            return []

        return [field.name for field in self.model._meta.fields]
    
    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        return True
        #return request.user.is_superuser or (obj and obj.status == 'pendente')

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
   
# ============== INLINES ============== #

class CondutorInline(BaseReadOnlyInline):
    model = Condutor
    extra = 1
    max_num = 1
    fields = ['nomeCondutor','cpfCondutor','cnh','cnhEstrangeira', 'ufCnh']

   

class VeiculoInline(BaseReadOnlyInline):
    model = Veiculo
    extra = 1
    max_num = 1
    fields = ['placa','chassi','marca', 'modelo', 'cor','especie','categoria','ufVeiculo','municipioVeiculo']
   


class AitInline(BaseReadOnlyInline):
    model = Ait
    extra = 1
    max_num = 4
    fields = ['ait']
   

class EnquadramentoInlineForm(forms.ModelForm): # ajusta o tamanho do campo Enquadramento
    
    class Meta:
        model = Enquadramento
        fields = ['enquadramento']
        widgets = {
            'enquadramento': forms.Select(attrs={'style': 'width: 500px;'}),
        }        

class EnquadramentoInline(BaseReadOnlyInline):
    model = Enquadramento
    form = EnquadramentoInlineForm
    extra = 1
    max_num = 4
    fields = ['enquadramento']
    verbose_name_plural = "Enquadramentos"


class ArrendatarioInline(BaseReadOnlyInline):
    model = Arrendatario
    extra = 1
    max_num = 1
    fields = ['arrendatario']
    verbose_name_plural = "Arrendatário"


class TabelaArrendatarioResource(resources.ModelResource):
    class Meta:
        model = TabelaArrendatario
        import_id_fields = ['nome_arrendatario']
        fields = ('nome_arrendatario', 'cnpj_arrendatario','endereco_arrendatario','numero_arrendatario','complemento_arrendatario','bairro_arrendatario','cidade_arrendatario','uf_arrendatario','cep_arrendatario')


@admin.register(TabelaArrendatario)
class TabelaArrendatarioAdmin(ImportExportModelAdmin):
    resource_class = TabelaArrendatarioResource
    list_display = ('nome_arrendatario', 'cnpj_arrendatario')





# ============== MODELADMINS ============== #
class FiltroCrrAtrasado(admin.SimpleListFilter):
    title = 'TODOS CRRs'
    parameter_name = 'crr_filtro'

    def lookups(self, request, model_admin):
        return (
            ('atrasado', 'NOTIFICAÇÃO PENDENTE'),
            ('edital', 'EDITAL PENDENTE'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'atrasado':
            data_limite = date.today() - timedelta(days=10)
            return queryset.filter(dataFiscalizacao__lte=data_limite, not_gerada=False, status='retido')

        if self.value() == 'edital':
            data_limite = date.today() - timedelta(days=30)
            return queryset.filter(dataFiscalizacao__lte=data_limite, status='retido', edital_emitido=False)

        return queryset

class TabelaEnquadramentoResource(resources.ModelResource):
    class Meta:
        model = TabelaEnquadramento
        import_id_fields = ['codigo']
        fields = ('codigo', 'amparo_legal', 'descricao_infracao')

@admin.register(TabelaEnquadramento)
class TabelaEnquadramentoAdmin(ImportExportModelAdmin):
    resource_class = TabelaEnquadramentoResource
    list_display = ('codigo', 'amparo_legal', 'descricao_infracao')

class ImagemCrrInline(admin.StackedInline):
    model = ImagemCrr
    extra = 1
    max_num = 4
    fields = ['imagem',]

             
@admin.register(Crr)
class CrrAdmin(admin.ModelAdmin):
    list_display = ('numeroCrr','get_placa','get_chassi','get_marca','criar_notificacao_link','dataFiscalizacao', 'get_enquadramentos','status','edital_emitido')
    list_filter = (FiltroCrrAtrasado,'dataFiscalizacao', 'status',)
    actions = ['gerar_edital_docx_action']
    search_fields = ['numeroCrr', 'veiculo__placa','veiculo__chassi','veiculo__marca'] 
    list_editable = ('status',)
    ordering = ('numeroCrr',)
    fieldsets = (
        ("Identificação do CRR", {
            'fields': ('numeroCrr',)
        }),
        ("Local e Data da Fiscalização", {
            'fields': ('localFiscalizacao', 'dataFiscalizacao', 'horaFiscalizacao')
        }),
        ("Dados do Guincho", {
            'fields': ('placaGuincho', 'encarregado')
        }),
        ("Informações Adicionais", {
            'fields': ('observacao', 'matriculaAgente')
        }),
    )

    # Ordem dos inlines conforme solicitado:
    # 1. Condutor, 2. Veículo, 3. Enquadramento, 4. AIT, 5. Arrendatário, 6. Imagens
    inlines = [CondutorInline, VeiculoInline, EnquadramentoInline, AitInline, ArrendatarioInline, ImagemCrrInline]
       

    # Lista vazia na listagem de CRR
    def get_queryset(self, request):
        """
        Retorna um queryset vazio por padrão, exceto se houver filtro aplicado.
        """
        qs = super().get_queryset(request)

        # Só retorna resultados se houver parâmetros de filtro na URL
        if request.GET:
            return qs
        self.message_user(
                request,
                "Selecione algum fitro.",
                level=messages.WARNING
            )
        # Nenhum filtro → retorna queryset vazio
        return qs.none()
        
    
    def get_placa(self, obj):
        return ", ".join([v.placa for v in obj.veiculo.all()]) if obj.veiculo.exists() else "-"
    get_placa.short_description = 'Placa'

    def get_chassi(self, obj):
        return ", ".join([v.chassi for v in obj.veiculo.all()]) if obj.veiculo.exists() else "-"
    get_chassi.short_description = 'Chassi'

    def get_marca(self, obj):
        return ", ".join([v.marca for v in obj.veiculo.all()]) if obj.veiculo.exists() else "-"
    get_marca.short_description = 'Marca'

    def get_enquadramentos(self, obj):
        enquads = obj.enquadramentos.all()
        return ", ".join([str(enq.enquadramento.codigo) for enq in enquads]) if enquads else "—"
    get_enquadramentos.short_description = "Enquadramento"

    # transforma em os campos readyonly
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []

        if obj is None:  # Página de criação (add), sempre editável
            return []

        if obj.status == 'pendente':
            return []

        # Caso contrário, todos os campos são somente leitura, exceto 'status'
        return [f.name for f in self.model._meta.fields if f.name != 'status']

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    # restrição das opções do status
    def get_changelist_formset(self, request, **kwargs):
        FormSet = super().get_changelist_formset(request, **kwargs)

        class CustomFormSet(FormSet):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if not request.user.is_superuser:
                    for form in self.forms:
                        if 'status' in form.fields:
                            current_value = form.initial.get('status')
                            choices = form.fields['status'].choices

                            # Permitir mudar para 'retido' e 'liberado' se atual for 'pendente'
                            if current_value == 'pendente':
                                allowed_choices = [
                                    choice for choice in choices
                                    if choice[0] in ['pendente', 'retido', 'liberado']
                                ]
                            else:
                                # Permite só manter atual + 'liberado'
                                allowed_choices = [
                                    choice for choice in choices
                                    if choice[0] in [current_value, 'liberado']
                                ]
                            form.fields['status'].choices = allowed_choices

        return CustomFormSet
    
    

    
    @admin.action(description="Gerar Edital em DOCX")
    def gerar_edital_docx_action(self, request, queryset):
        response = gerar_edital_docx(queryset)
        queryset.update(edital_emitido=True)
        return response

    def criar_notificacao_link(self, obj):
        if obj.status != 'retido':
            return None
        if hasattr(obj, 'notificacao'):
            return "✅ Notificação emitida"

        url = reverse("admin:notificacao_notificacao_add")
        return format_html('<a class="button" href="{}?crr={}">➕ Notificar</a>', url, obj.pk)

    criar_notificacao_link.short_description = "Nova Notificação"

    

    def save_model(self, request, obj, form, change):
        # Só aplica essa lógica se estiver editando (change = True)
        if change :
            if not request.user.is_superuser:
                if obj.status == 'pendente':
                    obj.status = 'retido'
                    self.message_user(
                    request,
                    "O status do CRR mudou para retido.",
                    level=messages.WARNING
                )
        super().save_model(request, obj, form, change)
        
        
    class Media:
        js = (
            'js/mascaras.js',
        )

# ==================== DISPOSITIVOS MOBILE ==================== #

@admin.register(DispositivoMobile)
class DispositivoMobileAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'codigo_ativacao', 'ativado',
        'ativo', 'ultimo_acesso',
    ]
    list_filter = ['ativo', 'ativado']
    search_fields = [
        'nome', 'imei', 'codigo_ativacao',
    ]
    readonly_fields = [
        'api_key', 'codigo_ativacao',
        'criado_em', 'ultimo_acesso',
    ]
    actions = [
        'regenerar_api_key', 'regenerar_codigo_ativacao',
        'desativar_dispositivos', 'ativar_dispositivos',
    ]

    fieldsets = (
        ('Identificacao do Dispositivo', {
            'fields': ('nome', 'ativo'),
        }),
        ('Ativacao', {
            'fields': ('codigo_ativacao', 'ativado'),
        }),
        ('Autenticacao API', {
            'fields': ('api_key', 'imei'),
            'classes': ('collapse',),
        }),
        ('Informacoes do Sistema', {
            'fields': ('criado_em', 'ultimo_acesso')
        }),
    )

    @admin.action(description="Regenerar API Key")
    def regenerar_api_key(self, request, queryset):
        for dispositivo in queryset:
            dispositivo.api_key = DispositivoMobile.gerar_api_key()
            dispositivo.save()
        self.message_user(
            request,
            f"API Keys regeneradas para {queryset.count()} dispositivo(s). Os dispositivos precisarao fazer login novamente.",
            level=messages.WARNING
        )

    @admin.action(description="Regenerar codigo de ativacao")
    def regenerar_codigo_ativacao(self, request, queryset):
        for dispositivo in queryset:
            dispositivo.codigo_ativacao = ''
            dispositivo.ativado = False
            dispositivo.save()
        self.message_user(
            request,
            f"Codigos regenerados para {queryset.count()} dispositivo(s). Os dispositivos precisarao ser ativados novamente.",
            level=messages.WARNING
        )

    @admin.action(description="Desativar dispositivos selecionados")
    def desativar_dispositivos(self, request, queryset):
        queryset.update(ativo=False)
        self.message_user(request, f"{queryset.count()} dispositivo(s) desativado(s).")

    @admin.action(description="Ativar dispositivos selecionados")
    def ativar_dispositivos(self, request, queryset):
        queryset.update(ativo=True)
        self.message_user(request, f"{queryset.count()} dispositivo(s) ativado(s).")



@admin.register(Agente)
class AgenteAdmin(admin.ModelAdmin):
    list_display = [
        'matricula', 'nome', 'ativo',
        'senha_alterada', 'criado_em',
    ]
    list_filter = ['ativo', 'senha_alterada']
    search_fields = ['matricula', 'nome']
    ordering = ['nome']
    actions = ['resetar_senha']

    fieldsets = (
        (None, {
            'fields': ('matricula', 'nome', 'ativo', 'assinatura')
        }),
        ('Informacoes do Sistema', {
            'fields': ('senha_alterada', 'criado_em',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['criado_em', 'senha_alterada']

    @admin.action(description="Resetar senha para padrao (admin)")
    def resetar_senha(self, request, queryset):
        from django.contrib.auth.hashers import make_password
        queryset.update(
            senha=make_password('admin'),
            senha_alterada=False,
        )
        self.message_user(
            request,
            f"Senha resetada para {queryset.count()} agente(s)."
        )


# --- Configurações Globais do Admin Site ---
admin.site.site_header = "Administração CRR"
admin.site.site_title = "Painel CRR"

# --- Customização do Contexto do Dashboard ---
original_each_context = admin.site.each_context

def custom_admin_each_context(request):
    context = original_each_context(request)

    hoje = now().date()
    trinta_dias_atras = hoje - timedelta(days=30)
    dez_dias_atras = hoje - timedelta(days=10)

    context['hoje_str'] = hoje.strftime('%Y-%m-%d')
    context['trinta_dias_atras_str'] = trinta_dias_atras.strftime('%Y-%m-%d')


    # Contadores
    context['total_crr_pendentes'] = Crr.objects.filter(status='pendente').count()
    context['total_notificacao_pendente'] = Crr.objects.filter(
        status='retido',
        not_gerada=False,
        dataFiscalizacao__lte=dez_dias_atras
    ).count()
    context['total_edital_pendente'] = Crr.objects.filter(
        status='retido',
        edital_emitido=False,
        dataFiscalizacao__lte=trinta_dias_atras
    ).count()

    # Gráfico 1: Retido vs Liberado
    total_retido = Crr.objects.filter(status='retido').count()
    total_liberado = Crr.objects.filter(status='liberado').count()
    context['chart_retido_liberado_data'] = json.dumps([total_retido, total_liberado])
    context['chart_retido_liberado_labels'] = json.dumps(['Retidos', 'Liberados'])

    # Gráfico 2: Abandonado vs Abordado
    abandonado_ids = Enquadramento.objects.filter(
        enquadramento__codigo='00000'
    ).values_list('crr_id', flat=True).distinct()

    total_abandonado = Crr.objects.filter(id__in=abandonado_ids).count()
    total_abordado = Crr.objects.exclude(id__in=abandonado_ids).count()

    context['chart_enquadramento_data'] = json.dumps([total_abandonado, total_abordado])
    context['chart_enquadramento_labels'] = json.dumps(['Veículo Abandonado', 'Veículo Abordado'])

    return context

# Atribuindo o contexto ao admin padrão
admin.site.each_context = custom_admin_each_context