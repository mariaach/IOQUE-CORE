import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@ioque.local")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "Admin123*")

if User.objects.filter(username=username).exists():
    print("Superuser already exists.")
else:
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
    )
    print(f"Creating default superuser... {username}")
