from rest_framework import serializers
from .models import (
    Crr,
    Veiculo,
    Condutor,
    Ait,
    Enquadramento,
    TabelaEnquadramento,
    ImagemCrr,
    DispositivoMobile,
    Arrendatario,
)


class VeiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veiculo
        exclude = ['crr']


class CondutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condutor
        exclude = ['crr']


class AitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ait
        exclude = ['crr']


class TabelaEnquadramentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TabelaEnquadramento
        fields = '__all__'


class EnquadramentoSerializer(serializers.ModelSerializer):
    enquadramento = serializers.SlugRelatedField(
        slug_field='codigo',
        queryset=TabelaEnquadramento.objects.all()
    )

    class Meta:
        model = Enquadramento
        exclude = ['crr']


class ImagemCrrSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagemCrr
        fields = ['nomeArquivo', 'url']


class CrrSerializer(serializers.ModelSerializer):
    placa = serializers.CharField(write_only=True)
    chassi = serializers.CharField(write_only=True)
    marca = serializers.CharField(write_only=True)
    modelo = serializers.CharField(write_only=True)
    cor = serializers.CharField(write_only=True)
    nomeCondutor = serializers.CharField(write_only=True)
    cpfCondutor = serializers.CharField(write_only=True)
    cnh = serializers.CharField(write_only=True)
    cnhEstrangeira = serializers.CharField(write_only=True)
    aits = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    enquadramentos = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    imagens = ImagemCrrSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Crr
        fields = [
            'numeroCrr', 'localFiscalizacao', 'municipioEstadoFiscalizacao', 'dataFiscalizacao',
            'horaFiscalizacao', 'medidaAdministrativa', 'localPatio', 'placaGuincho',
            'encarregado', 'observacao', 'matriculaAgente',
            'placa', 'chassi', 'marca', 'modelo', 'cor',
            'nomeCondutor', 'cpfCondutor', 'cnh', 'cnhEstrangeira',
            'aits', 'enquadramentos', 'imagens'
        ]

    def create(self, validated_data):
        veiculo_data = {
            'placa': validated_data.pop('placa'),
            'chassi': validated_data.pop('chassi'),
            'marca': validated_data.pop('marca'),
            'modelo': validated_data.pop('modelo'),
            'cor': validated_data.pop('cor'),
        }
        condutor_data = {
            'nomeCondutor': validated_data.pop('nomeCondutor'),
            'cpfCondutor': validated_data.pop('cpfCondutor'),
            'cnh': validated_data.pop('cnh'),
            'cnhEstrangeira': validated_data.pop('cnhEstrangeira'),
        }

        aits_list = validated_data.pop('aits', [])
        enquadramentos_list = validated_data.pop('enquadramentos', [])
        imagens_data = validated_data.pop('imagens', [])

        try:
            crr = Crr.objects.create(**validated_data)
            Veiculo.objects.create(crr=crr, **veiculo_data)
            Condutor.objects.create(crr=crr, **condutor_data)

            for numero_ait in aits_list:
                Ait.objects.create(crr=crr, ait=numero_ait)

            for imagem in imagens_data[:8]:
                ImagemCrr.objects.create(crr=crr, **imagem)

            for codigo in enquadramentos_list:
                codigo_str = str(codigo).zfill(5)
                if not codigo_str.isdigit() or len(codigo_str) != 5:
                    raise serializers.ValidationError(
                        f"Código de enquadramento inválido: '{codigo_str}'. Deve conter 5 dígitos numéricos."
                    )
                enquad_obj, _ = TabelaEnquadramento.objects.get_or_create(
                    codigo=codigo_str,
                    defaults={
                        "amparo_legal": "NÃO INFORMADO",
                        "descricao_infracao": ""
                    }
                )
                Enquadramento.objects.create(crr=crr, enquadramento=enquad_obj)

            return crr

        except Exception as e:
            raise serializers.ValidationError(f"Erro ao criar CRR: {e}")

    def validate(self, data):
        campos = ['placa', 'marca', 'nomeCondutor', 'cpfCondutor', 'dataFiscalizacao', 'horaFiscalizacao']
        for campo in campos:
            if not data.get(campo):
                raise serializers.ValidationError(f"O campo '{campo}' é obrigatório.")
        return data


class ArrendatarioDetalheSerializer(serializers.ModelSerializer):
    nomeArrendatario = serializers.CharField(source='arrendatario.nome_arrendatario', read_only=True)
    cnpjArrendatario = serializers.CharField(source='arrendatario.cnpj_arrendatario', read_only=True)
    enderecoArrendatario = serializers.CharField(source='arrendatario.endereco_arrendatario', read_only=True)
    numeroArrendatario = serializers.CharField(source='arrendatario.numero_arrendatario', read_only=True)
    complementoArrendatario = serializers.CharField(source='arrendatario.complemento_arrendatario', read_only=True)
    bairroArrendatario = serializers.CharField(source='arrendatario.bairro_arrendatario', read_only=True)
    cidadeArrendatario = serializers.CharField(source='arrendatario.cidade_arrendatario', read_only=True)
    ufArrendatario = serializers.CharField(source='arrendatario.uf_arrendatario', read_only=True)
    cepArrendatario = serializers.CharField(source='arrendatario.cep_arrendatario', read_only=True)

    class Meta:
        model = Arrendatario
        fields = [
            'id',
            'nomeArrendatario',
            'cnpjArrendatario',
            'enderecoArrendatario',
            'numeroArrendatario',
            'complementoArrendatario',
            'bairroArrendatario',
            'cidadeArrendatario',
            'ufArrendatario',
            'cepArrendatario',
        ]


class EnquadramentoDetalheSerializer(serializers.ModelSerializer):
    detalhe = TabelaEnquadramentoSerializer(source='enquadramento', read_only=True)

    class Meta:
        model = Enquadramento
        fields = ['id', 'detalhe']


class ImagemCrrDetalheSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagemCrr
        fields = ['id', 'nomeArquivo', 'url']


class CrrJavaSerializer(serializers.ModelSerializer):
    placa = serializers.SerializerMethodField()
    marca = serializers.SerializerMethodField()
    modelo = serializers.SerializerMethodField()
    aits = serializers.SerializerMethodField()
    enquadramentos = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()
    local = serializers.SerializerMethodField()
    nomeCondutor = serializers.SerializerMethodField()
    cpfCondutor = serializers.SerializerMethodField()
    cnh = serializers.SerializerMethodField()
    cnhEstrangeira = serializers.SerializerMethodField()
    ufCnh = serializers.SerializerMethodField()
    assinaturaCondutor = serializers.SerializerMethodField()

    class Meta:
        model = Crr
        fields = [
            'id',
            'numeroCrr',
            'status',
            'placa',
            'marca',
            'modelo',
            'data',
            'local',
            'aits',
            'enquadramentos',
            'nomeCondutor',
            'cpfCondutor',
            'cnh',
            'cnhEstrangeira',
            'ufCnh',
            'assinaturaCondutor',
        ]

    def get_placa(self, obj):
        v = obj.veiculo.first()
        return v.placa if v else ''

    def get_marca(self, obj):
        v = obj.veiculo.first()
        return v.marca if v else ''

    def get_modelo(self, obj):
        v = obj.veiculo.first()
        return v.modelo if v else ''

    def get_data(self, obj):
        return obj.dataFiscalizacao.isoformat() if obj.dataFiscalizacao else ''

    def get_local(self, obj):
        local = obj.localFiscalizacao or ''
        municipio = obj.municipioEstadoFiscalizacao or ''
        if local and municipio:
            return f'{local} - {municipio}'
        return local or municipio

    def get_aits(self, obj):
        return [a.ait for a in obj.aits.all() if a.ait]

    def get_enquadramentos(self, obj):
        return [
            str(e.enquadramento.codigo)
            for e in obj.enquadramentos.select_related('enquadramento').all()
            if e.enquadramento and e.enquadramento.codigo
        ]

    def get_nomeCondutor(self, obj):
        c = obj.condutores.first()
        return c.nomeCondutor if c else ''

    def get_cpfCondutor(self, obj):
        c = obj.condutores.first()
        return c.cpfCondutor if c else ''

    def get_cnh(self, obj):
        c = obj.condutores.first()
        return c.cnh if c else ''

    def get_cnhEstrangeira(self, obj):
        c = obj.condutores.first()
        return c.cnhEstrangeira if c else ''

    def get_ufCnh(self, obj):
        c = obj.condutores.first()
        return c.ufCnh if c else ''

    def get_assinaturaCondutor(self, obj):
        c = obj.condutores.first()
        return c.assinaturaCondutor if c else ''


class CrrJavaDetalheSerializer(serializers.ModelSerializer):
    veiculo = VeiculoSerializer(many=True, read_only=True)
    condutores = CondutorSerializer(many=True, read_only=True)
    aits = AitSerializer(many=True, read_only=True)
    enquadramentos = EnquadramentoDetalheSerializer(many=True, read_only=True)
    arrendatarios = ArrendatarioDetalheSerializer(many=True, read_only=True)
    imagens = ImagemCrrDetalheSerializer(many=True, read_only=True)
    data = serializers.SerializerMethodField()
    hora = serializers.SerializerMethodField()
    local = serializers.SerializerMethodField()

    class Meta:
        model = Crr
        fields = [
            'id',
            'numeroCrr',
            'status',
            'situacaoEntrega',
            'not_gerada',
            'edital_emitido',
            'matriculaAgente',
            'medidaAdministrativa',
            'observacao',
            'placaGuincho',
            'encarregado',
            'localPatio',
            'localFiscalizacao',
            'municipioEstadoFiscalizacao',
            'dataFiscalizacao',
            'horaFiscalizacao',
            'data',
            'hora',
            'local',
            'veiculo',
            'condutores',
            'aits',
            'enquadramentos',
            'arrendatarios',
            'imagens',
            'criado_em',
            'editado_em',
        ]

    def get_data(self, obj):
        return obj.dataFiscalizacao.isoformat() if obj.dataFiscalizacao else ''

    def get_hora(self, obj):
        return obj.horaFiscalizacao.strftime('%H:%M:%S') if obj.horaFiscalizacao else ''

    def get_local(self, obj):
        local = obj.localFiscalizacao or ''
        municipio = obj.municipioEstadoFiscalizacao or ''
        if local and municipio:
            return f'{local} - {municipio}'
        return local or municipio


class CrrStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crr
        fields = ['status']

    def validate_status(self, value):
        if value != 'liberado':
            raise serializers.ValidationError(
                "Apenas é permitido atualizar o status para 'liberado'."
            )
        return value


class VeiculoPublicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veiculo
        fields = ['placa', 'marca', 'modelo', 'cor']


class ConsultaExterna(serializers.ModelSerializer):
    veiculo = serializers.SerializerMethodField()

    class Meta:
        model = Crr
        fields = [
            'numeroCrr',
            'veiculo',
            'status',
            'localPatio',
            'dataFiscalizacao',
            'horaFiscalizacao',
            'localFiscalizacao',
        ]

    def get_veiculo(self, obj):
        veiculo = obj.veiculo.first()
        if veiculo:
            return VeiculoPublicoSerializer(veiculo).data
        return None


class DispositivoRegistroSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=100)
    imei = serializers.CharField(max_length=20)
    matricula = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_imei(self, value):
        dispositivo = DispositivoMobile.objects.filter(imei=value).first()
        if dispositivo:
            raise serializers.ValidationError(
                f"DEVICE_EXISTS:{dispositivo.api_key}"
            )
        return value

    def create(self, validated_data):
        validated_data.pop('matricula', '')
        dispositivo = DispositivoMobile.objects.create(
            nome=validated_data['nome'],
            imei=validated_data['imei'],
        )
        return dispositivo


class DispositivoLoginSerializer(serializers.Serializer):
    imei = serializers.CharField(max_length=20)
    api_key = serializers.CharField(max_length=64, required=False, allow_blank=True)


class DispositivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DispositivoMobile
        fields = ['id', 'nome', 'imei', 'api_key', 'ativo']
        read_only_fields = ['api_key']


class CrrMobileReadSerializer(serializers.ModelSerializer):
    placa = serializers.SerializerMethodField()
    chassi = serializers.SerializerMethodField()
    marca = serializers.SerializerMethodField()
    modelo = serializers.SerializerMethodField()
    cor = serializers.SerializerMethodField()
    nomeCondutor = serializers.SerializerMethodField()
    cpfCondutor = serializers.SerializerMethodField()
    cnh = serializers.SerializerMethodField()
    cnhEstrangeira = serializers.SerializerMethodField()
    assinaturaCondutor = serializers.SerializerMethodField()
    aits = serializers.SerializerMethodField()
    enquadramentos = serializers.SerializerMethodField()

    class Meta:
        model = Crr
        fields = [
            'id', 'numeroCrr', 'localFiscalizacao',
            'municipioEstadoFiscalizacao',
            'dataFiscalizacao', 'horaFiscalizacao',
            'medidaAdministrativa', 'localPatio',
            'placaGuincho', 'encarregado', 'observacao',
            'matriculaAgente', 'status', 'situacaoEntrega', 'criado_em',
            'placa', 'chassi', 'marca', 'modelo', 'cor',
            'nomeCondutor', 'cpfCondutor',
            'cnh', 'cnhEstrangeira', 'assinaturaCondutor',
            'aits', 'enquadramentos',
        ]

    def get_placa(self, obj):
        v = obj.veiculo.first()
        return v.placa if v else ''

    def get_chassi(self, obj):
        v = obj.veiculo.first()
        return v.chassi if v else ''

    def get_marca(self, obj):
        v = obj.veiculo.first()
        return v.marca if v else ''

    def get_modelo(self, obj):
        v = obj.veiculo.first()
        return v.modelo if v else ''

    def get_cor(self, obj):
        v = obj.veiculo.first()
        return v.cor if v else ''

    def get_nomeCondutor(self, obj):
        c = obj.condutores.first()
        return c.nomeCondutor if c else ''

    def get_cpfCondutor(self, obj):
        c = obj.condutores.first()
        return c.cpfCondutor if c else ''

    def get_cnh(self, obj):
        c = obj.condutores.first()
        return c.cnh if c else ''

    def get_cnhEstrangeira(self, obj):
        c = obj.condutores.first()
        return c.cnhEstrangeira if c else ''

    def get_assinaturaCondutor(self, obj):
        c = obj.condutores.first()
        return c.assinaturaCondutor if c else ''

    def get_aits(self, obj):
        return [a.ait for a in obj.aits.all()]

    def get_enquadramentos(self, obj):
        return [
            str(e.enquadramento.codigo)
            for e in obj.enquadramentos.all()
            if e.enquadramento
        ]


class CrrMobileSerializer(serializers.ModelSerializer):
    numeroCrr = serializers.CharField(required=False, allow_blank=True, default='')
    dataFiscalizacao = serializers.DateField(input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'])
    horaFiscalizacao = serializers.TimeField(input_formats=['%H:%M', '%H:%M:%S'])
    placa = serializers.CharField(write_only=True, required=False, allow_blank=True)
    chassi = serializers.CharField(write_only=True, required=False, allow_blank=True)
    marca = serializers.CharField(write_only=True, required=False, allow_blank=True)
    modelo = serializers.CharField(write_only=True, required=False, allow_blank=True)
    cor = serializers.CharField(write_only=True, required=False, allow_blank=True)
    nomeCondutor = serializers.CharField(write_only=True, required=False, allow_blank=True)
    cpfCondutor = serializers.CharField(write_only=True, required=False, allow_blank=True)
    cnh = serializers.CharField(write_only=True, required=False, allow_blank=True)
    cnhEstrangeira = serializers.CharField(write_only=True, required=False, allow_blank=True)
    aits = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    enquadramentos = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    imagens = serializers.ListField(child=serializers.CharField(), write_only=True, required=False, default=list)
    veiculoSemIdentificacao = serializers.BooleanField(write_only=True, required=False, default=False)
    situacaoEntrega = serializers.CharField(required=False, allow_blank=True, default='')
    sincronizado = serializers.BooleanField(read_only=True, default=True)

    def validate_situacaoEntrega(self, value):
        return value.lower() if value else value

    class Meta:
        model = Crr
        fields = [
            'id', 'numeroCrr', 'localFiscalizacao', 'municipioEstadoFiscalizacao',
            'dataFiscalizacao', 'horaFiscalizacao', 'medidaAdministrativa',
            'localPatio', 'placaGuincho', 'encarregado', 'observacao',
            'matriculaAgente', 'status', 'situacaoEntrega', 'criado_em',
            'placa', 'chassi', 'marca', 'modelo', 'cor',
            'nomeCondutor', 'cpfCondutor', 'cnh', 'cnhEstrangeira',
            'aits', 'enquadramentos', 'imagens', 'veiculoSemIdentificacao',
            'sincronizado'
        ]
        read_only_fields = ['id', 'status', 'criado_em']

    def validate_numeroCrr(self, value):
        if not value:
            from django.db import connection, transaction
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute('LOCK TABLE crr_crr IN SHARE ROW EXCLUSIVE MODE')
                from django.db.models import Max, IntegerField
                from django.db.models.functions import Cast, Substr
                resultado = Crr.objects.filter(
                    numeroCrr__regex=r'^[eE]\d+'
                ).annotate(
                    num_part=Cast(Substr('numeroCrr', 2), IntegerField())
                ).aggregate(max_num=Max('num_part'))
                proximo = (resultado['max_num'] or 0) + 1
                return f"E{proximo:04d}"

        value = value.upper()
        if not value.startswith('E'):
            raise serializers.ValidationError(
                "Número do CRR deve começar com 'E' (ex: E0001)"
            )

        if Crr.objects.filter(numeroCrr__iexact=value).exists():
            raise serializers.ValidationError(
                f"CRR {value} já existe no sistema."
            )

        return value

    def create(self, validated_data):
        veiculo_data = {
            'placa': validated_data.pop('placa', ''),
            'chassi': validated_data.pop('chassi', ''),
            'marca': validated_data.pop('marca', ''),
            'modelo': validated_data.pop('modelo', ''),
            'cor': validated_data.pop('cor', ''),
        }
        condutor_data = {
            'nomeCondutor': validated_data.pop('nomeCondutor', ''),
            'cpfCondutor': validated_data.pop('cpfCondutor', ''),
            'cnh': validated_data.pop('cnh', ''),
            'cnhEstrangeira': validated_data.pop('cnhEstrangeira', ''),
        }

        aits_list = validated_data.pop('aits', [])
        enquadramentos_list = validated_data.pop('enquadramentos', [])
        imagens_data = validated_data.pop('imagens', [])
        validated_data.pop('veiculoSemIdentificacao', None)

        try:
            crr = Crr.objects.create(**validated_data)

            if any(veiculo_data.values()):
                Veiculo.objects.create(crr=crr, **veiculo_data)

            if any(condutor_data.values()):
                Condutor.objects.create(crr=crr, **condutor_data)

            for numero_ait in aits_list:
                if numero_ait:
                    Ait.objects.create(crr=crr, ait=numero_ait)

            import base64 as b64mod
            import logging
            from django.core.files.base import ContentFile
            logger = logging.getLogger(__name__)
            for i, imagem in enumerate(imagens_data[:8]):
                try:
                    if isinstance(imagem, str) and len(imagem) > 100:
                        img_bytes = b64mod.b64decode(imagem)
                        nome = f"crr_{crr.numeroCrr}_{i+1}.jpg"
                        img_file = ContentFile(img_bytes, name=nome)
                        imagem_obj = ImagemCrr(crr=crr, nomeArquivo=nome)
                        imagem_obj.imagem.save(nome, img_file, save=True)
                        logger.info(f"Imagem {nome} salva com sucesso. URL: {imagem_obj.imagem.url}")
                    elif isinstance(imagem, dict):
                        ImagemCrr.objects.create(crr=crr, **imagem)
                except Exception as e:
                    logger.error(f"Erro ao salvar imagem {i+1} do CRR {crr.numeroCrr}: {e}", exc_info=True)

            for codigo in enquadramentos_list:
                if codigo:
                    codigo_str = str(codigo).zfill(5)
                    enquad_obj, _ = TabelaEnquadramento.objects.get_or_create(
                        codigo=codigo_str,
                        defaults={
                            "amparo_legal": "NÃO INFORMADO",
                            "descricao_infracao": ""
                        }
                    )
                    Enquadramento.objects.create(crr=crr, enquadramento=enquad_obj)

            try:
                from .email_utils import enviar_email_crr
                enviar_email_crr(crr)
            except Exception:
                pass

            return crr

        except Exception as e:
            raise serializers.ValidationError(f"Erro ao criar CRR: {e}")


class SincronizacaoSerializer(serializers.Serializer):
    crrs = CrrMobileSerializer(many=True)

    def create(self, validated_data):
        crrs_data = validated_data.get('crrs', [])
        resultados = []

        for crr_data in crrs_data:
            serializer = CrrMobileSerializer(data=crr_data)
            try:
                if serializer.is_valid(raise_exception=True):
                    crr = serializer.save()
                    resultados.append({
                        'numeroCrr': crr.numeroCrr,
                        'status': 'sucesso',
                        'id': crr.id
                    })
            except serializers.ValidationError as e:
                resultados.append({
                    'numeroCrr': crr_data.get('numeroCrr', 'desconhecido'),
                    'status': 'erro',
                    'erro': str(e.detail)
                })

        return resultados
