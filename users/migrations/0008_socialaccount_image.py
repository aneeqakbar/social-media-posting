# Generated by Django 4.0.2 on 2022-02-25 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_socialaccount_unique_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialaccount',
            name='image',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
