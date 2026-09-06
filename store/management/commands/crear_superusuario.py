import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = (
        "Crea un superusuario automáticamente usando variables de entorno, si no existe"
    )

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username or not password:
            self.stdout.write(
                "Variables DJANGO_SUPERUSER_USERNAME/PASSWORD no configuradas, se omite."
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                f'El superusuario "{username}" ya existe, no se crea de nuevo.'
            )
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(
            self.style.SUCCESS(f'Superusuario "{username}" creado correctamente.')
        )
