# Generated by Django 5.0.1 on 2024-07-01 18:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='store',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=100)),
                ('cash_value', models.IntegerField(default=0)),
                ('activeFlag', models.CharField(default='Y', max_length=1)),
                ('store_manager_emp_id', models.CharField(max_length=50, null=True)),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='store_emp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('addr', models.CharField(max_length=80)),
                ('activeFlag', models.CharField(default='Y', max_length=1)),
                ('role', models.CharField(choices=[('store_manager', 'store_manager'), ('store_staff', 'store_staff')], default='piece', max_length=50)),
                ('emp_obj', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('store_obj', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stores_app.store')),
            ],
        ),
    ]
