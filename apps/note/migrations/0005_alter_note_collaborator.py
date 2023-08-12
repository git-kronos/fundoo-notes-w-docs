# Generated by Django 4.2.4 on 2023-08-12 15:47

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('note', '0004_note_collaborator_alter_note_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='collaborator',
            field=models.ManyToManyField(related_name='collab', to=settings.AUTH_USER_MODEL),
        ),
    ]
