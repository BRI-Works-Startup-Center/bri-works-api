# Generated by Django 4.2.15 on 2024-09-10 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0006_event_rate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventregistration',
            name='status',
            field=models.CharField(choices=[('PENDING', 'PENDING'), ('CANCELLED', 'CANCELLED'), ('REGISTERED', 'REGISTERED'), ('ATTENDED', 'ATTENDED')], default='PENDING'),
        ),
    ]
