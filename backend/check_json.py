import sqlite3
import json

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Получаем JSON для каждого заказа
cursor.execute('SELECT o.number, r.data FROM smeta_order o JOIN smeta_rawjson r ON o.id = r.order_id')
results = cursor.fetchall()

for number, data in results:
    print(f'JSON для заказа {number}:')
    # Преобразуем JSON и показываем первые 200 символов
    json_data = json.loads(data)
    formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
    print(formatted_json[:500] + '...' if len(formatted_json) > 500 else formatted_json)
    print('-' * 80)

conn.close() 