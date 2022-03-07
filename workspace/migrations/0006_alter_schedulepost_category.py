# Generated by Django 4.0.2 on 2022-02-26 07:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workspace', '0005_dayname_schedulepost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedulepost',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='workspace.category'),
        ),
    ]