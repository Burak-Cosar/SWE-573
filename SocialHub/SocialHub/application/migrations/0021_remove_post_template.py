# Generated by Django 4.2.11 on 2024-05-18 09:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0020_remove_templatefield_community'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='template',
        ),
    ]
