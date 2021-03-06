#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import configparser
import os
import sys

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters

sys.path.append('src/')
import CommandHandlerFunctions as chfuncs
import MessageHandlerFunctions as mhfuncs
import QueryHandlerFunctions as qhfuncs
import ErrorHandlerFunctions as ehfuncs
sys.path.pop()


logging.basicConfig(format="%(asctime)s [%(name)s][%(levelname)s] %(message)s",
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    pass


def read_config(section:str, key:str, config_file:str='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_file)
    if section in config:
        if key in config[section]:
            return config[section][key]
        else:
            raise ConfigError('Key %s not found in config file.' % key)
    else:
        raise ConfigError('Section %s not found in config file.' % section)


def main():
    
    use_webhook = False
    is_heroku = False
    # First check the arguments
    for sysarg in sys.argv:
        if sysarg == "--webhook": use_webhook = True
        if sysarg == "--heroku": is_heroku = True

    if is_heroku: # On Heroku, use config vars instead of config file.
        TOKEN = os.environ.get('TOKEN')
        DATAFILE_NAME = os.environ.get('DATAFILE_NAME','SakuzyoBot.dat')
        if use_webhook:
            PORT = int(os.environ.get('PORT', '8443'))
            WEBHOOK_ADDRESS = os.environ.get('APP_ADDRESS')
    else:
        TOKEN = read_config('General','Token')
        DATAFILE_NAME = read_config('General','Datafile_Name')
        if use_webhook:
            PORT = int(read_config('Webhook','Port'))
            WEBHOOK_ADDRESS = read_config('Webhook','Address')

    # initiate the updater with persistence to keep data between restarts
    persistence_keeper = telegram.ext.PicklePersistence(filename = DATAFILE_NAME)
    updater = Updater(TOKEN, persistence = persistence_keeper, use_context=True)

    dp = updater.dispatcher

    # handle commands
    dp.add_handler(CommandHandler("start", chfuncs.start))
    dp.add_handler(CommandHandler("check", chfuncs.check))
    dp.add_handler(CommandHandler("stop", chfuncs.stop))
    dp.add_handler(CommandHandler("delete", chfuncs.delete))

    # record all non-command messages
    dp.add_handler(MessageHandler(Filters.all, mhfuncs.record))

    dp.add_handler(CallbackQueryHandler(qhfuncs.process_callback_query))

    # handle errors
    dp.add_error_handler(ehfuncs.error)
    
    if use_webhook:
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
        updater.bot.set_webhook(WEBHOOK_ADDRESS + TOKEN)
        logger.info("Started the bot using webhook mode!")
    else:
        if not updater.bot.delete_webhook: # Unset the webhook to use polling.
            logger.warning("Webhook deletion failed! I am unable to receive updates.")
        updater.start_polling()
        logger.info("Started the bot using polling mode!")
        updater.idle()


if __name__ == '__main__':
    main()

