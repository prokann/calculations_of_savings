import telebot
from .models import *
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


bot = telebot.TeleBot()


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Привіт! Це бот для підрахунку заощаджень. "
                                      "\nЄ такі команди: "
                                      "\n'/add_type' - створити новий тип заощаджень, "
                                      "\n'/delete_type' - видалити тип, "
                                      "\n'/view_types' - переглянути всі типи, "
                                      "\n'/add_savings' - додати нові заощадження, "
                                      "\n'/withdraw_savings' - зняти заощадження.")
    user = User.objects.get_or_create(chat_id=message.chat.id)


@bot.message_handler(func=lambda n: True)
def commands(message):

    if message.text == '/add_type':
        bot.send_message(message.chat.id, "Напишіть назву для нового типу заощадження. Якщо передумали, напишіть: 'Ні'.")
        bot.register_next_step_handler(message, new_type)

    if message.text == '/view_types' or message.text == '/add_savings' or message.text == '/withdraw_savings' or message.text == '/delete_type':
        show_types(message.chat.id, message.text)


@bot.message_handler(func=lambda n: True)
def new_type(message):
    if message.text != 'Ні':
        type = SavingsType.objects.get_or_create(user_id=message.chat.id, name=message.text, amount=0)
        bot.send_message(message.chat.id, f"Тип {type[0].name} створено!")
    else:
        bot.send_message(message.chat.id, "Команду скасовано.")


@bot.message_handler(func=lambda n: True)
def show_types(chat_id, command):
    types = SavingsType.objects.filter(user_id=chat_id)

    keyboard = []
    for type in types:
        button = InlineKeyboardButton(type.name, callback_data=f'{command}__{type.id}')
        keyboard.append([button])

    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id, "Виберіть тип заощадження: ", reply_markup=reply_markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('/delete_type'))
def callback_query(call):
    SavingsType.objects.get(id=int(call.data.split('__')[1])) .delete()
    bot.send_message(call.message.chat.id, 'Цей тип видалено')



@bot.callback_query_handler(func=lambda call: call.data.startswith('/view_types'))
def callback_query(call):
    bot.send_message(call.message.chat.id, f"У типі '{SavingsType.objects.get(id=int(call.data.split('__')[1])).name}' "
                                           f"{SavingsType.objects.get(id=int(call.data.split('__')[1])).amount} грошей.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('/add_savings'))
def callback_query(call):
    bot.send_message(call.message.chat.id, f"Тут {SavingsType.objects.get(id=int(call.data.split('__')[1])).amount} "
                                           f"грошей. Скільки хочете додати?")
    bot.register_next_step_handler(call.message, lambda message: add_money(call.message.chat.id, call, message))


@bot.message_handler(func=lambda n: True)
def add_money(chat_id, type, message):
    try:
        amount = SavingsType.objects.get(id=int(type.data.split('__')[1])).amount + int(message.text)
        item = SavingsType.objects.get(pk=int(type.data.split('__')[1]))
        item.amount = amount
        item.save()
        bot.send_message(chat_id, f'Тепер ваші накопичення становлять {amount}')

    except Exception as e:
        bot.send_message(chat_id, 'Ви ввели не число.')


@bot.callback_query_handler(func=lambda call: call.data.startswith('/withdraw_savings'))
def callback_query(call):
    bot.send_message(call.message.chat.id, f"Тут {SavingsType.objects.get(id=int(call.data.split('__')[1])).amount} "
                                           f"грошей. Скільки хочете зняти?")
    bot.register_next_step_handler(call.message, lambda message: withdraw_money(call.message.chat.id, call, message))


@bot.message_handler(func=lambda n: True)
def withdraw_money(chat_id, type, message):
    try:
        amount = SavingsType.objects.get(id=int(type.data.split('__')[1])).amount - int(message.text)
        item = SavingsType.objects.get(pk=int(type.data.split('__')[1]))
        item.amount = amount
        item.save()
        bot.send_message(chat_id, f'Тепер ваші накопичення становлять {amount}')
    except Exception as e:
        bot.send_message(chat_id, 'Ви ввели не число.')


bot.polling(none_stop=True)


