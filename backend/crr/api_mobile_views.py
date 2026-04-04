# api_mobile_views.py
"""
API para aplicativo mobile de cadastro de CRR.
Autenticação via API Key (header X-API-Key).
"""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import DispositivoMobile, TabelaEnquadramento, Agente
from .permissions import IsDispositivoMobile
from .serializers import (
    CrrMobileReadSerializer,
    DispositivoSerializer,
    CrrMobileSerializer,
    DispositivoLoginSerializer,
    DispositivoRegistroSerializer,
    TabelaEnquadramentoSerializer,
)


MOBILE_API_KEY_PARAMETER = OpenApiParameter(
    name='X-API-Key',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.HEADER,
    required=True,
    description='API Key do dispositivo mobile.',
)

MOBILE_MATRICULA_PARAMETER = OpenApiParameter(
    name='X-Matricula',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.HEADER,
    required=False,
    description='Matrícula do agente usada em alguns endpoints mobile.',
)


# ==================== ATIVACAO E LOGIN ==================== #

@extend_schema(
    summary='Ativa um dispositivo mobile',
    request=inline_serializer(
        name='AtivarDispositivoRequest',
        fields={
            'codigo': serializers.CharField(),
            'matricula': serializers.CharField(),
            'senha': serializers.CharField(),
        },
    ),
    responses=OpenApiTypes.OBJECT,
)
@api_view(['POST'])
@permission_classes([AllowAny])
def ativar_dispositivo(request):
    """
    Ativa um dispositivo mobile usando o codigo de ativacao.

    POST /api/v1/mobile/ativar/
    {
        "codigo": "123456",
        "matricula": "12345"
    }

    Retorna a API Key para autenticacao nas proximas requests.
    """
    codigo = request.data.get('codigo', '').strip()
    matricula = request.data.get('matricula', '').strip()

    if not codigo:
        return Response({
            'sucesso': False,
            'erro': 'Codigo de ativacao e obrigatorio'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        dispositivo = DispositivoMobile.objects.get(codigo_ativacao=codigo)
    except DispositivoMobile.DoesNotExist:
        return Response({
            'sucesso': False,
            'erro': 'Codigo de ativacao invalido'
        }, status=status.HTTP_404_NOT_FOUND)

    if not dispositivo.ativo:
        return Response({
            'sucesso': False,
            'erro': 'Dispositivo desativado. Contate o administrador.'
        }, status=status.HTTP_403_FORBIDDEN)

    if dispositivo.ativado:
        return Response({
            'sucesso': False,
            'erro': 'Código de ativação já utilizado. Solicite ao administrador a liberação do dispositivo.'
        }, status=status.HTTP_403_FORBIDDEN)

    # Valida matricula do agente
    if not matricula:
        return Response({
            'sucesso': False,
            'erro': 'Matricula do agente e obrigatoria'
        }, status=status.HTTP_400_BAD_REQUEST)

    senha = request.data.get('senha', '').strip()
    if not senha:
        return Response({
            'sucesso': False,
            'erro': 'Senha e obrigatoria'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        agente = Agente.objects.get(matricula=matricula)
        if not agente.ativo:
            return Response({
                'sucesso': False,
                'erro': 'Agente desativado. Contate o administrador.'
            }, status=status.HTTP_403_FORBIDDEN)
    except Agente.DoesNotExist:
        return Response({
            'sucesso': False,
            'erro': 'Matricula nao cadastrada. Contate o administrador.'
        }, status=status.HTTP_404_NOT_FOUND)

    # Valida senha do agente
    if not agente.check_senha(senha):
        return Response({
            'sucesso': False,
            'erro': 'Senha incorreta'
        }, status=status.HTTP_403_FORBIDDEN)

    from django.utils import timezone
    dispositivo.ativado = True
    dispositivo.ultimo_acesso = timezone.now()
    dispositivo.save()

    return Response({
        'sucesso': True,
        'mensagem': 'Dispositivo ativado com sucesso',
        'dispositivo': DispositivoSerializer(dispositivo).data,
        'senha_alterada': agente.senha_alterada,
        'assinatura_url': agente.assinatura.url if agente.assinatura else None,
    })


@extend_schema(
    summary='Registra um dispositivo mobile',
    request=DispositivoRegistroSerializer,
    responses=OpenApiTypes.OBJECT,
)
@api_view(['POST'])
@permission_classes([AllowAny])
def registrar_dispositivo(request):
    """
    Registra um novo dispositivo mobile via identificador do app.

    POST /api/v1/mobile/registrar/
    {
        "nome": "Tablet Agente 01",
        "device_id": "f2811296-afb2-459f-a530-4e7867c44e69",
        "matricula": "12345"
    }

    Tambem aceita o campo legado "imei" por compatibilidade.
    Se o dispositivo ja existir (mesmo identificador), retorna os dados do dispositivo existente.
    O dispositivo deve ser ativado pelo administrador no painel web.
    """
    serializer = DispositivoRegistroSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    device_id = serializer.validated_data['device_id']

    # Verifica se dispositivo ja existe com este identificador
    dispositivo = DispositivoMobile.objects.filter(device_id=device_id).first()

    if dispositivo:
        # Atualiza ultimo acesso
        from django.utils import timezone
        dispositivo.ultimo_acesso = timezone.now()
        dispositivo.save()

        return Response({
            'sucesso': True,
            'mensagem': 'Dispositivo encontrado',
            'dispositivo': DispositivoSerializer(dispositivo).data,
            'novo': False
        })

    # Cria novo dispositivo
    dispositivo = serializer.save()

    return Response({
        'sucesso': True,
        'mensagem': 'Dispositivo registrado. Aguarde a ativacao pelo administrador.',
        'dispositivo': DispositivoSerializer(dispositivo).data,
        'novo': True
    }, status=status.HTTP_201_CREATED)


@extend_schema(
    summary='Realiza login do dispositivo por identificador',
    request=DispositivoLoginSerializer,
    responses=OpenApiTypes.OBJECT,
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_dispositivo(request):
    """
    Login de dispositivo existente via identificador do app.

    POST /api/v1/mobile/login/
    {
        "device_id": "f2811296-afb2-459f-a530-4e7867c44e69"
    }

    Tambem aceita o campo legado "imei" por compatibilidade.
    Retorna dados do dispositivo.
    """
    serializer = DispositivoLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    device_id = serializer.validated_data['device_id']

    try:
        dispositivo = DispositivoMobile.objects.get(device_id=device_id)

        if not dispositivo.ativo:
            return Response({
                'sucesso': False,
                'erro': 'Dispositivo desativado. Contate o administrador.'
            }, status=status.HTTP_403_FORBIDDEN)

        # Atualiza ultimo acesso
        from django.utils import timezone
        dispositivo.ultimo_acesso = timezone.now()
        dispositivo.save()

        return Response({
            'sucesso': True,
            'dispositivo': DispositivoSerializer(dispositivo).data,
        })

    except DispositivoMobile.DoesNotExist:
        return Response({
            'sucesso': False,
            'erro': 'Dispositivo nao registrado. Faca o registro primeiro.'
        }, status=status.HTTP_404_NOT_FOUND)



@extend_schema(
    summary='Obtém o próximo número de CRR',
    parameters=[MOBILE_API_KEY_PARAMETER],
    responses=OpenApiTypes.OBJECT,
)
@api_view(['GET'])
@permission_classes([IsDispositivoMobile])
def obter_proximo_numero(request):
    """
    Retorna o proximo numero CRR disponivel.
    Gera sequencialmente a partir do maior numeroCrr existente.

    GET /api/v1/mobile/crr/proximo-numero/
    Header: X-API-Key: <api_key>
    """
    from .models import Crr
    from django.db.models import Max, IntegerField
    from django.db.models.functions import Cast, Substr

    resultado = Crr.objects.filter(
        numeroCrr__regex=r'^[eE]\d+'
    ).annotate(
        num_part=Cast(Substr('numeroCrr', 2), IntegerField())
    ).aggregate(max_num=Max('num_part'))

    proximo = (resultado['max_num'] or 0) + 1
    numero_formatado = f"E{proximo:04d}"

    return Response({
        'sucesso': True,
        'proximo_numero': numero_formatado,
    })


# ==================== CRUD DE CRR ==================== #

@extend_schema(
    summary='Lista CRRs do agente',
    parameters=[MOBILE_API_KEY_PARAMETER, MOBILE_MATRICULA_PARAMETER],
    responses=CrrMobileReadSerializer(many=True),
)
@api_view(['GET'])
@permission_classes([IsDispositivoMobile])
def listar_crrs(request):
    """
    Lista os CRRs criados pelo agente do dispositivo.

    GET /api/v1/mobile/crr/
    Header: X-API-Key: <api_key>
    """
    from .models import Crr
    from .serializers import CrrMobileReadSerializer
    matricula = request.headers.get('X-Matricula', '').strip()

    crrs = Crr.objects.filter(
        matriculaAgente=matricula
    ).prefetch_related(
        'veiculo', 'condutores', 'aits',
        'enquadramentos__enquadramento',
    ).order_by('-criado_em')[:10]

    return Response({
        'sucesso': True,
        'total': crrs.count(),
        'crrs': CrrMobileReadSerializer(crrs, many=True).data
    })


@extend_schema(
    summary='Busca CRRs por filtros',
    parameters=[
        MOBILE_API_KEY_PARAMETER,
        OpenApiParameter('placa', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Placa do veículo'),
        OpenApiParameter('marca', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Marca do veículo'),
        OpenApiParameter('modelo', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Modelo do veículo'),
        OpenApiParameter('data', OpenApiTypes.DATE, OpenApiParameter.QUERY, description='Data da fiscalização'),
        OpenApiParameter('numeroCrr', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Número do CRR'),
    ],
    responses=CrrMobileReadSerializer(many=True),
)
@api_view(['GET'])
@permission_classes([IsDispositivoMobile])
def buscar_crrs(request):
    """
    Busca CRRs por filtros: placa, marca, modelo, data.

    GET /api/v1/mobile/crr/buscar/?placa=ABC&marca=FORD&modelo=FIESTA&data=2024-01-01
    Header: X-API-Key: <api_key>
    """
    from .models import Crr
    from .serializers import CrrMobileReadSerializer

    placa = request.query_params.get('placa', '').strip()
    marca = request.query_params.get('marca', '').strip()
    modelo = request.query_params.get('modelo', '').strip()
    data = request.query_params.get('data', '').strip()

    numero_crr = request.query_params.get('numeroCrr', '').strip()

    if not any([placa, marca, modelo, data, numero_crr]):
        return Response({
            'sucesso': False,
            'erro': 'Informe ao menos um filtro de busca'
        }, status=status.HTTP_400_BAD_REQUEST)

    crrs = Crr.objects.prefetch_related(
        'veiculo', 'condutores', 'aits',
        'enquadramentos__enquadramento',
    )

    if numero_crr:
        crrs = crrs.filter(numeroCrr__icontains=numero_crr)
    if placa:
        crrs = crrs.filter(veiculo__placa__icontains=placa)
    if marca:
        crrs = crrs.filter(veiculo__marca__icontains=marca)
    if modelo:
        crrs = crrs.filter(veiculo__modelo__icontains=modelo)
    if data:
        crrs = crrs.filter(dataFiscalizacao=data)

    crrs = crrs.order_by('-criado_em')[:20]

    return Response({
        'sucesso': True,
        'total': crrs.count(),
        'crrs': CrrMobileReadSerializer(crrs, many=True).data
    })


@extend_schema(
    summary='Cria um novo CRR via mobile',
    parameters=[MOBILE_API_KEY_PARAMETER],
    request=CrrMobileSerializer,
    responses=CrrMobileSerializer,
)
@api_view(['POST'])
@permission_classes([IsDispositivoMobile])
def criar_crr(request):
    """
    Cria um novo CRR.

    POST /api/v1/mobile/crr/
    Header: X-API-Key: <api_key>

    O numeroCrr deve ser do lote atribuído ao dispositivo.
    """
    serializer = CrrMobileSerializer(data=request.data)

    if serializer.is_valid():
        crr = serializer.save()
        return Response({
            'sucesso': True,
            'mensagem': f'CRR {crr.numeroCrr} criado com sucesso',
            'crr': CrrMobileSerializer(crr).data
        }, status=status.HTTP_201_CREATED)

    return Response({
        'sucesso': False,
        'erros': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(
    summary='Atualiza dados do condutor do CRR',
    parameters=[MOBILE_API_KEY_PARAMETER, MOBILE_MATRICULA_PARAMETER],
    request=inline_serializer(
        name='AtualizarCondutorCrrRequest',
        fields={
            'situacaoEntrega': serializers.CharField(required=False),
            'assinaturaCondutor': serializers.CharField(required=False),
        },
    ),
    responses=OpenApiTypes.OBJECT,
)
@api_view(['PATCH'])
@permission_classes([IsDispositivoMobile])
def atualizar_condutor_crr(request, crr_id):
    """
    Atualiza situacaoEntrega e/ou assinaturaCondutor de um CRR existente.

    PATCH /api/v1/mobile/crr/<crr_id>/atualizar-condutor/
    Header: X-API-Key: <api_key>
    {
        "situacaoEntrega": "Assinou e recebeu 2a via",
        "assinaturaCondutor": "<base64_png>"
    }

    Apenas o agente que criou o CRR pode atualiza-lo.
    """
    from .models import Crr

    matricula = request.headers.get('X-Matricula', '').strip()

    try:
        crr = Crr.objects.get(id=crr_id, matriculaAgente=matricula)
    except Crr.DoesNotExist:
        return Response(
            {'sucesso': False, 'erro': 'CRR nao encontrado'},
            status=status.HTTP_404_NOT_FOUND,
        )

    SITUACOES_VALIDAS = {
        'condutor ausente',
        'assinou e recebeu 2a via',
        'recusou assinar e recebeu 2a via',
        'recusou assinar e a receber 2a via',
    }

    situacao = request.data.get('situacaoEntrega', '').strip().lower()
    assinatura = request.data.get('assinaturaCondutor', '')

    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"[atualizar_condutor] crr_id={crr_id} situacao='{situacao}' assinatura_len={len(assinatura) if assinatura else 0}")

    if situacao and situacao not in SITUACOES_VALIDAS:
        return Response(
            {'sucesso': False, 'erro': 'Situacao de entrega invalida'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if situacao:
        crr.situacaoEntrega = situacao
        crr.save(update_fields=['situacaoEntrega'])

    condutor_atualizado = False
    if assinatura:
        condutor = crr.condutores.first()
        if condutor:
            condutor.assinaturaCondutor = assinatura
            condutor.save(update_fields=['assinaturaCondutor'])
            condutor_atualizado = True
            logger.warning(f"[atualizar_condutor] assinatura salva condutor_id={condutor.pk} ({len(assinatura)} chars)")
        else:
            logger.warning(f"[atualizar_condutor] CRR {crr_id} nao tem condutor cadastrado")

    return Response({'sucesso': True, 'mensagem': 'Condutor atualizado com sucesso', 'condutor_atualizado': condutor_atualizado})


@extend_schema(
    summary='Envia o CRR por email',
    parameters=[MOBILE_API_KEY_PARAMETER],
    request=inline_serializer(
        name='EnviarEmailCondutorRequest',
        fields={'email': serializers.EmailField()},
    ),
    responses=OpenApiTypes.OBJECT,
)
@api_view(['POST'])
@permission_classes([IsDispositivoMobile])
def enviar_email_condutor_view(request, crr_id):
    """
    Envia email do CRR para o condutor.

    POST /api/v1/mobile/crr/<crr_id>/enviar-email/
    Header: X-API-Key: <api_key>
    {
        "email": "condutor@email.com"
    }
    """
    from .models import Crr
    from .email_utils import enviar_email_condutor

    email_dest = request.data.get('email', '').strip()
    if not email_dest:
        return Response(
            {'sucesso': False, 'erro': 'Email não informado'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        crr = Crr.objects.prefetch_related(
            'veiculo', 'condutores', 'aits',
            'enquadramentos__enquadramento',
        ).get(id=crr_id)
    except Crr.DoesNotExist:
        return Response(
            {'sucesso': False, 'erro': 'CRR não encontrado'},
            status=status.HTTP_404_NOT_FOUND,
        )

    import threading

    def _enviar():
        enviar_email_condutor(crr, email_dest)

    threading.Thread(target=_enviar, daemon=True).start()
    return Response({'sucesso': True, 'mensagem': 'Email sendo enviado'})


# ==================== DADOS AUXILIARES ==================== #

@extend_schema(
    summary='Lista enquadramentos disponíveis',
    parameters=[MOBILE_API_KEY_PARAMETER],
    responses=TabelaEnquadramentoSerializer(many=True),
)
@api_view(['GET'])
@permission_classes([IsDispositivoMobile])
def listar_enquadramentos(request):
    """
    Lista todos os enquadramentos disponíveis.

    GET /api/v1/mobile/enquadramentos/
    Header: X-API-Key: <api_key>
    """
    enquadramentos = TabelaEnquadramento.objects.all().order_by('codigo')
    serializer = TabelaEnquadramentoSerializer(enquadramentos, many=True)

    return Response({
        'sucesso': True,
        'total': enquadramentos.count(),
        'enquadramentos': serializer.data
    })


@extend_schema(
    summary='Retorna o status do dispositivo',
    parameters=[MOBILE_API_KEY_PARAMETER],
    responses=OpenApiTypes.OBJECT,
)
@api_view(['GET'])
@permission_classes([IsDispositivoMobile])
def status_dispositivo(request):
    """
    Retorna status completo do dispositivo.

    GET /api/v1/mobile/status/
    Header: X-API-Key: <api_key>
    """
    dispositivo = request.dispositivo

    return Response({
        'sucesso': True,
        'dispositivo': {
            'id': dispositivo.id,
            'nome': dispositivo.nome,
            'device_id': dispositivo.device_id,
            'imei': dispositivo.device_id,
            'ativo': dispositivo.ativo,
            'ultimo_acesso': dispositivo.ultimo_acesso,
        },
    })


# ==================== VALIDAÇÃO DE LOGIN ==================== #

@extend_schema(
    summary='Valida login do app mobile',
    request=inline_serializer(
        name='ValidarLoginRequest',
        fields={
            'api_key': serializers.CharField(),
            'matricula': serializers.CharField(),
            'senha': serializers.CharField(),
        },
    ),
    responses=OpenApiTypes.OBJECT,
)
@api_view(['POST'])
@permission_classes([AllowAny])
def validar_login(request):
    """
    Valida login do app mobile: verifica api_key + matricula.
    Garante que o agente existe, esta ativo e corresponde ao dispositivo.

    POST /api/v1/mobile/validar-login/
    {
        "api_key": "abc123...",
        "matricula": "12345"
    }
    """
    api_key = request.data.get('api_key', '').strip()
    matricula = request.data.get('matricula', '').strip()
    senha = request.data.get('senha', '').strip()

    if not api_key or not matricula or not senha:
        return Response({
            'sucesso': False,
            'erro': 'API Key, matricula e senha sao obrigatorios'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Valida dispositivo
    try:
        dispositivo = DispositivoMobile.objects.get(
            api_key=api_key, ativo=True, ativado=True
        )
    except DispositivoMobile.DoesNotExist:
        return Response({
            'sucesso': False,
            'erro': 'Dispositivo nao encontrado ou desativado'
        }, status=status.HTTP_403_FORBIDDEN)

    # Valida que o agente esta ativo
    try:
        agente = Agente.objects.get(matricula=matricula, ativo=True)
    except Agente.DoesNotExist:
        return Response({
            'sucesso': False,
            'erro': 'Agente nao cadastrado ou desativado'
        }, status=status.HTTP_403_FORBIDDEN)

    # Valida senha do agente
    if not agente.check_senha(senha):
        return Response({
            'sucesso': False,
            'erro': 'Senha incorreta'
        }, status=status.HTTP_403_FORBIDDEN)

    # Atualiza ultimo acesso
    from django.utils import timezone
    dispositivo.ultimo_acesso = timezone.now()
    dispositivo.save(update_fields=['ultimo_acesso'])

    assinatura_url = agente.assinatura.url if agente.assinatura else None
    return Response({
        'sucesso': True,
        'agente': {
            'nome': agente.nome,
            'matricula': agente.matricula,
            'assinatura_url': assinatura_url,
        },
        'senha_alterada': agente.senha_alterada,
    })


# ==================== ALTERAÇÃO DE SENHA ==================== #

@extend_schema(
    summary='Altera a senha do agente',
    parameters=[MOBILE_API_KEY_PARAMETER],
    request=inline_serializer(
        name='AlterarSenhaRequest',
        fields={
            'matricula': serializers.CharField(),
            'nova_senha': serializers.CharField(),
        },
    ),
    responses=OpenApiTypes.OBJECT,
)
@api_view(['POST'])
@permission_classes([IsDispositivoMobile])
def alterar_senha(request):
    """
    Altera a senha do agente.

    POST /api/v1/mobile/alterar-senha/
    Header: X-API-Key: <api_key>
    { "matricula": "12345", "nova_senha": "novasenha" }
    """
    matricula = request.data.get('matricula', '').strip()
    nova_senha = request.data.get('nova_senha', '').strip()

    if not matricula or not nova_senha:
        return Response({
            'sucesso': False,
            'erro': 'Matricula e nova senha sao obrigatorios'
        }, status=status.HTTP_400_BAD_REQUEST)

    if len(nova_senha) < 4:
        return Response({
            'sucesso': False,
            'erro': 'Senha deve ter no minimo 4 caracteres'
        }, status=status.HTTP_400_BAD_REQUEST)

    if nova_senha == 'admin':
        return Response({
            'sucesso': False,
            'erro': 'A nova senha nao pode ser "admin"'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        agente = Agente.objects.get(
            matricula=matricula, ativo=True
        )
        agente.set_senha(nova_senha)
        agente.senha_alterada = True
        agente.save(update_fields=['senha', 'senha_alterada'])
        return Response({
            'sucesso': True,
            'mensagem': 'Senha alterada com sucesso'
        })
    except Agente.DoesNotExist:
        return Response({
            'sucesso': False,
            'erro': 'Agente nao encontrado'
        }, status=status.HTTP_404_NOT_FOUND)


# ==================== VERSÃO DO APP ==================== #

@extend_schema(summary='Retorna a versão atual do app mobile', responses=OpenApiTypes.OBJECT)
@api_view(['GET'])
@permission_classes([AllowAny])
def app_version(request):
    """
    Retorna informações da versão atual do app.
    Usado para verificar atualizações.

    GET /api/v1/mobile/app-version/
    """
    return Response({
        'versao': '1.0.0',
        'build': 1,
        'obrigatoria': False,
        'mensagem': 'Nova versão disponível!',
        'download_url': 'http://192.168.1.71:8000/static/app/divprom-mobile.apk',
        'novidades': [
            'Correções de bugs',
            'Melhorias de performance',
        ]
    })
