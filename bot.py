import asyncio

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
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
    if msg['first_name'] == '.':
        return 'yin'
    else:
        return 'yo'


def update_replacement(doc):
    collection.replace_one(query, doc)


def get_doc():
    return collection.find()[0]


def get_score():
    return get_doc()['score']


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)
    point = int(update.message.text.replace('/add ', ""))
    replace_score(user, point)
    update.message.reply_text(get_score())


async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_score())


async def money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_total())


async def spend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.message.from_user)
    amount = float(update.message.text.replace('/spend ', ""))
    replace_money(user, amount)
    await update.message.reply_text(get_total())


async def payjor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(pay_jor())


BOT_TOKEN = '6178516544:AAHHplpEDdaZRM_nxG1-Lq3YHtwIO1n5DsQ'
WEBAPP_HOST = '0.0.0.0'

if __name__ == '__main__':
    print("HELLO BOT START")
    port = int(os.environ.get('PORT', '5001'))
    uri = "mongodb+srv://dbUser:dbUser@yyhome.8qwk7gw.mongodb.net/?retryWrites=true&w=majority"
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    collection = client["yydb"]["yycollection"]
    document = collection.find()[0]
    query = {'_id': ObjectId('646f99c4428dd0fcd5042c6a')}
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('add', add))
    application.add_handler(CommandHandler('money', money))
    application.add_handler(CommandHandler('payjor', payjor))
    application.add_handler(CommandHandler('score', score))
    application.add_handler(CommandHandler('spend', spend))
    application.run_polling()