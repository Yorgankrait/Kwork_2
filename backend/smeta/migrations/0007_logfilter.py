# Generated by Django 4.2.13 on 2025-03-17 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smeta', '0006_logsettings_scriptcode_templatesettings_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogFilter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название фильтра')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('keywords', models.TextField(blank=True, verbose_name='Ключевые слова (по одному на строку)')),
                ('log_level', models.CharField(choices=[('ALL', 'Все уровни'), ('INFO', 'Информация'), ('WARNING', 'Предупреждения'), ('ERROR', 'Ошибки'), ('DEBUG', 'Отладка')], default='ALL', max_length=20, verbose_name='Уровень логов')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
            ],
            options={
                'verbose_name': 'Фильтр логов',
                'verbose_name_plural': 'Фильтры логов',
            },
        ),
    ]
