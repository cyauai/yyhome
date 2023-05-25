from aiogram import Bot, Dispatcher, executor, types
from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


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
    money[name] = money[name] + amount/2
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


uri = "mongodb+srv://dbUser:dbUser@yyhome.8qwk7gw.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
collection = client["yydb"]["yycollection"]
document = collection.find()[0]
query = {'_id': ObjectId('646f99c4428dd0fcd5042c6a')}
bot = Bot(token='6178516544:AAHHplpEDdaZRM_nxG1-Lq3YHtwIO1n5DsQ')
dp = Dispatcher(bot)


@dp.message_handler(commands=['add'])
async def add(message: types.Message):
    user = get_user(message)
    point = int(message['text'].replace('/add ', ""))
    replace_score(user, point)
    await message.answer(get_score())


@dp.message_handler(commands=['score'])
async def score(message: types.Message):
    print(message)
    await message.answer(get_score())


@dp.message_handler(commands=['money'])
async def money(message: types.Message):
    await message.answer(get_total())


@dp.message_handler(commands=['spend'])
async def spend(message: types.Message):
    user = get_user(message)
    amount = float(message['text'].replace('/spend ', ""))
    replace_money(user, amount)
    await message.answer(get_total())


@dp.message_handler(commands=['payjor'])
async def payjor(message: types.Message):
    await message.answer(pay_jor())

answers = []  # store the answers they have given

executor.start_polling(dp)
