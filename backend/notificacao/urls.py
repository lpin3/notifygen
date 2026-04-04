from django.urls import path
from . import views

app_name = 'notificacao'

urlpatterns = [
    path('', views.notificacao_list, name='notificacao_list'),
    path('nova/', views.notificacao_create, name='notificacao_create'),
    path('<int:pk>/pdf/', views.notificacao_pdf, name='notificacao_pdf'),
    path('<int:pk>/excluir/', views.notificacao_delete, name='notificacao_delete'),
]
