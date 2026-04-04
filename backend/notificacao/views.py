from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.utils import timezone
from datetime import timedelta
from django.contrib.admin.models import LogEntry, ADDITION, DELETION
from django.contrib.contenttypes.models import ContentType

from .models import Notificacao
from .forms import NotificacaoForm
from .template_pdf import render_notificacao_template


def _log(user, obj, flag, msg=''):
    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str(obj)[:200],
        action_flag=flag,
        change_message=msg,
    )


@login_required
def notificacao_list(request):
    notificacoes = Notificacao.objects.select_related('crr').order_by('-criado_em')
    search = request.GET.get('search', '')
    if search:
        notificacoes = notificacoes.filter(crr__numeroCrr__icontains=search) | \
                       notificacoes.filter(destinatario__icontains=search)
        notificacoes = notificacoes.distinct()
    return render(request, 'notificacao/notificacao_list.html', {
        'notificacoes': notificacoes,
        'search': search,
    })


@login_required
def notificacao_create(request):
    crr_id = request.GET.get('crr')
    initial = {}
    if crr_id:
        initial['crr'] = crr_id

    if request.method == 'POST':
        form = NotificacaoForm(request.POST)
        if form.is_valid():
            notificacao = form.save(commit=False)
            crr = notificacao.crr
            if crr.status != 'retido':
                messages.error(request, "Somente veículos com status 'Retido' podem ser notificados.")
                return render(request, 'notificacao/notificacao_form.html', {'form': form})
            notificacao.prazo_leilao = crr.dataFiscalizacao + timedelta(days=60)
            notificacao.save()
            crr.not_gerada = True
            crr.save(update_fields=['not_gerada'])
            _log(request.user, notificacao, ADDITION, f'Notificação emitida para CRR {crr.numeroCrr}.')

            # Gera e retorna PDF imediatamente (mesmo comportamento do admin)
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            largura, altura = A4
            render_notificacao_template(c, notificacao, largura, altura)
            c.save()
            buffer.seek(0)
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = (
                f'attachment; filename="notificacao_{notificacao.numero_controle}.pdf"'
            )
            return response
    else:
        form = NotificacaoForm(initial=initial)

    return render(request, 'notificacao/notificacao_form.html', {'form': form})


@login_required
def notificacao_pdf(request, pk):
    notificacao = get_object_or_404(Notificacao, pk=pk)
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4
    render_notificacao_template(c, notificacao, largura, altura)
    c.save()
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="notificacao_{notificacao.numero_controle}.pdf"'
    )
    return response


@login_required
def notificacao_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('notificacao:notificacao_list')
    notificacao = get_object_or_404(Notificacao, pk=pk)
    if request.method == 'POST':
        crr = notificacao.crr
        _log(request.user, notificacao, DELETION, f'Notificação {notificacao.numero_controle} removida.')
        notificacao.delete()
        crr.not_gerada = False
        crr.save(update_fields=['not_gerada'])
        messages.success(request, 'Notificação removida.')
    return redirect('notificacao:notificacao_list')
