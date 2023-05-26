import asyncio

from aiogram import Bot, Dispatcher, executor, types
from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os


def get_total():
    doc = collection.find()[0]
    money = doc['money']
    yin_amount = money['yin']
    yo_amount = money['yo']
    if yin_amount == 0 and yo_amount == 0:
        return "唔洗俾錢錢"
    if yin_amount >= yo_amount:
        return "肥婆堯要俾綽言: ＄" + str(yin_amount)
    else:
        return "可憐綽言要俾肥婆堯: ＄" + str(yo_amount)


def pay_jor():
    doc = collection.find()[0]
    doc['money'] = {'yin': 0.0, 'yo': 0.0}
    update_replacement(doc)
    return "一筆勾消了"


def replace_money(name, amount):
    doc = collection.find()[0]
    money = doc['money']
    money[name] = money[name] + amount / 2
    yin_amount = money['yin']
    yo_amount = money['yo']
    if yin_amount >= yo_amount:
        money['yin'] = money['yin'] - money['yo']
        money['yo'] = 0.0
    else:
        money['yo'] = money['yo'] - money['yin']
        money['yin'] = 0.0
    doc['money'] = money
    update_replacement(doc)


def replace_score(name, point):
    doc = collection.find()[0]
    score = doc['score']
    score[name] = score[name] + point
    doc['score'] = score
    update_replacement(doc)


def get_user(msg):
    if msg['from']['first_name'] == '.':
        return 'yin'
    else:
        return 'yo'


def update_replacement(doc):
    collection.replace_one(query, doc)


def get_doc():
    return collection.find()[0]


def get_score():
    return get_doc()['score']


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


WEBHOOK_HOST = 'yy-home.herokuapp.com'
BOT_TOKEN = '6178516544:AAHHplpEDdaZRM_nxG1-Lq3YHtwIO1n5DsQ'
WEBAPP_HOST = '0.0.0.0'
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

if __name__ == '__main__':
    print("HELLO BOT START")
    port = int(os.environ.get('PORT', '5001'))
    uri = "mongodb+srv://dbUser:dbUser@yyhome.8qwk7gw.mongodb.net/?retryWrites=true&w=majority"
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    collection = client["yydb"]["yycollection"]
    document = collection.find()[0]
    query = {'_id': ObjectId('646f99c4428dd0fcd5042c6a')}
    token = '6178516544:AAHHplpEDdaZRM_nxG1-Lq3YHtwIO1n5DsQ'
    bot = Bot(token=token)
    dp = Dispatcher(bot)
    answers = []  # store the answers they have given
    executor.start_webhook(port=port, dispatcher=dp, webhook_path=f'/webhook/{token}', on_startup=on_startup)
    # executor.start_polling(dp)


@dp.async_task
@dp.message_handler(commands=['add'])
async def add(message: types.Message):
    await asyncio.sleep(2)
    user = get_user(message)
    point = int(message['text'].replace('/add ', ""))
    replace_score(user, point)
    await message.answer(get_score())


@dp.async_task @ dp.async_task
@dp.message_handler(commands=['score'])
async def score(message: types.Message):
    await asyncio.sleep(2)
    print(message)
    await message.answer(get_score())


@dp.async_task
@dp.message_handler(commands=['money'])
async def money(message: types.Message):
    await asyncio.sleep(2)
    await message.answer(get_total())


@dp.async_task
@dp.message_handler(commands=['spend'])
async def spend(message: types.Message):
    await asyncio.sleep(2)
    user = get_user(message)
    amount = float(message['text'].replace('/spend ', ""))
    replace_money(user, amount)
    await message.answer(get_total())


@dp.async_task
@dp.message_handler(commands=['payjor'])
async def payjor(message: types.Message):
    await asyncio.sleep(2)
    await message.answer(pay_jor())
