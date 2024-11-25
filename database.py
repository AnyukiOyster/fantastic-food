import sqlite3

con = sqlite3.connect('delivery.db', check_same_thread=False)
sql = con.cursor()
#таблица со списком клиентов
sql.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER, name TEXT, tel TEXT UNIQUE);')
#таблица с доступными позициями
sql.execute('CREATE TABLE IF NOT EXISTS products(pr_id INTEGER PRIMARY KEY AUTOINCREMENT, pr_name TEXT, pr_desc TEXT, pr_price REAL, '
            'pr_count INTEGER, pr_photo TEXT);')
#корзина пользователя
sql.execute('CREATE TABLE IF NOT EXISTS cart(user_id INTEGER, ordered_product TEXT, pr_amount INTEGER);')

##Методы для пользователей##
def register(tg_id, name, num): #Регистрация пользователя
    sql.execute('INSERT INTO users VALUES (?, ?, ?);', (tg_id, name, num))
    con.commit() #Фиксация изменений в БД

def check_user(tg_id): #Проверка, есть ли пользователь в базе данных
    if sql.execute("SELECT * FROM users WHERE id=?", (tg_id,)).fetchone():
        return True
    else:
        return False

def get_name(tg_id):
    name = sql.execute("SELECT name FROM users WHERE id=?", (tg_id,)).fetchone()[0]
    return name

## Методы для продуктов (Клиентская сторона)
#Вывод всех товаров
def get_all_product():
    return sql.execute('SELECT * FROM products;').fetchall()
#Вывод товаров для кнопок
def get_product_buttons():
    all_products = sql.execute('SELECT pr_id, pr_name, pr_count FROM products;').fetchall()
    in_stock = [n for n in all_products if n[2] > 0]
    return in_stock

#Вывод конкретного товара
def get_certain_prod(pr_id):
    return sql.execute('SELECT * FROM products WHERE pr_id=?;', (pr_id,)).fetchone()

#Вывод цены конкретного товара
def get_exact_price(pr_name):
    return sql.execute('SELECT pr_price FROM products WHERE pr_name=?;', (pr_name,)).fetchone()

## Методы для корзины
#Добавить продукты в корзину
def add_to_cart(user_id, ordered_product, pr_amount):
    sql.execute('INSERT INTO cart VALUES (?, ?, ?);', (user_id, ordered_product, pr_amount))
    con.commit() #Фиксируем изменения

#Очистка корзины
def clear_cart(user_id):
    sql.execute('DELETE FROM cart WHERE user_id=?;', (user_id,))
    con.commit()  # Фиксируем изменения

#Вывод корзины
def show_cart(user_id):
    return sql.execute('SELECT * FROM cart WHERE user_id=?;', (user_id,)).fetchall()

#Оформление заказа
def order_cart(user_id):
    #1. Названия всех товаров из корзины и их кол-во
    product_names = sql.execute('SELECT ordered_product FROM cart WHERE user_id=?;', (user_id,)).fetchall()
    product_amount = sql.execute('SELECT pr_amount FROM cart WHERE user_id=?;', (user_id,)).fetchall()
    #2. Кол-во продуктов со склада
    stock_amount = [sql.execute('SELECT pr_count FROM products WHERE pr_name=?', (i[0],)).fetchone()[0]
                    for i in product_names]
    #3. Расчёт остатка на складе после покупки
    stock_total = []
    for e in product_amount: #количество заказанных пользователем позиций
        for c in stock_amount: #общее количество на складе
            stock_total.append(c - e[0])
    for t in stock_total: #изменённое количество товара на складе
        for n in product_names: #название товара
            sql.execute('UPDATE products SET pr_count=? WHERE pr_name=?;', (t, n[0]))
    con.commit()
    return stock_amount, stock_total

## Администраторская сторона ##
# Добавление товара в БД
def pr_to_db(pr_name, pr_desc, pr_price, pr_count, pr_photo):
    if (pr_name,) in sql.execute('SELECT pr_name FROM products;').fetchall():
        return False
    else:
        sql.execute('INSERT INTO products (pr_name, pr_desc, pr_price, pr_count, pr_photo) VALUES (?, ?, ?, ?, ?);',
                    (pr_name, pr_desc, pr_price, pr_count, pr_photo))
        con.commit()

#Удаление товара из БД
def del_prod(pr_name):
    sql.execute('DELETE FROM products WHERE pr_name=?;', (pr_name,))
    con.commit()

#Изменение атрибутов товара в БД
def change_att(keyword, new_value, att=''):
    if att == 'name':
        sql.execute('UPDATE products SET pr_name=? WHERE pr_name=?;', (new_value, keyword))
    elif att == 'desc':
        sql.execute('UPDATE products SET pr_desc=? WHERE pr_name=?;', (new_value, keyword))
    elif att == 'price':
        sql.execute('UPDATE products SET pr_price=? WHERE pr_name=?;', (new_value, keyword))
    elif att == 'count':
        sql.execute('UPDATE products SET pr_count=? WHERE pr_name=?;', (new_value, keyword))
    elif att == 'photo':
        sql.execute('UPDATE products SET pr_photo=? WHERE pr_name=?;', (new_value, keyword))
    con.commit()

#Проверка наличия товара в БД
def check_pr():
    if sql.execute('SELECT * FROM products;').fetchall():
        return True
    else:
        return False