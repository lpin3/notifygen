from django.contrib import admin
from django.http import HttpResponse
from .models import Notificacao
from crr.models import Crr, ImagemCrr, Condutor
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.utils import timezone
from .template_pdf import render_notificacao_template
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from django.utils.html import format_html


def gerar_pdf_notificacoes(modeladmin, request, queryset):   
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4    
    for i, notificacao in enumerate(queryset):
        if i > 0:
            c.showPage()        
        render_notificacao_template(c, notificacao, largura, altura) 
    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="notificacoes_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    return response

gerar_pdf_notificacoes.short_description = "NOTIFICAÇÃO PROPRIETÁRIO"

# Register your models here.
@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('get_numero_crr','data_emissao','data_postagem','prazo_leilao','imagem_preview')
    list_display_links = ('get_numero_crr',)
    search_fields = ('crr__numeroCrr','numero_controle', 'destinatario')
    list_filter = ('data_emissao', 'crr__numeroCrr')
    readonly_fields = ('numero_controle','prazo_leilao')
    actions = [gerar_pdf_notificacoes]

    def get_numero_crr(self, obj):
        return obj.crr.numeroCrr if obj.crr else '-'
    get_numero_crr.short_description = 'Número CRR'

    def get_ait(self, obj):
        aits = obj.crr.ait.all()
        return ", ".join([ait.ait for ait in aits]) if aits else ""
    get_ait.short_description = "AIT"

    def get_enquadramento(self, obj):
        enquadramentos = obj.crr.enquadramento.all()
        return ", ".join([enq.codigo for enq in enquadramentos]) if enquadramentos else ""
    get_enquadramento.short_description = "ENQUADRAMENTO"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None and 'prazo_leilao' in form.base_fields:
            form.base_fields['prazo_leilao'].required = False
        return form

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.prazo_leilao = obj.crr.dataFiscalizacao + timedelta(days=60)

        if obj.crr.status != 'retido':
            raise ValidationError("Somente veículos com status 'Retido'.")

        # ✅ Atualiza o status not_gerada do CRR relacionado
        

        super().save_model(request, obj, form, change)
        
        obj.crr.not_gerada = True
        obj.crr.save()

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        crr_id = request.GET.get("crr")
        if crr_id:
            initial["crr"] = crr_id
        return initial

    def response_add(self, request, obj, post_url_continue=None):
        # Gera o PDF em memória
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        largura, altura = A4
        render_notificacao_template(c, obj, largura, altura)
        c.save()
        buffer.seek(0)

        # Retorna como arquivo para download no navegador
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="notificacao_{obj.numero_controle}.pdf"'
        return response

    fieldsets = (
        ("Informações da Notificação", {
            'fields': ('numero_controle','crr','data_emissao','data_postagem')
        }),
        ("Destinatário", {
            'fields': ('destinatario', 'endereco', 'numero', 'complemento', 'bairro', 'cidade_destinatario','uf_destinatario', 'cep')
        }),
    )

    
    def imagem_preview(self, obj):
        try:
            imagem = obj.crr.imagens.first()
            if imagem:
                # Tenta usar o campo imagem (upload local)
                if imagem.imagem:
                    url = imagem.imagem.url
                # Caso contrário, usa a URL vinda da API
                elif imagem.url:
                    url = imagem.url
                else:
                    return "Sem imagem"

                return format_html(
                    '<a href="{0}" target="_blank"><img src="{0}" style="max-height: 60px; max-width: 60px;" /></a>',
                    url
                )
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")
        return "Sem imagem"

        imagem_preview.short_description = "Pré-visualização"


    class Media:
        js = (
            
            'js/mascaras.js',
        
        )