from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.auth.views import PasswordChangeView as DjangoPasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User, Group
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from .models import Crr, Condutor, Veiculo, Ait, Enquadramento, Arrendatario, ImagemCrr, DispositivoMobile, EditalGerado, TabelaArrendatario, TabelaEnquadramento, Agente
from .forms import (
    CrrForm, CondutorFormSet, VeiculoFormSet, AitFormSet,
    EnquadramentoFormSet, ArrendatarioFormSet, ImagemCrrFormSet,
    TabelaArrendatarioForm, TabelaEnquadramentoForm, AgenteForm,
    UsuarioCreateForm, UsuarioEditForm, GrupoForm,
)
from .template_edital import gerar_edital_docx


def _log(user, obj, flag, msg=''):
    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str(obj)[:200],
        action_flag=flag,
        change_message=msg,
    )


class CrrListView(LoginRequiredMixin, ListView):
    model = Crr
    template_name = 'crr/crr_list.html'
    context_object_name = 'crrs'
    paginate_by = 20
    ordering = ['-criado_em']

    def get_queryset(self):
        # Só exibe resultados após o usuário usar o filtro
        if 'search' not in self.request.GET and 'status' not in self.request.GET:
            return Crr.objects.none()

        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        search = self.request.GET.get('search')

        if status:
            queryset = queryset.filter(status=status)

        if search:
            queryset = queryset.filter(
                numeroCrr__icontains=search
            ) | queryset.filter(
                veiculo__placa__icontains=search
            ) | queryset.filter(
                veiculo__chassi__icontains=search
            )

        return queryset.distinct().prefetch_related('condutores')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['search'] = self.request.GET.get('search', '')
        context['total_pendentes'] = Crr.objects.filter(status='pendente').count()
        context['total_retidos'] = Crr.objects.filter(status='retido').count()
        context['total_liberados'] = Crr.objects.filter(status='liberado').count()
        return context


class CrrDetailView(LoginRequiredMixin, DetailView):
    model = Crr
    template_name = 'crr/crr_detail.html'
    context_object_name = 'crr'


@login_required
def crr_detail_modal(request, pk):
    crr = get_object_or_404(Crr, pk=pk)
    return render(request, 'crr/crr_detail_partial.html', {'crr': crr})


@login_required
def triagem_detail_modal(request, pk):
    crr = get_object_or_404(Crr, pk=pk, status='pendente')
    return render(request, 'crr/crr_detail_partial.html', {'crr': crr})


class CrrCreateView(LoginRequiredMixin, CreateView):
    model = Crr
    form_class = CrrForm
    template_name = 'crr/crr_form.html'
    success_url = reverse_lazy('crr:crr_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['condutor_formset'] = CondutorFormSet(self.request.POST, prefix='condutor')
            context['veiculo_formset'] = VeiculoFormSet(self.request.POST, prefix='veiculo')
            context['enquadramento_formset'] = EnquadramentoFormSet(self.request.POST, prefix='enquadramento')
            context['ait_formset'] = AitFormSet(self.request.POST, prefix='ait')
            context['arrendatario_formset'] = ArrendatarioFormSet(self.request.POST, prefix='arrendatario')
            context['imagem_formset'] = ImagemCrrFormSet(self.request.POST, self.request.FILES, prefix='imagem')
        else:
            context['condutor_formset'] = CondutorFormSet(prefix='condutor')
            context['veiculo_formset'] = VeiculoFormSet(prefix='veiculo')
            context['enquadramento_formset'] = EnquadramentoFormSet(prefix='enquadramento')
            context['ait_formset'] = AitFormSet(prefix='ait')
            context['arrendatario_formset'] = ArrendatarioFormSet(prefix='arrendatario')
            context['imagem_formset'] = ImagemCrrFormSet(prefix='imagem')
        context['is_edit'] = False
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        condutor_formset = context['condutor_formset']
        veiculo_formset = context['veiculo_formset']
        enquadramento_formset = context['enquadramento_formset']
        ait_formset = context['ait_formset']
        arrendatario_formset = context['arrendatario_formset']
        imagem_formset = context['imagem_formset']

        with transaction.atomic():
            self.object = form.save()

            # Salvar formsets
            for formset in [condutor_formset, veiculo_formset, enquadramento_formset,
                           ait_formset, arrendatario_formset, imagem_formset]:
                if formset.is_valid():
                    formset.instance = self.object
                    formset.save()

        _log(self.request.user, self.object, ADDITION, 'CRR criado via sistema.')
        messages.success(self.request, f'CRR {self.object.numeroCrr} criado com sucesso!')
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao criar CRR. Verifique os dados informados.')
        return super().form_invalid(form)


class CrrUpdateView(LoginRequiredMixin, UpdateView):
    model = Crr
    form_class = CrrForm
    template_name = 'crr/crr_form.html'
    success_url = reverse_lazy('crr:crr_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['condutor_formset'] = CondutorFormSet(self.request.POST, instance=self.object, prefix='condutor')
            context['veiculo_formset'] = VeiculoFormSet(self.request.POST, instance=self.object, prefix='veiculo')
            context['enquadramento_formset'] = EnquadramentoFormSet(self.request.POST, instance=self.object, prefix='enquadramento')
            context['ait_formset'] = AitFormSet(self.request.POST, instance=self.object, prefix='ait')
            context['arrendatario_formset'] = ArrendatarioFormSet(self.request.POST, instance=self.object, prefix='arrendatario')
            context['imagem_formset'] = ImagemCrrFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix='imagem')
        else:
            context['condutor_formset'] = CondutorFormSet(instance=self.object, prefix='condutor')
            context['veiculo_formset'] = VeiculoFormSet(instance=self.object, prefix='veiculo')
            context['enquadramento_formset'] = EnquadramentoFormSet(instance=self.object, prefix='enquadramento')
            context['ait_formset'] = AitFormSet(instance=self.object, prefix='ait')
            context['arrendatario_formset'] = ArrendatarioFormSet(instance=self.object, prefix='arrendatario')
            context['imagem_formset'] = ImagemCrrFormSet(instance=self.object, prefix='imagem')
        context['is_edit'] = True
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        condutor_formset = context['condutor_formset']
        veiculo_formset = context['veiculo_formset']
        enquadramento_formset = context['enquadramento_formset']
        ait_formset = context['ait_formset']
        arrendatario_formset = context['arrendatario_formset']
        imagem_formset = context['imagem_formset']

        with transaction.atomic():
            self.object = form.save()

            for formset in [condutor_formset, veiculo_formset, enquadramento_formset,
                           ait_formset, arrendatario_formset, imagem_formset]:
                if formset.is_valid():
                    formset.instance = self.object
                    formset.save()

        _log(self.request.user, self.object, CHANGE, 'CRR editado via sistema.')
        messages.success(self.request, f'CRR {self.object.numeroCrr} atualizado com sucesso!')
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao atualizar CRR. Verifique os dados informados.')
        return super().form_invalid(form)


class CrrDeleteView(LoginRequiredMixin, DeleteView):
    model = Crr
    template_name = 'crr/crr_confirm_delete.html'
    success_url = reverse_lazy('crr:crr_list')

    def delete(self, request, *args, **kwargs):
        crr = self.get_object()
        _log(request.user, crr, DELETION, f'CRR {crr.numeroCrr} excluído via sistema.')
        messages.success(request, f'CRR {crr.numeroCrr} excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


# ==================== TRIAGEM ==================== #

class TriagemListView(LoginRequiredMixin, ListView):
    """Lista de CRRs pendentes para triagem"""
    model = Crr
    template_name = 'crr/triagem_list.html'
    context_object_name = 'crrs'
    paginate_by = 20
    ordering = ['dataFiscalizacao']

    def get_queryset(self):
        queryset = super().get_queryset().filter(status='pendente')
        search = self.request.GET.get('search')

        if search:
            queryset = queryset.filter(
                numeroCrr__icontains=search
            ) | queryset.filter(
                veiculo__placa__icontains=search
            ) | queryset.filter(
                veiculo__chassi__icontains=search
            )

        return queryset.distinct().prefetch_related('condutores')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['total_pendentes'] = Crr.objects.filter(status='pendente').count()
        return context


class TriagemDetailView(LoginRequiredMixin, DetailView):
    """Visualização detalhada do CRR para triagem"""
    model = Crr
    template_name = 'crr/triagem_detail.html'
    context_object_name = 'crr'

    def get_queryset(self):
        return super().get_queryset().filter(status='pendente')


class TriagemUpdateView(LoginRequiredMixin, UpdateView):
    """Edição do CRR na triagem - ao salvar, muda status para 'retido'"""
    model = Crr
    form_class = CrrForm
    template_name = 'crr/triagem_form.html'
    success_url = reverse_lazy('crr:triagem_list')

    def get_queryset(self):
        return super().get_queryset().filter(status='pendente')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['condutor_formset'] = CondutorFormSet(self.request.POST, instance=self.object, prefix='condutor')
            context['veiculo_formset'] = VeiculoFormSet(self.request.POST, instance=self.object, prefix='veiculo')
            context['enquadramento_formset'] = EnquadramentoFormSet(self.request.POST, instance=self.object, prefix='enquadramento')
            context['ait_formset'] = AitFormSet(self.request.POST, instance=self.object, prefix='ait')
            context['arrendatario_formset'] = ArrendatarioFormSet(self.request.POST, instance=self.object, prefix='arrendatario')
            context['imagem_formset'] = ImagemCrrFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix='imagem')
        else:
            context['condutor_formset'] = CondutorFormSet(instance=self.object, prefix='condutor')
            context['veiculo_formset'] = VeiculoFormSet(instance=self.object, prefix='veiculo')
            context['enquadramento_formset'] = EnquadramentoFormSet(instance=self.object, prefix='enquadramento')
            context['ait_formset'] = AitFormSet(instance=self.object, prefix='ait')
            context['arrendatario_formset'] = ArrendatarioFormSet(instance=self.object, prefix='arrendatario')
            context['imagem_formset'] = ImagemCrrFormSet(instance=self.object, prefix='imagem')
        context['is_triagem'] = True
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        condutor_formset = context['condutor_formset']
        veiculo_formset = context['veiculo_formset']
        enquadramento_formset = context['enquadramento_formset']
        ait_formset = context['ait_formset']
        arrendatario_formset = context['arrendatario_formset']
        imagem_formset = context['imagem_formset']

        with transaction.atomic():
            self.object = form.save(commit=False)
            # Ao salvar na triagem, muda status para 'retido' (se não for superuser)
            if not self.request.user.is_superuser:
                self.object.status = 'retido'
            self.object.save()

            for formset in [condutor_formset, veiculo_formset, enquadramento_formset,
                           ait_formset, arrendatario_formset, imagem_formset]:
                if formset.is_valid():
                    formset.instance = self.object
                    formset.save()

        _log(self.request.user, self.object, CHANGE, 'CRR triado → status Retido.')
        messages.success(self.request, f'CRR {self.object.numeroCrr} triado com sucesso! Status: Retido')
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao salvar triagem. Verifique os dados informados.')
        return super().form_invalid(form)


@login_required
def dispositivo_list(request):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    dispositivos = DispositivoMobile.objects.order_by('nome')
    return render(request, 'crr/dispositivo_list.html', {'dispositivos': dispositivos})


@login_required
def dispositivo_create(request):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        if nome:
            dispositivo = DispositivoMobile.objects.create(nome=nome)
            _log(request.user, dispositivo, ADDITION, f'Dispositivo "{nome}" cadastrado.')
            messages.success(request, f'Dispositivo "{nome}" cadastrado. Código de ativação gerado automaticamente.')
        else:
            messages.error(request, 'Informe o nome do dispositivo.')
    return redirect('crr:dispositivo_list')


@login_required
def dispositivo_edit(request, pk):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    dispositivo = get_object_or_404(DispositivoMobile, pk=pk)
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        ativo = request.POST.get('ativo') == '1'
        ativado = request.POST.get('ativado') == '1'
        if nome:
            dispositivo.nome = nome
            dispositivo.ativo = ativo
            dispositivo.ativado = ativado
            dispositivo.save(update_fields=['nome', 'ativo', 'ativado'])
            _log(request.user, dispositivo, CHANGE, f'Dispositivo "{nome}" atualizado.')
            messages.success(request, f'Dispositivo "{nome}" atualizado.')
        else:
            messages.error(request, 'Informe o nome do dispositivo.')
    return redirect('crr:dispositivo_list')


@login_required
def dispositivo_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    dispositivo = get_object_or_404(DispositivoMobile, pk=pk)
    if request.method == 'POST':
        nome = dispositivo.nome
        _log(request.user, dispositivo, DELETION, f'Dispositivo "{nome}" removido.')
        dispositivo.delete()
        messages.success(request, f'Dispositivo "{nome}" removido.')
    return redirect('crr:dispositivo_list')


@login_required
def crr_gerar_edital(request):
    if request.method != 'POST':
        return redirect('crr:crr_list')
    ids = request.POST.getlist('crr_ids')
    if not ids:
        messages.warning(request, 'Selecione ao menos um CRR para gerar o edital.')
        return redirect('crr:crr_list')
    # Só CRRs retidos que ainda não tiveram edital emitido
    queryset = Crr.objects.filter(pk__in=ids, status='retido', edital_emitido=False)
    if not queryset.exists():
        messages.warning(request, 'Nenhum CRR elegível selecionado (retido e sem edital emitido).')
        return redirect('crr:crr_list')
    crrs_numeros = list(queryset.values_list('numeroCrr', flat=True))
    response = gerar_edital_docx(queryset)
    queryset.update(edital_emitido=True)
    # Salvar arquivo e registrar
    cd = response.get('Content-Disposition', '')
    filename = cd.split('filename=')[-1].strip('"')
    numero = filename.split('_')[1] if filename.count('_') >= 2 else '00'
    saved_path = default_storage.save(f'editais/{filename}', ContentFile(response.content))
    edital = EditalGerado.objects.create(
        numero=numero,
        arquivo=saved_path,
        usuario=request.user,
        crrs=', '.join(crrs_numeros),
    )
    _log(request.user, edital, ADDITION, f'Edital gerado para CRRs: {", ".join(crrs_numeros)}.')
    return response


@login_required
def edital_list(request):
    editais = EditalGerado.objects.select_related('usuario').order_by('-gerado_em')
    return render(request, 'crr/edital_list.html', {'editais': editais})


@login_required
def triagem_status(request, pk, novo_status):
    """Atualiza o status de um CRR via botão na triagem (retido / liberado)."""
    VALIDOS = {'pendente', 'retido', 'liberado', 'cancelado', 'leiloado'}
    if novo_status not in VALIDOS:
        messages.error(request, 'Status inválido.')
        return redirect('crr:triagem_list')

    crr = get_object_or_404(Crr, pk=pk)
    crr.status = novo_status
    crr.save(update_fields=['status'])

    labels = {'retido': 'Retido', 'liberado': 'Liberado', 'cancelado': 'Cancelado',
              'leiloado': 'Leiloado', 'pendente': 'Pendente'}
    label = labels.get(novo_status, novo_status.capitalize())
    _log(request.user, crr, CHANGE, f'Status alterado para {label}.')
    messages.success(request, f'CRR {crr.numeroCrr.upper()} marcado como {label}.')

    next_url = request.GET.get('next', '')
    if next_url == 'crr_list':
        return redirect('crr:crr_list')
    return redirect('crr:triagem_list')


# -------- TabelaArrendatario CRUD (superuser only) -------- #

@login_required
def arrendatario_list(request):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    itens = TabelaArrendatario.objects.all().order_by('nome_arrendatario')
    return render(request, 'crr/arrendatario_list.html', {'itens': itens})


@login_required
def arrendatario_create(request):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    if request.method == 'POST':
        form = TabelaArrendatarioForm(request.POST)
        if form.is_valid():
            obj = form.save()
            _log(request.user, obj, ADDITION, 'Arrendatário cadastrado.')
            messages.success(request, 'Arrendatário cadastrado com sucesso.')
            return redirect('crr:arrendatario_list')
    else:
        form = TabelaArrendatarioForm()
    return render(request, 'crr/arrendatario_form.html', {'form': form, 'titulo': 'Novo Arrendatário'})


@login_required
def arrendatario_edit(request, pk):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    obj = get_object_or_404(TabelaArrendatario, pk=pk)
    if request.method == 'POST':
        form = TabelaArrendatarioForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            _log(request.user, obj, CHANGE, 'Arrendatário atualizado.')
            messages.success(request, 'Arrendatário atualizado com sucesso.')
            return redirect('crr:arrendatario_list')
    else:
        form = TabelaArrendatarioForm(instance=obj)
    return render(request, 'crr/arrendatario_form.html', {'form': form, 'titulo': 'Editar Arrendatário', 'obj': obj})


@login_required
def arrendatario_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    obj = get_object_or_404(TabelaArrendatario, pk=pk)
    if request.method == 'POST':
        _log(request.user, obj, DELETION, f'Arrendatário "{obj}" excluído.')
        obj.delete()
        messages.success(request, 'Arrendatário excluído.')
        return redirect('crr:arrendatario_list')
    return render(request, 'crr/arrendatario_confirm_delete.html', {'obj': obj})


# -------- TabelaEnquadramento CRUD (superuser only) -------- #

@login_required
def enquadramento_list(request):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    itens = TabelaEnquadramento.objects.all().order_by('codigo')
    return render(request, 'crr/enquadramento_list.html', {'itens': itens})


@login_required
def enquadramento_create(request):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    if request.method == 'POST':
        form = TabelaEnquadramentoForm(request.POST)
        if form.is_valid():
            obj = form.save()
            _log(request.user, obj, ADDITION, 'Enquadramento cadastrado.')
            messages.success(request, 'Enquadramento cadastrado com sucesso.')
            return redirect('crr:enquadramento_list')
    else:
        form = TabelaEnquadramentoForm()
    return render(request, 'crr/enquadramento_form.html', {'form': form, 'titulo': 'Novo Enquadramento'})


@login_required
def enquadramento_edit(request, pk):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    obj = get_object_or_404(TabelaEnquadramento, pk=pk)
    if request.method == 'POST':
        form = TabelaEnquadramentoForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            _log(request.user, obj, CHANGE, 'Enquadramento atualizado.')
            messages.success(request, 'Enquadramento atualizado com sucesso.')
            return redirect('crr:enquadramento_list')
    else:
        form = TabelaEnquadramentoForm(instance=obj)
    return render(request, 'crr/enquadramento_form.html', {'form': form, 'titulo': 'Editar Enquadramento', 'obj': obj})


@login_required
def enquadramento_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    obj = get_object_or_404(TabelaEnquadramento, pk=pk)
    if request.method == 'POST':
        _log(request.user, obj, DELETION, f'Enquadramento "{obj}" excluído.')
        obj.delete()
        messages.success(request, 'Enquadramento excluído.')
        return redirect('crr:enquadramento_list')
    return render(request, 'crr/enquadramento_confirm_delete.html', {'obj': obj})


# -------- Agentes (superuser only) -------- #

@login_required
def agente_list(request):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    agentes = Agente.objects.order_by('nome')
    return render(request, 'crr/agente_list.html', {'agentes': agentes})


@login_required
def agente_create(request):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    if request.method == 'POST':
        form = AgenteForm(request.POST, request.FILES)
        if form.is_valid():
            agente = form.save(commit=False)
            nova_senha = form.cleaned_data.get('nova_senha')
            if nova_senha:
                agente.set_senha(nova_senha)
                agente.senha_alterada = False
            else:
                agente.set_senha('admin')
                agente.senha_alterada = False
            agente.save()
            _log(request.user, agente, ADDITION, f'Agente "{agente.nome}" cadastrado.')
            messages.success(request, f'Agente {agente.nome} cadastrado. Senha inicial: "admin" (ou a definida).')
            return redirect('crr:agente_list')
    else:
        form = AgenteForm()
    return render(request, 'crr/agente_form.html', {'form': form, 'titulo': 'Novo Agente'})


@login_required
def agente_edit(request, pk):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    agente = get_object_or_404(Agente, pk=pk)
    if request.method == 'POST':
        form = AgenteForm(request.POST, request.FILES, instance=agente)
        if form.is_valid():
            form.save()
            _log(request.user, agente, CHANGE, f'Agente "{agente.nome}" atualizado.')
            messages.success(request, f'Agente {agente.nome} atualizado.')
            return redirect('crr:agente_list')
    else:
        form = AgenteForm(instance=agente)
    return render(request, 'crr/agente_form.html', {'form': form, 'titulo': 'Editar Agente', 'obj': agente})


@login_required
def agente_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    agente = get_object_or_404(Agente, pk=pk)
    if request.method == 'POST':
        nome = agente.nome
        _log(request.user, agente, DELETION, f'Agente "{nome}" removido.')
        agente.delete()
        messages.success(request, f'Agente {nome} removido.')
        return redirect('crr:agente_list')
    return render(request, 'crr/agente_confirm_delete.html', {'obj': agente})


# -------- Logs do Sistema (superuser only) -------- #

@login_required
def log_list(request):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')

    logs = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')

    def _get(key):
        v = request.GET.get(key, '').strip()
        return v if v and v != 'None' else ''

    usuario_id = _get('usuario')
    data_de    = _get('data_de')
    data_ate   = _get('data_ate')
    acao       = _get('acao')
    model      = _get('model')

    if usuario_id:
        logs = logs.filter(user_id=usuario_id)
    if data_de:
        logs = logs.filter(action_time__date__gte=data_de)
    if data_ate:
        logs = logs.filter(action_time__date__lte=data_ate)
    if acao:
        logs = logs.filter(action_flag=acao)
    if model:
        logs = logs.filter(content_type__model=model)

    paginator = Paginator(logs, 50)
    page_obj = paginator.get_page(request.GET.get('page'))

    usuarios = User.objects.filter(logentry__isnull=False).distinct().order_by('username')
    content_types = ContentType.objects.filter(logentry__isnull=False).distinct().order_by('model')

    return render(request, 'crr/log_list.html', {
        'page_obj': page_obj,
        'usuarios': usuarios,
        'content_types': content_types,
        'filtros': {
            'usuario': usuario_id, 'data_de': data_de, 'data_ate': data_ate,
            'acao': acao, 'model': model,
        },
    })


# -------- Usuários (superuser only) -------- #

@login_required
def usuario_list(request):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    usuarios = User.objects.all().order_by('username')
    return render(request, 'crr/usuario_list.html', {'usuarios': usuarios})


@login_required
def usuario_create(request):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            _log(request.user, usuario, ADDITION, f'Usuário "{usuario.username}" criado.')
            messages.success(request, 'Usuário criado com sucesso.')
            return redirect('crr:usuario_list')
    else:
        form = UsuarioCreateForm()
    return render(request, 'crr/usuario_form.html', {'form': form, 'titulo': 'Novo Usuário'})


@login_required
def usuario_edit(request, pk):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UsuarioEditForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            _log(request.user, usuario, CHANGE, f'Usuário "{usuario.username}" atualizado.')
            messages.success(request, f'Usuário {usuario.username} atualizado.')
            return redirect('crr:usuario_list')
    else:
        form = UsuarioEditForm(instance=usuario)
    return render(request, 'crr/usuario_form.html', {'form': form, 'titulo': 'Editar Usuário', 'obj': usuario})


@login_required
def usuario_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if usuario == request.user:
            messages.error(request, 'Você não pode excluir seu próprio usuário.')
            return redirect('crr:usuario_list')
        username = usuario.username
        _log(request.user, usuario, DELETION, f'Usuário "{username}" removido.')
        usuario.delete()
        messages.success(request, f'Usuário "{username}" removido.')
        return redirect('crr:usuario_list')
    return render(request, 'crr/usuario_confirm_delete.html', {'obj': usuario})


# -------- Grupos (superuser only) -------- #

@login_required
def grupo_list(request):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    grupos = Group.objects.all().order_by('name')
    return render(request, 'crr/grupo_list.html', {'grupos': grupos})


@login_required
def grupo_create(request):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    if request.method == 'POST':
        form = GrupoForm(request.POST)
        if form.is_valid():
            grupo = form.save()
            _log(request.user, grupo, ADDITION, f'Grupo "{grupo.name}" criado.')
            messages.success(request, 'Grupo criado com sucesso.')
            return redirect('crr:grupo_list')
    else:
        form = GrupoForm()
    return render(request, 'crr/grupo_form.html', {'form': form, 'titulo': 'Novo Grupo'})


@login_required
def grupo_edit(request, pk):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    grupo = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GrupoForm(request.POST, instance=grupo)
        if form.is_valid():
            form.save()
            _log(request.user, grupo, CHANGE, f'Grupo "{grupo.name}" atualizado.')
            messages.success(request, f'Grupo "{grupo.name}" atualizado.')
            return redirect('crr:grupo_list')
    else:
        form = GrupoForm(instance=grupo)
    return render(request, 'crr/grupo_form.html', {'form': form, 'titulo': 'Editar Grupo', 'obj': grupo})


@login_required
def grupo_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('crr:crr_list')
    grupo = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        nome = grupo.name
        _log(request.user, grupo, DELETION, f'Grupo "{nome}" removido.')
        grupo.delete()
        messages.success(request, f'Grupo "{nome}" removido.')
        return redirect('crr:grupo_list')
    return render(request, 'crr/grupo_confirm_delete.html', {'obj': grupo})


# -------- Reenvio de email do CRR -------- #

@login_required
def reenviar_email_crr(request, pk):
    crr = get_object_or_404(Crr, pk=pk)
    from .email_utils import enviar_email_crr
    sucesso = enviar_email_crr(crr)
    if sucesso:
        messages.success(
            request,
            f'Email do CRR {crr.numeroCrr.upper()} enviado com sucesso.'
        )
    else:
        messages.error(
            request,
            f'Falha ao enviar email do CRR {crr.numeroCrr.upper()}. '
            'Verifique as configurações de email.'
        )
    return redirect('crr:crr_detail', pk=pk)


# - Acesso View JAVA- #

class MinhaSenhaView(DjangoPasswordChangeView):
    template_name = 'crr/change_password.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('crr:crr_list')

    def form_valid(self, form):
        messages.success(self.request, 'Senha alterada com sucesso.')
        return super().form_valid(form)

# - Alteração de senha (usuário comum) - #

        if self.request.method == 'PATCH':
            return CrrStatusUpdateSerializer
        if self.action == 'retrieve':
            return CrrJavaDetalheSerializer
        return CrrJavaSerializer
