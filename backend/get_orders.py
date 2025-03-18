import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Получаем информацию о заказах и их UUID
cursor.execute('SELECT id, uuid, number FROM smeta_order')
orders = cursor.fetchall()

for order_id, order_uuid, number in orders:
    # Форматируем UUID с дефисами для URL
    formatted_uuid = f"{order_uuid[:8]}-{order_uuid[8:12]}-{order_uuid[12:16]}-{order_uuid[16:20]}-{order_uuid[20:]}" if order_uuid else "MISSING_UUID"
    
    print(f'Заказ {number}: http://127.0.0.1:8000/smeta/{formatted_uuid}/')

conn.close() 