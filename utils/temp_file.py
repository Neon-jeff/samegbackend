import os

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pathlib import Path

base_dir=Path(__file__).parents[1]


def create_temp_path(file):
    path=default_storage.save(f'uploads/{file.name}',ContentFile(file.read()))
    return {
        "path":f'{base_dir}/media/{path}',
        "name":file.name
    }

