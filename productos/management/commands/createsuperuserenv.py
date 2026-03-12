import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Crea un superuser desde variables de entorno'

    def handle(self, *args, **options):
        username = os.environ.get('ADMIN_USERNAME')
        email = os.environ.get('ADMIN_EMAIL')
        password = os.environ.get('ADMIN_PASSWORD')

        if not all([username, email, password]):
            self.stdout.write(
                self.style.ERROR(
                    'Error: Debes establecer ADMIN_USERNAME, ADMIN_EMAIL y ADMIN_PASSWORD'
                )
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'El superuser "{username}" ya existe')
            )
            return

        User.objects.create_superuser(username, email, password)
        self.stdout.write(
            self.style.SUCCESS(f'Superuser "{username}" creado exitosamente')
        )
