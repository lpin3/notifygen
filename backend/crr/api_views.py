from rest_framework import viewsets, mixins, status as drf_status
from rest_framework.response import Response
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view

from .models import Crr, Veiculo, Condutor, TabelaEnquadramento, Ait, Enquadramento
from .serializers import (
    CrrJavaSerializer,
    CrrJavaDetalheSerializer,
    CrrStatusUpdateSerializer,
    VeiculoSerializer,
    AitSerializer,
    CondutorSerializer,
    TabelaEnquadramentoSerializer,
    EnquadramentoSerializer,
)
from .permissions import IsJavaUser


@extend_schema_view(
    list=extend_schema(
        summary='Lista CRRs',
        description='Lista CRRs com filtros opcionais por número, placa, chassi, marca, modelo e status.',
        parameters=[
            OpenApiParameter('numeroCrr', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Número do CRR'),
            OpenApiParameter('placa', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Placa do veículo'),
            OpenApiParameter('chassi', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Chassi do veículo'),
            OpenApiParameter('marca', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Marca do veículo'),
            OpenApiParameter('modelo', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Modelo do veículo'),
            OpenApiParameter('status', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Status do CRR'),
        ],
    ),
    retrieve=extend_schema(summary='Detalha um CRR'),
    partial_update=extend_schema(
        summary='Libera um CRR',
        description="Atualiza o status do CRR. Apenas o valor 'liberado' é aceito.",
    ),
)
class CrrViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Crr.objects.all().order_by('-criado_em')
    permission_classes = [IsJavaUser]
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_queryset(self):
        qs = (
            Crr.objects.all()
            .prefetch_related(
                'veiculo',
                'condutores',
                'aits',
                'enquadramentos__enquadramento',
                'arrendatarios__arrendatario',
                'imagens',
            )
            .order_by('-criado_em')
        )

        params = self.request.query_params
        numero = params.get('numeroCrr')
        placa = params.get('placa')
        chassi = params.get('chassi')
        marca = params.get('marca')
        modelo = params.get('modelo')
        status_param = params.get('status')

        if numero:
            qs = qs.filter(numeroCrr__iexact=numero.strip())
        if placa:
            qs = qs.filter(veiculo__placa__iexact=placa.strip())
        if chassi:
            qs = qs.filter(veiculo__chassi__iexact=chassi.strip())
        if marca:
            qs = qs.filter(veiculo__marca__icontains=marca.strip())
        if modelo:
            qs = qs.filter(veiculo__modelo__icontains=modelo.strip())
        if status_param:
            qs = qs.filter(status__iexact=status_param.strip())

        return qs.distinct()

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return CrrStatusUpdateSerializer
        if self.action == 'retrieve':
            return CrrJavaDetalheSerializer
        return CrrJavaSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'mensagem': f"CRR {instance.numeroCrr} atualizado para 'liberado'."},
            status=drf_status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        if not kwargs.get('partial'):
            return Response(
                {'erro': 'Metodo nao permitido. Use PATCH para atualizar o status.'},
                status=drf_status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().update(request, *args, **kwargs)


class VeiculoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Veiculo.objects.all()
    serializer_class = VeiculoSerializer
    permission_classes = [IsJavaUser]


class AitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ait.objects.all()
    serializer_class = AitSerializer
    permission_classes = [IsJavaUser]


class CondutorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Condutor.objects.all()
    serializer_class = CondutorSerializer
    permission_classes = [IsJavaUser]


class TabelaEnquadramentoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TabelaEnquadramento.objects.all()
    serializer_class = TabelaEnquadramentoSerializer
    permission_classes = [IsJavaUser]


class EnquadramentoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Enquadramento.objects.all()
    serializer_class = EnquadramentoSerializer
    permission_classes = [IsJavaUser]
