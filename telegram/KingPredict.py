
# coding: utf-8

# In[1]:


import telegram
from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)
import Dunkest_BOT


token_api = '584681226:AAG1F0B6Liietx8njooXXLl238x7ThjU2nQ'
bot = telegram.Bot(token=token_api)
print(bot.get_me())

updater = Updater(token=token_api)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

def computeteam(bot, update, args):
    credits_total = float(args[0])
    dunkest_bot = Dunkest_BOT.dunkest_bot()
    dunkest_bot.credits_total = credits_total
    dunkest_bot.credits_computed = credits_total
    bot.send_message(chat_id = update.message.chat_id, text = "Starting computing stuffs")
    dunkest_bot.read_data_from_disk_telegram()
    bot.send_message(chat_id = update.message.chat_id, text = "I'm computing the best team for you :)")
    dunkest_bot.maximization_scores()
    bot.send_message(chat_id = update.message.chat_id, text = "Here we are, enjoy!")
    text_output = dunkest_bot.final_print_telegram()
    bot.send_message(chat_id = update.message.chat_id, text = text_output)

def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        # remove update.message.chat_id from conversation list
        print("Unauthorized")
    except BadRequest:
        # handle malformed requests - read more below!
        bot.send_message(chat_id = update.message.chat_id, text = "Your message can't be empty!")
    except TimedOut:
        # handle slow connection problems
        print("TimedOut")
    except NetworkError:
        # handle other connection problems
        print("NetworkError")
    except ChatMigrated as e:
        # the chat_id of a group has changed, use e.new_chat_id instead
        print("ChatMigrated")
    except TelegramError:
        # handle all other telegram related errors
        print("TelegramError")

dunkest_handler = CommandHandler('team', computeteam, pass_args=True)
dispatcher.add_handler(dunkest_handler)

dispatcher.add_error_handler(error_callback)

updater.start_polling()
updater.idle()
#updater.stop()
