from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils import timezone


class IsJavaUser(BasePermission):
    """
    Permite apenas ao usuário 'java' fazer GET e POST.
    Bloqueia PUT, PATCH, DELETE.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Permite apenas ao usuário 'java'
        if user.username != 'java':
            return False

        # Permite apenas GET (leitura) e PATCH (atualização parcial de status)
        if request.method in SAFE_METHODS or request.method == 'PATCH':
            return True

        return False


class IsDispositivoMobile(BasePermission):
    """
    Autenticação via API Key para dispositivos mobile.
    Header: X-API-Key: <api_key>
    """

    def has_permission(self, request, view):
        from .models import DispositivoMobile

        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return False

        try:
            dispositivo = DispositivoMobile.objects.get(
                api_key=api_key,
                ativo=True
            )
            # Atualiza último acesso
            dispositivo.ultimo_acesso = timezone.now()
            dispositivo.save(update_fields=['ultimo_acesso'])

            # Anexa dispositivo ao request para uso nas views
            request.dispositivo = dispositivo
            return True

        except DispositivoMobile.DoesNotExist:
            return False
