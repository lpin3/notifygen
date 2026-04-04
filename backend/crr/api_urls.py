
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views  import (CrrViewSet,VeiculoViewSet,AitViewSet,CondutorViewSet,
                    TabelaEnquadramentoViewSet, EnquadramentoViewSet) 
from crr.api_ext_views import consulta_publica_crr, pagina_consulta_crr

router = DefaultRouter()
router.register(r'crr', CrrViewSet)
router.register(r'veiculo', VeiculoViewSet)
router.register(r'condutores', CondutorViewSet)
router.register(r'aits', AitViewSet)
router.register(r'tabelaenquadramento', TabelaEnquadramentoViewSet)
router.register(r'enquadramento', EnquadramentoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('consulta-publica/crr/', consulta_publica_crr, name='consulta_publica_crr'),
    path('consulta-publica/', pagina_consulta_crr, name='pagina_consulta_crr'),
]