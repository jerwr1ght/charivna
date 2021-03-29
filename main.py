# -*- coding: utf8 -*-
import telebot
import random
from telebot import types
import config
import threading
import psycopg2
url = urlparse.urlparse(os.environ['DATABASE_URL'])
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port
global db
global sql
db = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host,
    port=port
)
sql=db.cursor()
sql.execute("""CREATE TABLE IF NOT EXISTS players (chatid TEXT, username TEXT, cash INT, inbank INT, total INT, job_blocked TEXT)""")
db.commit()

bot=telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    sql.execute(f"SELECT cash FROM players WHERE chatid = '{message.chat.id}'")
    res=sql.fetchone()
    if res is None:
        choose_nickname=bot.send_message(message.chat.id, "Напишите ваш никнейм для игры (в дальнейшем его можно изменить)")
        bot.register_next_step_handler(choose_nickname, creating_account)


@bot.message_handler(content_types=['text'])
def chatting(message):
    global choosing_cash
    if message.text=='🎲 Играть в кости':
        choosing_cash=bot.send_message(message.chat.id, "На какую сумму хотите сыграть?")
        bot.register_next_step_handler(choosing_cash, roll_win)
    elif message.text=='💰 Баланс':
        sql.execute(f"SELECT * FROM players WHERE chatid = '{message.chat.id}'")
        res=sql.fetchone()
        msg= f"💰 <b>Ваш баланс</b> 💰\n\n👋 Наличные: {res[2]} 💸\n🏦 В банке: {res[3]} 💸\n⚖️ Всего: {res[4]} 💸"
        bot.send_message(message.chat.id, msg, parse_mode='html')
    elif message.text=='💼 Работать':
        sql.execute(f"SELECT job_blocked FROM players WHERE chatid = '{message.chat.id}'")
        res=sql.fetchone()
        if res[0]!='blocked':
            fee = random.randint(100,500)
            sql.execute(f"UPDATE players SET inbank = inbank + {fee}, total = total + {fee} WHERE chatid = '{message.chat.id}'")
            db.commit()
            sql.execute(f"UPDATE players SET job_blocked = 'blocked' WHERE chatid = '{message.chat.id}'")
            db.commit()
            bot.send_message(message.chat.id, f'Спасибо за работу. {fee} 💸 были переведены на ваш банковский счёт! Данная работа временно вам не доступна. Ожидайте 5 минут.')
            print(f"{message.from_user.username} заработал {fee}")
            import check_work
            user_id=str(message.chat.id)
            check_work.t = threading.Timer(300.0, check_work.block_work, args=(user_id,))
            check_work.t.start()
        else:
            bot.send_message(message.chat.id, 'К сожалению, ещё длится перерыв. Подождите, пожалуйста!')
    elif message.text=='💵 Положить на банковский счёт':
        user_cash=bot.send_message(message.chat.id, "Какую сумму хотите перевести?")
        bot.register_next_step_handler(user_cash, to_bank)
    elif message.text=='🏦 Снять с банковского счёта':
        user_inbank=bot.send_message(message.chat.id, "Какую сумму хотите снять?")
        bot.register_next_step_handler(user_inbank, from_bank)
    elif message.text=='🏆 Список лидеров':
        counter = 0
        msg = '🏆 Список самых богатых игроков 🏆\n\n'
        no_repeat=False
        for row in sql.execute(f"SELECT username, total, chatid FROM players ORDER BY total DESC LIMIT 10"):
            if row[2]==message.chat.id:
                no_repeat=True
                counter += 1
                msg = f"{msg}<b><u>#{counter}</u> | {row[0]} (Вы)</b> - {row[1]} 💸\n"
            else:
                counter += 1
                msg = f"{msg}<b><u>#{counter}</u> | {row[0]}</b> - {row[1]} 💸\n"
        if no_repeat==True:
            counter = 0
            for row in sql.execute(f"SELECT username, total, chatid FROM players ORDER BY total"):
                counter += 1
                if row[2] == message.chat.id:
                    continue
            msg=f"{msg}\nВы занимаете <b>{counter}-ое</b> место, но ваше место в таблице лидеров не за горами!"
        bot.send_message(message.chat.id, msg, parse_mode='html')

#Проверка на баланс на руках для игры в кости
def roll_win(message):
    global bot_dice
    global amount
    try:
        amount=int(message.text)
        sql.execute(f"SELECT cash FROM players WHERE chatid = '{message.chat.id}'")
        res=sql.fetchone()
        if res[0]>=amount:
            bot_dice = bot.send_dice(message.chat.id, emoji='🎲')
            bot.send_message(message.chat.id, 'Ваша очередь бросать игральную кость! (Отправьте этот эмодзи - 🎲, либо нажмите на кость выше)')
            bot.register_next_step_handler(bot_dice, user_dice)
        else:
            bot.reply_to(message, f'Ваших наличных не хватает для ставки на сумму {amount} 💸')
    except: 
        return
#Проверка на выигрыш в кости
def user_dice(message):
    if message.dice.emoji=='🎲':
        if bot_dice.dice.value>message.dice.value:
            bot.send_message(message.chat.id, f'К сожалению, вы проиграли. \n<b>Сумма проигрыша:</b> {amount} 💸', parse_mode='html')
            sql.execute(f"UPDATE players SET cash = cash - {amount}, total = total - {amount} WHERE chatid = '{message.chat.id}'")
            db.commit()
            print(f'{message.from_user.username} проиграл {amount} в игре "Кости"')
        elif bot_dice.dice.value==message.dice.value:
            bot.send_message(message.chat.id, f'В этот раз - ничья. Ваши {amount} 💸 вернутся к вам на счёт')
        else:
            sql.execute(f"UPDATE players SET cash = cash + {amount}, total = total + {amount} WHERE chatid = '{message.chat.id}'")
            db.commit()
            bot.send_message(message.chat.id, f'Поздравляю! Вы выиграли {amount} 💸')
            print(f'{message.from_user.username} выиграл {amount} в игре "Кости"')

#Перевод на банковский счёт
def to_bank(message):
    try:
        amount=int(message.text)
        sql.execute(f"SELECT cash FROM players WHERE chatid = '{message.chat.id}'")
        res=sql.fetchone()
        if res[0]>=amount:
            sql.execute(f"UPDATE players SET inbank = inbank + {amount}, cash = cash - {amount}, total = inbank + cash WHERE chatid = '{message.chat.id}'")
            db.commit()
            bot.send_message(message.chat.id, f'{amount} 💸 были отправлены на ваш банковский счёт!')
            bot.register_next_step_handler(bot_dice, user_dice)
            print(f'{message.from_user.username} положил {amount} на банковский счёт')
        else:
            bot.reply_to(message, f'Ваших наличных не хватает для перевода на сумму {amount} 💸')
    except: 
        return

#Снятие наличных
def from_bank(message):
    try:
        amount=int(message.text)
        sql.execute(f"SELECT inbank FROM players WHERE chatid = '{message.chat.id}'")
        res=sql.fetchone()
        if res[0]>=amount:
            sql.execute(f"UPDATE players SET cash = cash + {amount}, inbank = inbank - {amount}, total = cash + inbank WHERE chatid = '{message.chat.id}'")
            db.commit()
            bot.send_message(message.chat.id, f'Вы сняли {amount} 💸 с вашего банковского счёта!')
            bot.register_next_step_handler(bot_dice, user_dice)
            print(f'{message.from_user.username} списал {amount} с банковского счёта')
        else:
            bot.reply_to(message, f'Недостаточно денег на банковском счету для снятия {amount} 💸')
    except: 
        return

def creating_account(message):
    sql.execute(f"SELECT username FROM players WHERE username = '{message.text}'")
    if sql.fetchone() is None and len(message.text)>=1 and len(message.text)<=15:
        username=message.text
    elif len(message.text)>15:
        bot.reply_to(message, f"Ваш никнейм состоит из более 15 символов. Используйте другой и начните заново - /start")
        return
    else:
        bot.reply_to(message, f"Этот никнейм занят. Используйте другой и начните заново, используя команду /start")
        return
    start_cash=150
    start_bank=0
    total=start_cash+start_bank
    sql.execute("INSERT INTO players VALUES (?, ?, ?, ?, ?, ?)", (message.chat.id, username, start_cash, start_bank, total, 'unblocked'))
    db.commit()
    adding_keyboard()
    bot.send_message(message.chat.id, f'<b>Добро пожаловать в игровой мир, {username}!</b> Внизу появилось ваше меню для игры.\nСейчас у вас на руках: 150 💸. Используя меню, вы можете работать, играть, проводить банковские операции и не только.\n\nСтаньте <u>самым богатым</u> человеком в этой игре! (Следите за списком лидеров)', reply_markup=markup_reply, parse_mode='html')
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEBD05gX7Z7x5kCc1iqEBF0HeFaRzXH3gACAwEAAladvQoC5dF4h-X6Tx4E')
    print("Новый пользователь Casinogg Bot - "+username)
#Добавляем клавиатуру
def adding_keyboard():
    global markup_reply
    markup_reply=types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup_reply.add(types.KeyboardButton('🎲 Играть в кости'), types.KeyboardButton('💼 Работать'))
    markup_reply.add(types.KeyboardButton('💵 Положить на банковский счёт'), types.KeyboardButton('🏦 Снять с банковского счёта'))
    markup_reply.add(types.KeyboardButton('💰 Баланс'))
    markup_reply.add(types.KeyboardButton('🏆 Список лидеров'))




bot.polling(none_stop=True)