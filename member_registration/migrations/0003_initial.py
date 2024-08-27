# Generated by Django 4.2.15 on 2024-08-26 19:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('member_registration', '0002_delete_memberpackage'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemberPackage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('validity_month', models.IntegerField()),
                ('accesses', models.JSONField(default=list)),
                ('facilities', models.JSONField(default=list)),
                ('price', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='MemberRegistration',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('expiry_date', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member', to=settings.AUTH_USER_MODEL, to_field='email')),
            ],
        ),
    ]
