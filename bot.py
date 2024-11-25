import telebot
import buttons, database

bot = telebot.TeleBot('7505843520:AAFcGVAYi8IWdEPsis7tVUWKToTA20')
# Хранилище временных данных
user_cart = {}
admins = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if database.check_user(user_id):
        user_name = database.get_name(user_id)
        bot.send_message(user_id, f'{user_name}, с возвращением!', reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.send_message(user_id, 'Чем хотите побаловать себя сегодня?', reply_markup=buttons.main_menu(database.get_product_buttons()))
    else:
        bot.send_message(user_id, f'Приветствуем!\nЧтобы продолжить, введите своё имя.',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_id = message.from_user.id
    user_name = message.text
    bot.send_message(user_id, f'{user_name}, приятно познакомиться! 😊\n'
                              f'Отправьте нам свой номер телефона, чтобы мы могли связаться с вами.', reply_markup=buttons.tel_button())
    bot.register_next_step_handler(message, get_tel, user_name)

#Выбор кол-ва товаров - эту функцию отнесли выше, чтобы не возник конфликт с функцией, где лямбда обрабатывала только целые числа
@bot.callback_query_handler(lambda call: call.data in ['increment', 'decrement', 'to_cart', 'back'])
def choose_count(call):
    user_id = call.message.chat.id
    if call.data == 'increment':
        bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id,
                                      reply_markup=buttons.choose_amount(database.get_certain_prod(user_cart[user_id]['pr_name'])[4],
                                                                         'increment', user_cart[user_id]['pr_count']))
        user_cart[user_id]['pr_count'] += 1
    elif call.data == 'decrement':
        bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id,
                                      reply_markup=buttons.choose_amount(database.get_certain_prod(user_cart[user_id]['pr_name'])[4],
                                                                         'decrement', user_cart[user_id]['pr_count']))
        user_cart[user_id]['pr_count'] -= 1
    elif call.data == 'to_cart':
        pr_name = database.get_certain_prod(user_cart[user_id]['pr_name'])[1]
        database.add_to_cart(user_id, pr_name, user_cart[user_id]['pr_count'])
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        bot.send_message(user_id, 'Товар добавлен в корзину! Хотите заказать что-нибудь ещё?',
                         reply_markup=buttons.main_menu(database.get_product_buttons()))
    elif call.data == 'back':
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        bot.send_message(user_id, 'Вы вернулись в меню. Что бы вы хотели заказать?',
                         reply_markup=buttons.main_menu(database.get_product_buttons()))

#Работа с корзиной со стороны клиента
@bot.callback_query_handler(lambda call: call.data in ['order', 'clear', 'cart'])
def cart_handler(call):
    user_id = call.message.chat.id
    text = 'Ваша корзина: \n\n'
    if call.data == 'cart':
        current_cart = database.show_cart(user_id)
        total = 0.0
        for i in current_cart:
            text += (f'Товар: {i[1]}\n'
                     f'Количество: {i[2]}\n')
            total += database.get_exact_price(i[1])[0] * i[2]
        total = "{:.2f}".format(total)
        text += f'Итоговая стоимость: {total} сум'
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        bot.send_message(user_id, text, reply_markup=buttons.cart_buttons())
    elif call.data == 'clear':
        database.clear_cart(user_id)
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        bot.send_message(user_id, 'Корзина очищена!', reply_markup=buttons.main_menu(database.get_product_buttons()))
    elif call.data == 'order':
        text = text.replace('Ваша корзина: ', "Новый заказ!")
        current_cart = database.show_cart(user_id)
        total = 0.0
        for i in current_cart:
            text += (f'Товар: {i[1]}\n'
                     f'Количество: {i[2]}\n')
            total += database.get_exact_price(i[1])[0] * i[2]
        total = "{:.2f}".format(total)
        text += f'Итоговая стоимость: {total} сум'
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        bot.send_message(user_id, "Отправьте адрес, куда нужно доставить заказ, с помощью кнопки",
                         reply_markup=buttons.location_button())
        bot.register_next_step_handler(call.message, get_loc, text)

def get_loc(message, text):
    user_id = message.from_user.id
    if message.location:
        user_name = database.get_name(user_id)
        text += f'\nКлиент: {user_name}'
        bot.send_message(280453694, text)
        bot.send_location(280453694, latitude=message.location.latitude, longitude=message.location.longitude)
        database.order_cart(user_id)
        database.clear_cart(user_id)
        bot.send_message(user_id, 'Заказ принят!', reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.send_message(user_id, f'{user_name}, чем бы вы хотели себя побаловать?', reply_markup=buttons.main_menu(database.get_product_buttons()))
    else:
        bot.send_message(user_id, 'Отправьте локацию через кнопку "Отправить местоположение" или с помощью скрепки.')
        bot.register_next_step_handler(message, get_loc, text)

def get_tel(message, user_name):
    user_id = message.from_user.id
    if message.contact:
        user_tel = message.contact.phone_number
        database.register(user_id, user_name, user_tel)
        bot.send_message(user_id, 'Ура! Регистрация пройдена! 🥳', reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.send_message(user_id, 'Что бы вы хотели заказать?', reply_markup=buttons.main_menu(database.get_product_buttons()))
    else:
        bot.send_message(user_id, 'Отправьте контакт через кнопку "Отправить номер" или прикрепите его в виде вложения через скрепку.')
        bot.register_next_step_handler(message, get_tel, user_name)

@bot.callback_query_handler(lambda call: int(call.data) in [i[0] for i in database.get_all_product()])
def choose_pr_count(call): #call - словарь с множеством информации, call.data - это айди продукта
    user_id = call.message.chat.id
    pr_info = database.get_certain_prod(int(call.data))
    bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
    bot.send_photo(user_id, photo=pr_info[-1], caption=f'{pr_info[1]}\n\n'
                                                       f'Состав: {pr_info[2]}\n'
                                                       f'Количество: {pr_info[4]} шт.\n'
                                                       f'Цена: {pr_info[3]} сум', reply_markup=buttons.choose_amount(pr_info[4]))
    user_cart[user_id] = {'pr_name': call.data, 'pr_count': 1}

# Обработчик команды админа
@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id == 280453694:
        admin_id = message.from_user.id
        bot.send_message(admin_id, 'Вы вошли в панель администратора', reply_markup=buttons.admin_menu())
        bot.register_next_step_handler(message, choice)
    else:
        bot.send_message(message.from_user.id, 'Вы не являетесь администратором!')

# Этап выбора
def choice(message):
    admin_id = message.from_user.id
    if message.text == 'Добавить продукт':
        bot.send_message(admin_id, 'Добавьте данные о продукте в следующем порядке через точку:\n\n'
                                   'Название. Состав. Цена. Количество. Ссылка на фото\n\n'
                                   'Фотографию можно загрузить на сайт https://postimages.org\n'
                                   'Чтобы корректно добавить фото, скопируйте прямую ссылку.',
                                    reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, add_product)

def add_product(message):
    admin_id = message.from_user.id
    pr_att = message.text.split('. ')
    database.pr_to_db(pr_att[0],pr_att[1],pr_att[2],pr_att[3],pr_att[4])
    bot.send_message(admin_id, 'Готово!')

bot.polling(non_stop=True)