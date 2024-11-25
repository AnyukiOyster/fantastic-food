from telebot import types

def tel_button():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Отправить номер 📞', request_contact=True)
    kb.add(item1)
    return kb

def location_button():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    loc = types.KeyboardButton('Отправить местоположение 📍', request_location=True)
    kb.add(loc)
    return kb

#Кнопки для меню заказа
def main_menu(products):
    kb = types.InlineKeyboardMarkup(row_width=2)
    cart = types.InlineKeyboardButton(text='Корзина 🛒', callback_data='cart')
    all_products = [types.InlineKeyboardButton(text=f'{i[1]}', callback_data=i[0]) for i in products]
    kb.add(*all_products)
    kb.row(cart)
    return kb

#Кнопки выбора количества товара
def choose_amount(pr_amount, plus_or_minus='', amount=1):
    kb = types.InlineKeyboardMarkup(row_width=3)
    minus = types.InlineKeyboardButton(text='-', callback_data='decrement')
    count = types.InlineKeyboardButton(text=str(amount), callback_data=str(amount))
    plus = types.InlineKeyboardButton(text='+', callback_data='increment')
    to_cart = types.InlineKeyboardButton(text='Добавить в корзину 🛒', callback_data='to_cart')
    back = types.InlineKeyboardButton(text='Назад ⬅️', callback_data='back')
    #Алгоритм изменения количества
    if plus_or_minus == 'increment':
        if amount <= pr_amount:
            count = types.InlineKeyboardButton(text=str(amount + 1), callback_data=str(amount + 1))
    elif plus_or_minus == 'decrement':
        if amount > 1:
            count = types.InlineKeyboardButton(text=str(amount - 1), callback_data=str(amount - 1))
    kb.add(minus, count, plus)
    kb.row(back, to_cart)
    return kb

#Кнопки корзины
def cart_buttons():
    kb = types.InlineKeyboardMarkup(row_width=2)
    order = types.InlineKeyboardButton(text='Оформить заказ!', callback_data='order')
    clear = types.InlineKeyboardButton(text='Очистить корзину', callback_data='clear')
    back = types.InlineKeyboardButton(text='Назад ⬅️', callback_data='back')
    kb.add(order, clear)
    kb.row(back)
    return kb

## Кнопки админ-панели ##
# Админ меню
def admin_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    admin1 = types.KeyboardButton('Добавить продукт')
    admin2 = types.KeyboardButton('Удалить продукт')
    admin3 = types.KeyboardButton('Изменить продукт')
    admin4 = types.KeyboardButton('Перейти в галвное меню')
    kb.add(admin1, admin2, admin3)
    kb.row(admin4)
    return kb