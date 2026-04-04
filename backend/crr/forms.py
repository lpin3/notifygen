from django import forms
from django.forms import inlineformset_factory
from .models import Crr, Condutor, Veiculo, Ait, Enquadramento, Arrendatario, ImagemCrr, TabelaEnquadramento, TabelaArrendatario, Agente


PATIO_CHOICES = [
    ('AV ODISSEU 750 - CANTO DO MAR - SÃO SEBASTIÃO/SP',
     'AV ODISSEU 750 - CANTO DO MAR - SÃO SEBASTIÃO/SP'),
    ('RUA BOLIVIA, Nº202, JARAGUA - SÃO SEBASTIÃO/SP - 11600-748',
     'RUA BOLIVIA, Nº202, JARAGUA - SÃO SEBASTIÃO/SP - 11600-748'),
]


class CrrForm(forms.ModelForm):
    localPatio = forms.ChoiceField(
        choices=PATIO_CHOICES,
        initial='AV ODISSEU 750 - CANTO DO MAR - SÃO SEBASTIÃO/SP',
        label='Local do Pátio',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Crr
        fields = [
            'numeroCrr', 'localFiscalizacao', 'dataFiscalizacao',
            'horaFiscalizacao', 'localPatio', 'placaGuincho', 'encarregado',
            'observacao', 'matriculaAgente'
        ]
        widgets = {
            'numeroCrr': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número do CRR'}),
            'localFiscalizacao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Local da Fiscalização'}),
            'dataFiscalizacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'horaFiscalizacao': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}, format='%H:%M'),
            'placaGuincho': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Placa do Guincho'}),
            'encarregado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Encarregado'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observações'}),
            'matriculaAgente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Matrícula do Agente'}),
        }


class CondutorForm(forms.ModelForm):
    class Meta:
        model = Condutor
        fields = ['nomeCondutor', 'cpfCondutor', 'cnh', 'cnhEstrangeira', 'ufCnh']
        widgets = {
            'nomeCondutor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Condutor'}),
            'cpfCondutor': forms.TextInput(attrs={'class': 'form-control cpf-mask', 'placeholder': '000.000.000-00'}),
            'cnh': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CNH'}),
            'cnhEstrangeira': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CNH Estrangeira'}),
            'ufCnh': forms.Select(attrs={'class': 'form-select'}),
        }


class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ['placa', 'chassi', 'marca', 'modelo', 'cor', 'especie', 'categoria', 'ufVeiculo', 'municipioVeiculo']
        widgets = {
            'placa': forms.TextInput(attrs={'class': 'form-control placa-mask', 'placeholder': 'ABC1234'}),
            'chassi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Chassi'}),
            'marca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Marca'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Modelo'}),
            'cor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cor'}),
            'especie': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'ufVeiculo': forms.Select(attrs={'class': 'form-select'}),
            'municipioVeiculo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Município'}),
        }


class AitForm(forms.ModelForm):
    class Meta:
        model = Ait
        fields = ['ait']
        widgets = {
            'ait': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código AIT'}),
        }


class EnquadramentoForm(forms.ModelForm):
    class Meta:
        model = Enquadramento
        fields = ['enquadramento']
        widgets = {
            'enquadramento': forms.Select(attrs={'class': 'form-select'}),
        }


class ArrendatarioForm(forms.ModelForm):
    class Meta:
        model = Arrendatario
        fields = ['arrendatario']
        widgets = {
            'arrendatario': forms.Select(attrs={'class': 'form-select'}),
        }


class ImagemCrrForm(forms.ModelForm):
    class Meta:
        model = ImagemCrr
        fields = ['imagem']
        widgets = {
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class TabelaArrendatarioForm(forms.ModelForm):
    class Meta:
        model = TabelaArrendatario
        fields = [
            'nome_arrendatario', 'cnpj_arrendatario', 'endereco_arrendatario',
            'numero_arrendatario', 'complemento_arrendatario', 'bairro_arrendatario',
            'cidade_arrendatario', 'uf_arrendatario', 'cep_arrendatario',
        ]
        widgets = {
            'nome_arrendatario': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj_arrendatario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0001-00'}),
            'endereco_arrendatario': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_arrendatario': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento_arrendatario': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro_arrendatario': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade_arrendatario': forms.TextInput(attrs={'class': 'form-control'}),
            'uf_arrendatario': forms.Select(attrs={'class': 'form-select'}),
            'cep_arrendatario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
        }


class TabelaEnquadramentoForm(forms.ModelForm):
    class Meta:
        model = TabelaEnquadramento
        fields = ['codigo', 'amparo_legal', 'descricao_infracao']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 51930'}),
            'amparo_legal': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao_infracao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class UsuarioCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Senha', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(
        label='Confirmar Senha', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        from django.contrib.auth.models import User
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'is_active', 'is_staff', 'is_superuser', 'groups']
        widgets = {
            'username':     forms.TextInput(attrs={'class': 'form-control'}),
            'first_name':   forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':    forms.TextInput(attrs={'class': 'form-control'}),
            'email':        forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active':    forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff':     forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'groups':       forms.CheckboxSelectMultiple(),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('As senhas não coincidem.')
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            self.save_m2m()
        return user


class UsuarioEditForm(forms.ModelForm):
    nova_senha = forms.CharField(
        label='Nova Senha (opcional)', required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 'Deixe em branco para não alterar'
        }),
    )

    class Meta:
        from django.contrib.auth.models import User
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'is_active', 'is_staff', 'is_superuser', 'groups']
        widgets = {
            'username':     forms.TextInput(attrs={'class': 'form-control'}),
            'first_name':   forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':    forms.TextInput(attrs={'class': 'form-control'}),
            'email':        forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active':    forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff':     forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'groups':       forms.CheckboxSelectMultiple(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        nova_senha = self.cleaned_data.get('nova_senha')
        if nova_senha:
            user.set_password(nova_senha)
        if commit:
            user.save()
            self.save_m2m()
        return user


class GrupoForm(forms.ModelForm):
    class Meta:
        from django.contrib.auth.models import Group
        model = Group
        fields = ['name', 'permissions']
        widgets = {
            'name':        forms.TextInput(attrs={'class': 'form-control'}),
            'permissions': forms.CheckboxSelectMultiple(),
        }


class AgenteForm(forms.ModelForm):
    nova_senha = forms.CharField(
        label='Nova Senha (opcional)',
        required=False,
        min_length=4,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Deixe em branco para não alterar'}),
        help_text='Se preenchido, a senha será redefinida e o agente deverá alterá-la no próximo acesso.',
    )

    class Meta:
        model = Agente
        fields = ['matricula', 'nome', 'ativo', 'assinatura']
        widgets = {
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'assinatura': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        agente = super().save(commit=False)
        nova_senha = self.cleaned_data.get('nova_senha')
        if nova_senha:
            agente.set_senha(nova_senha)
            agente.senha_alterada = False
        if commit:
            agente.save()
        return agente


# Formsets para os modelos relacionados
CondutorFormSet = inlineformset_factory(
    Crr, Condutor, form=CondutorForm,
    extra=1, max_num=1, can_delete=True
)

VeiculoFormSet = inlineformset_factory(
    Crr, Veiculo, form=VeiculoForm,
    extra=1, max_num=1, can_delete=True
)

AitFormSet = inlineformset_factory(
    Crr, Ait, form=AitForm,
    extra=1, max_num=4, can_delete=True
)

EnquadramentoFormSet = inlineformset_factory(
    Crr, Enquadramento, form=EnquadramentoForm,
    extra=1, max_num=4, can_delete=True
)

ArrendatarioFormSet = inlineformset_factory(
    Crr, Arrendatario, form=ArrendatarioForm,
    extra=1, max_num=1, can_delete=True
)

ImagemCrrFormSet = inlineformset_factory(
    Crr, ImagemCrr, form=ImagemCrrForm,
    extra=1, max_num=4, can_delete=True
)
