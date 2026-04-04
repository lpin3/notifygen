# api_mobile_urls.py
"""
URLs da API para aplicativo mobile.
Prefixo: /api/v1/mobile/
"""
from django.urls import path
from . import api_mobile_views

urlpatterns = [
    # Ativacao, Registro e Login (sem autenticação)
    path('ativar/', api_mobile_views.ativar_dispositivo, name='mobile_ativar'),
    path('registrar/', api_mobile_views.registrar_dispositivo, name='mobile_registrar'),
    path('login/', api_mobile_views.login_dispositivo, name='mobile_login'),
    path('validar-login/', api_mobile_views.validar_login, name='mobile_validar_login'),
    path('alterar-senha/', api_mobile_views.alterar_senha, name='mobile_alterar_senha'),

    # Numeracao CRR (requer API Key)
    path('crr/proximo-numero/', api_mobile_views.obter_proximo_numero, name='mobile_proximo'),

    # CRR (requer API Key)
    path('crr/', api_mobile_views.listar_crrs, name='mobile_crr_listar'),
    path('crr/buscar/', api_mobile_views.buscar_crrs, name='mobile_crr_buscar'),
    path('crr/criar/', api_mobile_views.criar_crr, name='mobile_crr_criar'),
    path('crr/<int:crr_id>/atualizar-condutor/', api_mobile_views.atualizar_condutor_crr, name='mobile_crr_atualizar_condutor'),
    path('crr/<int:crr_id>/enviar-email/', api_mobile_views.enviar_email_condutor_view, name='mobile_crr_enviar_email'),

    # Dados Auxiliares (requer API Key)
    path('enquadramentos/', api_mobile_views.listar_enquadramentos, name='mobile_enquadramentos'),
    path('status/', api_mobile_views.status_dispositivo, name='mobile_status'),

    # Versão do App (sem autenticação)
    path('app-version/', api_mobile_views.app_version, name='mobile_app_version'),
]
