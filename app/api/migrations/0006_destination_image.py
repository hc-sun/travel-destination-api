# Generated by Django 3.2.23 on 2023-11-20 06:10

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20231116_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='destination',
            name='image',
            field=models.ImageField(null=True, upload_to=api.models.destination_image_file_path),
        ),
    ]
