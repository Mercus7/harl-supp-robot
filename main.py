import logging
from aiogram import Bot, Dispatcher, executor, types
from config import API_TOKEN, admin
import keyboard as kb
import functions as func
import sqlite3
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import Throttled

storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
connection = sqlite3.connect('data.db')
q = connection.cursor()

class st(StatesGroup):
	item = State()
	item2 = State()
	item3 = State()
	item4 = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			await message.answer('<b>Добро пожаловать, администратор.</b>', reply_markup=kb.menu, parse_mode='HTML')
		else:
			await message.answer('<b>👋 Приветствую, если появились вопросы - обращайтесь</b>\n\n<b>🚀 Я постараюсь ответить быстей на ваш вопрос как освобожусь.</b>', parse_mode='HTML')
	else:
		await message.answer('<b<❗️Ваш аккаунт заблокирован в данном боте.</b>', parse_mode='HTML')


@dp.message_handler(content_types=['text'], text='❇️Админка')
async def handfler(message: types.Message, state: FSMContext):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			await message.answer('<b>Добро пожаловать в админ-панель</b>', reply_markup=kb.adm, parse_mode='HTML')

@dp.message_handler(content_types=['text'], text='« Назад')
async def handledr(message: types.Message, state: FSMContext):
	await message.answer('<b>Добро пожаловать, администратор</b>', parse_mode='HTML', reply_markup=kb.menu)

@dp.message_handler(content_types=['text'], text='▪️Чёрный список')
async def handlaer(message: types.Message, state: FSMContext):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			q.execute(f"SELECT * FROM users WHERE block == 1")
			result = q.fetchall()
			sl = []
			for index in result:
				i = index[0]
				sl.append(i)

			ids = '\n'.join(map(str, sl))
			await message.answer(f'*📋 ID пользователей в ЧС:*\n`{ids}`', parse_mode='Markdown')

@dp.message_handler(content_types=['text'], text='🔺Добавить в чёрный список')
async def hanadler(message: types.Message, state: FSMContext):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			await message.answer('<b>💁‍♂️ Введите id пользователя, которого нужно заблокировать:</b>', reply_markup=kb.back, parse_mode='HTML')
			await st.item3.set()

@dp.message_handler(content_types=['text'], text='🔻Убрать из чёрного списка')
async def hfandler(message: types.Message, state: FSMContext):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			await message.answer('<b>💁‍♂️ Введите id пользователя, которого нужно разблокировать:</b>', reply_markup=kb.back, parse_mode='HTML')
			await st.item4.set()

@dp.message_handler(content_types=['text'], text='📧Рассылка')
async def hangdler(message: types.Message, state: FSMContext):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			await message.answer('<b>💁‍♂️ Введите сообщение для рассылки:\n\nВы можете отменить по кнопке внизу 👇</b>', reply_markup=kb.back, parse_mode='HTML')
			await st.item.set()

@dp.message_handler(content_types=['text'])
@dp.throttled(func.antiflood, rate=3)
async def h(message: types.Message, state: FSMContext):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			pass
		else:
			await message.answer('<b>✅ Ваше сообщение было отправлено. Ожидайте её ответа...</b>\n\n<b>⚠️ Просьба:</b> <i>не флудите, отвечю всем! Будите спамить улетите в чёрный список.</i>', parse_mode='HTML')
			await bot.send_message(admin, f"*🛎 Получен новый вопрос*\n*От:* {message.from_user.mention}\nID: `{message.chat.id}`\n*Сообщение:* {message.text}", reply_markup=kb.fun(message.chat.id), parse_mode='Markdown')
	else:
		await message.answer('<b<❗️Ваш аккаунт заблокирован в данном боте</b>', parse_mode='HTML')


@dp.callback_query_handler(lambda call: True) # Inline часть
async def cal(call, state: FSMContext):
	if 'ans' in call.data:
		a = call.data.index('-ans')
		ids = call.data[:a]
		await call.message.answer('<i>💁‍♂️ Введите ответ пользователю:</i>', reply_markup=kb.back, parse_mode='HTML')
		await st.item2.set() # админ отвечает пользователю
		await state.update_data(uid=ids)
	elif 'ignor' in call.data:
		await call.answer('Успешно удалено')
		await bot.delete_message(call.message.chat.id, call.message.message_id)
		await state.finish()

@dp.message_handler(state=st.item2)
async def proc(message: types.Message, state: FSMContext):
	if message.text == '⛔️Отмена':
		await message.answer('<b>❗️Действие отменено</b>', reply_markup=kb.menu, parse_mode='HTML')
		await state.finish()
	else:
		await message.answer('<b>✅ Сообщение было доставлено пользователю</b>', reply_markup=kb.menu, parse_mode='HTML')
		data = await state.get_data()
		id = data.get("uid")
		await state.finish()
		await bot.send_message(id, '<i>🛎 Вам поступил ответ:</i>\n\n<b>{}</b>' .format(message.text), parse_mode='HTML')
@dp.message_handler(state=st.item)
async def process_name(message: types.Message, state: FSMContext):
	q.execute(f'SELECT user_id FROM users')
	row = q.fetchall()
	connection.commit()
	text = message.text
	if message.text == '⛔️Отмена':
		await message.answer('<b>❗️Действие отменено</b>', reply_markup=kb.adm, parse_mode='HTML')
		await state.finish()
	else:
		info = row
		await message.answer('<b>✅ Рассылка запущена</b>', reply_markup=kb.adm, parse_mode='HTML')
		for i in range(len(info)):
			try:
				await bot.send_message(info[i][0], str(text))
			except:
				pass
		await message.answer('<b>❗️Рассылка завершена</b>', reply_markup=kb.adm, parse_mode='HTML')
		await state.finish()


@dp.message_handler(state=st.item3)
async def proce(message: types.Message, state: FSMContext):
	if message.text == '⛔️Отмена':
		await message.answer('<b>❗️Действие отменено</b>', reply_markup=kb.adm, parse_mode='HTML')
		await state.finish()
	else:
		if message.text.isdigit():
			q.execute(f"SELECT block FROM users WHERE user_id = {message.text}")
			result = q.fetchall()
			connection.commit()
			if len(result) == 0:
				await message.answer('<b>⚠️ Такой пользователь не найден в базе данных</b>', reply_markup=kb.adm, parse_mode='HTML')
				await state.finish()
			else:
				a = result[0]
				id = a[0]
				if id == 0:
					q.execute(f"UPDATE users SET block = 1 WHERE user_id = {message.text}")
					connection.commit()
					await message.answer('<b>✅ Пользователь успешно заблокирован</b>', reply_markup=kb.adm, parse_mode='HTML')
					await state.finish()
					await bot.send_message(message.text, '<b>❗️Вы были заблокированы в данном боте</b>', parse_mode='HTML')
				else:
					await message.answer('<b>⚠️ Данный пользователь уже имеет блокировку</b>', reply_markup=kb.adm, parse_mode='HTML')
					await state.finish()
		else:
			await message.answer('<b>⚠️Ты вводишь буквы!\n\nВведи ID:</b>', parse_mode='HTML')

@dp.message_handler(state=st.item4)
async def proc(message: types.Message, state: FSMContext):
	if message.text == '⛔️Отмена':
		await message.answer('<b>❗️Действие отменено</b>', reply_markup=kb.adm, parse_mode='HTML')
		await state.finish()
	else:
		if message.text.isdigit():
			q.execute(f"SELECT block FROM users WHERE user_id = {message.text}")
			result = q.fetchall()
			connection.commit()
			if len(result) == 0:
				await message.answer('<b>⚠️ Такой пользователь не найден в базе данных</b>', reply_markup=kb.adm, parse_mode='HTML')
				await state.finish()
			else:
				a = result[0]
				id = a[0]
				if id == 1:
					q.execute(f"UPDATE users SET block = 0 WHERE user_id = {message.text}")
					connection.commit()
					await message.answer('<b>✅ Пользователь успешно разбанен</b>', reply_markup=kb.adm, parse_mode='HTML')
					await state.finish()
					await bot.send_message(message.text, '<b>❗️Вы были разблокированы администрацией</b>', parse_mode='HTML')
				else:
					await message.answer('<b>⚠️ Данный пользователь не заблокирован</b>', reply_markup=kb.adm, parse_mode='HTML')
					await state.finish()
		else:
			await message.answer('<b>⚠️ Ты вводишь буквы!\n\nВведи ID:</b>', parse_mode='HTML')

if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)
