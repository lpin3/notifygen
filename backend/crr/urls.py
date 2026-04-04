from django.urls import path
from . import views

app_name = 'crr'

urlpatterns = [
    # CRR
    path('', views.CrrListView.as_view(), name='crr_list'),
    path('novo/', views.CrrCreateView.as_view(), name='crr_create'),
    path('<int:pk>/', views.CrrDetailView.as_view(), name='crr_detail'),
    path('<int:pk>/modal/', views.crr_detail_modal, name='crr_detail_modal'),
    path('<int:pk>/editar/', views.CrrUpdateView.as_view(), name='crr_update'),
    path('<int:pk>/excluir/', views.CrrDeleteView.as_view(), name='crr_delete'),
    path('<int:pk>/reenviar-email/', views.reenviar_email_crr, name='reenviar_email_crr'),

    # Dispositivos Mobile
    path('dispositivos/', views.dispositivo_list, name='dispositivo_list'),
    path('dispositivos/novo/', views.dispositivo_create, name='dispositivo_create'),
    path('dispositivos/<int:pk>/editar/', views.dispositivo_edit, name='dispositivo_edit'),
    path('dispositivos/<int:pk>/excluir/', views.dispositivo_delete, name='dispositivo_delete'),

    # Edital
    path('gerar-edital/', views.crr_gerar_edital, name='crr_gerar_edital'),
    path('editais/', views.edital_list, name='edital_list'),

    # Triagem
    path('triagem/', views.TriagemListView.as_view(), name='triagem_list'),
    path('triagem/<int:pk>/', views.TriagemDetailView.as_view(), name='triagem_detail'),
    path('triagem/<int:pk>/modal/', views.triagem_detail_modal, name='triagem_detail_modal'),
    path('triagem/<int:pk>/editar/', views.TriagemUpdateView.as_view(), name='triagem_update'),
    path('triagem/<int:pk>/status/<str:novo_status>/', views.triagem_status, name='triagem_status'),

    # Arrendatários
    path('arrendatarios/', views.arrendatario_list, name='arrendatario_list'),
    path('arrendatarios/novo/', views.arrendatario_create, name='arrendatario_create'),
    path('arrendatarios/<int:pk>/editar/', views.arrendatario_edit, name='arrendatario_edit'),
    path('arrendatarios/<int:pk>/excluir/', views.arrendatario_delete, name='arrendatario_delete'),

    # Enquadramentos
    path('enquadramentos/', views.enquadramento_list, name='enquadramento_list'),
    path('enquadramentos/novo/', views.enquadramento_create, name='enquadramento_create'),
    path('enquadramentos/<int:pk>/editar/', views.enquadramento_edit, name='enquadramento_edit'),
    path('enquadramentos/<int:pk>/excluir/', views.enquadramento_delete, name='enquadramento_delete'),

    # Agentes (superuser)
    path('agentes/', views.agente_list, name='agente_list'),
    path('agentes/novo/', views.agente_create, name='agente_create'),
    path('agentes/<int:pk>/editar/', views.agente_edit, name='agente_edit'),
    path('agentes/<int:pk>/excluir/', views.agente_delete, name='agente_delete'),

    # Minha Senha
    path('minha-senha/', views.MinhaSenhaView.as_view(), name='minha_senha'),

    # Logs do sistema (superuser)
    path('logs/', views.log_list, name='log_list'),

    # Usuários (superuser)
    path('usuarios/', views.usuario_list, name='usuario_list'),
    path('usuarios/novo/', views.usuario_create, name='usuario_create'),
    path('usuarios/<int:pk>/editar/', views.usuario_edit, name='usuario_edit'),
    path('usuarios/<int:pk>/excluir/', views.usuario_delete, name='usuario_delete'),

    # Grupos (superuser)
    path('grupos/', views.grupo_list, name='grupo_list'),
    path('grupos/novo/', views.grupo_create, name='grupo_create'),
    path('grupos/<int:pk>/editar/', views.grupo_edit, name='grupo_edit'),
    path('grupos/<int:pk>/excluir/', views.grupo_delete, name='grupo_delete'),
]
