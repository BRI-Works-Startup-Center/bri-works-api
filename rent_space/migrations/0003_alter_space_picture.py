# Generated by Django 4.2.15 on 2024-08-19 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rent_space', '0002_space_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='space',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='space/'),
        ),
    ]
