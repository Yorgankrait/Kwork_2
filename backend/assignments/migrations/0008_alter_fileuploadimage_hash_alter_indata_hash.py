# Generated by Django 4.1.7 on 2024-10-14 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0007_indata_hash_alter_fileuploadimage_hash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileuploadimage',
            name='hash',
            field=models.CharField(default='17HBM', max_length=255, verbose_name='hash'),
        ),
        migrations.AlterField(
            model_name='indata',
            name='hash',
            field=models.CharField(blank=True, default='8HT32', max_length=255, null=True),
        ),
    ]
