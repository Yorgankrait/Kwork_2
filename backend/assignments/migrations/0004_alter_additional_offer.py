# Generated by Django 4.1.7 on 2023-06-13 13:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0003_alter_izd_offer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additional',
            name='offer',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='additionals', to='assignments.offer'),
            preserve_default=False,
        ),
    ]
