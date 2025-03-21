# Сервис для формирования смет из JSON

## Описание
Сервис, который принимает JSON с данными для формирования смет и создает страницу с визуальным представлением.

Адрес сервиса: [offer.okonti.ru](https://offer.okonti.ru)
Пример сформированой сметы: [Пример сметы](https://offer.okonti.ru/smeta/b9d52a57-41fd-42ff-a876-51907da20f46/)

## Внесенные изменения

### 1. Прием и сохранение исходного JSON
- Добавлена модель `RawJSON` для хранения оригинального JSON
- Изменен процесс обработки JSON с сохранением исходных данных
- Улучшена обработка ошибок при создании смет

### 2. Система скриптов для страницы
- Добавлена модель `ScriptCode` для хранения и управления скриптами
- Возможность добавлять скрипты в различные части страницы (начало/конец head, начало/конец body)
- Сохранена обратная совместимость со старыми кодами метрик и чатов

### 3. Система логирования
- Улучшена система логирования действий пользователей
- Добавлены настройки времени хранения логов (модель `LogSettings`)
- Расширены возможности просмотра и экспорта логов

### 4. Шаблоны смет в админке
- Добавлена модель `TemplateSettings` для хранения и редактирования HTML/CSS шаблонов смет
- Добавлена поддержка пользовательских шаблонов с передачей всех данных заказа

### 5. Система вебхуков
- Добавлена модель `WebhookSettings` для настройки URL вебхуков
- Настроена отправка данных о созданных сметах через вебхуки

### 6. Разделение настроек для разработки
- Добавлен файл `settings_local.py` для локальной разработки
- Созданы скрипты для запуска в локальном режиме без влияния на продакшн

## Инструкция по локальной разработке

### Установка и запуск

1. Клонировать репозиторий
```bash
git clone <repository-url>
```

2. Создать виртуальное окружение и активировать его
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установить зависимости
```bash
cd ok-main/backend
pip install -r requirements.txt
```

4. Создать миграции и применить их
```bash
python run_migrations.py  # Создаст миграции
python run_migrations.py migrate  # Применит миграции
```

5. Запустить сервер разработки
```bash
python run_local.py
```

Сервер будет доступен по адресу: http://127.0.0.1:8000/

### Админ-панель

Для входа в админ-панель создайте суперпользователя:
```bash
python run_local.py createsuperuser
```

После этого вы сможете войти в админ-панель по адресу: http://127.0.0.1:8000/admin/

## Структура проекта

```
ok-main/
├── backend/                 # Основная директория проекта Django
│   ├── backend/             # Настройки проекта
│   │   ├── settings.py      # Основные настройки
│   │   ├── settings_local.py # Локальные настройки (не влияют на прод)
│   │   └── ...
│   ├── smeta/               # Приложение для работы со сметами
│   │   ├── models.py        # Модели данных
│   │   ├── views.py         # Представления
│   │   ├── admin.py         # Настройки админки
│   │   └── ...
│   ├── templates/           # Шаблоны страниц
│   │   ├── order_detail.html # Шаблон сметы
│   │   └── custom_template.html # Шаблон для пользовательских шаблонов
│   ├── run_local.py         # Скрипт для локального запуска
│   └── run_migrations.py    # Скрипт для миграций
└── ...
```

## Основные модели

* `Order` - Основная модель для хранения данных сметы/заказа
* `RawJSON` - Хранение оригинального JSON для сметы
* `ScriptCode` - Настройки скриптов для страниц
* `WebhookSettings` - Настройки вебхуков
* `TemplateSettings` - Пользовательские шаблоны смет
* `LogSettings` - Настройки хранения логов

## Примечания

* При обновлении проекта в продакшн среде, убедитесь, что выполнены миграции базы данных
* Локальные настройки не влияют на продакшн среду
* Для применения изменений в шаблонах может потребоваться перезапуск сервера 