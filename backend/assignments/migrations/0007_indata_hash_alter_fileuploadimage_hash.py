# Generated by Django 4.1.7 on 2023-09-13 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0006_indata_alter_fileuploadimage_hash'),
    ]

    operations = [
        migrations.AddField(
            model_name='indata',
            name='hash',
            field=models.CharField(blank=True, default='63468', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='fileuploadimage',
            name='hash',
            field=models.CharField(default='PT0M6', max_length=255, verbose_name='hash'),
        ),
    ]
