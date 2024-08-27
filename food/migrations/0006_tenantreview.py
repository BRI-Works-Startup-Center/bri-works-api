# Generated by Django 4.2.15 on 2024-08-27 18:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('food', '0005_order_total_price_alter_order_status_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TenantReview',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('star', models.IntegerField()),
                ('comment', models.TextField()),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tenant_reviews', to='food.tenant')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tenant_reviewer', to=settings.AUTH_USER_MODEL, to_field='email')),
            ],
        ),
    ]
