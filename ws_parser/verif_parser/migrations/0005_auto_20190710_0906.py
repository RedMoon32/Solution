# Generated by Django 2.2.3 on 2019-07-10 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('verif_parser', '0004_auto_20190710_0838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='siren',
            field=models.CharField(max_length=100),
        ),
    ]