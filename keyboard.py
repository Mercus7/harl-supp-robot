from aiogram import types



menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(
    types.KeyboardButton('❇️Админка')
)

adm = types.ReplyKeyboardMarkup(resize_keyboard=True)
adm.add(
    types.KeyboardButton('▪️Чёрный список'),
    types.KeyboardButton('🔺Добавить в чёрный список'),
    types.KeyboardButton('🔻Убрать из чёрного списка')
)
adm.add(types.KeyboardButton('📧Рассылка'))
adm.add('« Назад')

back = types.ReplyKeyboardMarkup(resize_keyboard=True)
back.add(
    types.KeyboardButton('⛔️Отмена')
)


def fun(user_id):
    quest = types.InlineKeyboardMarkup(row_width=3)
    quest.add(
        types.InlineKeyboardButton(text='✍️Ответить', callback_data=f'{user_id}-ans'),
        types.InlineKeyboardButton(text='🗑Удалить', callback_data='ignor')
    )
    return quest