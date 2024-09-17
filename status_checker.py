import datetime
import telebot
from telebot import types
import json
bot = telebot.TeleBot('') #bot API here

with open("ser.json", "r") as outfile:
    servers = json.load(outfile)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f'Обновить 🔁', callback_data="restart"))
    for server, condition in servers.items():
        status = condition['status']
        data = condition['date']
        user = condition['user']
        if not status:
            markup.add(types.InlineKeyboardButton(f'{server} свободен ✅       ЗАНЯТЬ', callback_data=f'{server}{not status}'))
        if status:
            if condition['userid'] != f'{message.from_user.id}':
                markup.add(types.InlineKeyboardButton(f'{server} занял {user},{data}⛔️ УВЕДОМИТЬ', parse_mode='html', reply_markup=markup, callback_data=f'{server}queue'))
            if condition['userid'] == f'{message.from_user.id}':
                markup.add(types.InlineKeyboardButton(f' {server} 🕊            ОСВОБОДИТЬ', parse_mode='html',reply_markup=markup, callback_data=f'{server}{status}'))
    bot.send_message(message.chat.id, "Выберите сервер:".format(message.from_user), reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global servers
    n = 0
    for server, condition in servers.items():
        status = condition['status']
        if callback.data == f'{server}{status}':
            if f'{callback.from_user.first_name} {callback.from_user.last_name}' == condition['user']:
                condition['status'] = False
                condition['user'] = ""
                condition['userid'] = ""
                n = 1
                for chat in condition['queue']:
                    bot.send_message(chat_id=chat, text=f"{server} был особожден 📣")
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton(f'Обновить 🔁', callback_data="restart"))
                    for server, condition in servers.items():
                        status = condition['status']
                        data = condition['date']
                        user = condition['user']
                        if not status:
                            markup.add(types.InlineKeyboardButton(f'{server}, свободен ✅       ЗАНЯТЬ',callback_data=f'{server}{not status}'))
                        if status:
                            if int(condition['userid']) != int(f'{callback.from_user.id}'):
                                markup.add(types.InlineKeyboardButton(f'{server} занял {user},{data}⛔️ УВЕДОМИТЬ',parse_mode='html', reply_markup=markup, callback_data=f'{server}queue'))
                            if int(condition['userid']) == int(f'{callback.from_user.id}'):
                                markup.add(types.InlineKeyboardButton(f'{server} 🕊            ОСВОБОДИТЬ ', parse_mode='html', reply_markup=markup, callback_data=f'{server}{status}'))
                    bot.send_message(chat_id=chat, text="Выберите сервер:".format(callback.message.from_user),reply_markup=markup)
                    condition['queue'] = []

        if callback.data == f'{server}{not status}':
                date = datetime.datetime.now().strftime("%H:%M")
                condition['status'] = True
                condition['userid'] = f'{callback.from_user.id}'
                if f'{callback.from_user.first_name}' != "" and f'{callback.from_user.last_name}' != "":
                    condition['user'] = f'{callback.from_user.first_name} {callback.from_user.last_name}'
                elif f'{callback.from_user.last_name}' == "":
                    condition['user'] = f'{callback.from_user.first_name}'
                elif f'{callback.from_user.first_name}' == "":
                    condition['user'] = f'{callback.from_user.username}'
                else:
                    pass
                condition['date'] = f'{date}'
                n = 1

        if callback.data == f'{server}queue':
            if f'{callback.from_user.id}' not in condition['queue']:
                condition['queue'].append(f'{callback.from_user.id}')
                bot.send_message(callback.message.chat.id,"Вы подписались на обновление ☑️".format(callback.message.from_user))
            elif f'{callback.from_user.id}' in condition['queue']:
                bot.send_message(callback.message.chat.id,"Вы уже подписаны ☑️".format(callback.message.from_user))

    if callback.data == "restart" or n == 1:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(f'Обновить 🔁', callback_data="restart"))
        for server, condition in servers.items():
            status = condition['status']
            data = condition['date']
            user = condition['user']
            if not status:
                markup.add(types.InlineKeyboardButton(f'{server}, свободен ✅       ЗАНЯТЬ', callback_data=f'{server}{not status}'))
            if status:
                if int(condition['userid']) != int(f'{callback.from_user.id}'):
                    markup.add(types.InlineKeyboardButton(f'{server} занял {user},{data}⛔️ УВЕДОМИТЬ', parse_mode='html', reply_markup=markup, callback_data=f'{server}queue'))
                if int(condition['userid']) == int(f'{callback.from_user.id}'):
                    markup.add(types.InlineKeyboardButton(f'{server} 🕊            ОСВОБОДИТЬ ', parse_mode='html', reply_markup=markup,callback_data=f'{server}{status}'))
        bot.send_message(callback.message.chat.id, "Выберите сервер:".format(callback.message.from_user), reply_markup=markup)
    with open('ser.json', 'w') as fp:
        json.dump(servers, fp)


bot.polling(none_stop=True, interval=0)
