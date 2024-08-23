# Generated by Django 5.0.1 on 2024-07-28 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores_app', '0003_alter_store_emp_store_obj'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='store',
            name='store_manager_username',
        ),
        migrations.AlterField(
            model_name='store_emp',
            name='role',
            field=models.CharField(choices=[('store_manager', 'store_manager'), ('store_staff', 'store_staff')], default='store_staff', max_length=50),
        ),
    ]
