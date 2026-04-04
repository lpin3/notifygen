from rest_framework.decorators import api_view, throttle_classes, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from .models import Crr, Veiculo
from .serializers import ConsultaExterna
from rest_framework.permissions import AllowAny
from django.shortcuts import render


@extend_schema(
    summary='Consulta pública de CRR',
    description='Consulta um CRR publicamente por placa, chassi ou número do CRR.',
    parameters=[
        OpenApiParameter('placa', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Placa do veículo'),
        OpenApiParameter('chassi', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Chassi do veículo'),
        OpenApiParameter('numeroCrr', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Número do CRR'),
    ],
    responses={200: ConsultaExterna},
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def consulta_publica_crr(request):
    """
    Consulta pública de CRR por placa, chassi ou número do CRR.
    - Status 'cancelado' não é exibido.
    - Todos os status exceto 'liberado' são retornados como 'retido'.
    """
    placa      = request.query_params.get('placa')
    chassi     = request.query_params.get('chassi')
    numero_crr = request.query_params.get('numeroCrr')

    if not placa and not chassi and not numero_crr:
        return Response(
            {"erro": "Informe a placa, o chassi ou o número do CRR para consulta."},
            status=status.HTTP_400_BAD_REQUEST
        )

    crr_instance = None

    if numero_crr:
        crr_instance = Crr.objects.filter(
            numeroCrr__iexact=numero_crr.strip()
        ).first()
        if not crr_instance:
            return Response(
                {"mensagem": "CRR não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        veiculo_qs = Veiculo.objects.select_related('crr')
        if placa:
            veiculo_qs = veiculo_qs.filter(placa__iexact=placa.strip())
        elif chassi:
            veiculo_qs = veiculo_qs.filter(chassi__iexact=chassi.strip())

        veiculo = veiculo_qs.first()
        if not veiculo:
            return Response(
                {"mensagem": "Veículo não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        if not veiculo.crr:
            return Response(
                {"mensagem": "CRR não encontrado para este veículo."},
                status=status.HTTP_404_NOT_FOUND
            )
        crr_instance = veiculo.crr

    # CRR cancelado não é exibido publicamente
    if crr_instance.status == 'cancelado':
        return Response(
            {"mensagem": "Veículo não encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = ConsultaExterna(crr_instance)
    data = dict(serializer.data)

    # Mapeamento de status para o público:
    # 'pendente' e 'retido' → 'retido'
    # 'liberado' → 'liberado'
    # 'leiloado' → 'leiloado'
    # 'cancelado' já foi bloqueado acima (404)
    status_map = {'liberado': 'liberado', 'leiloado': 'leiloado'}
    data['status'] = status_map.get(crr_instance.status, 'retido')

    return Response(data, status=status.HTTP_200_OK)


def pagina_consulta_crr(request):
    return render(request, 'crr/consulta_crr_api.html')
