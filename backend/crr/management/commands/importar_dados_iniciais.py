import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from crr.models import TabelaEnquadramento


class Command(BaseCommand):
    help = 'Importa dados iniciais (idempotente — só executa se não houver dados)'

    def handle(self, *args, **options):
        if TabelaEnquadramento.objects.exists():
            self.stdout.write(self.style.SUCCESS(
                'Dados já existem — importação ignorada.'
            ))
            return

        fixture = os.path.join(
            os.path.dirname(__file__), '..', '..', 'fixtures', 'dados_iniciais.json'
        )
        self.stdout.write('Importando dados iniciais...')
        call_command('loaddata', fixture, verbosity=1)
        self.stdout.write(self.style.SUCCESS('Dados importados com sucesso.'))
