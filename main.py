#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import configparser

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters

import CommandHandlerFunctions as chfuncs
import MessageHandlerFunctions as mhfuncs
import QueryHandlerFunctions as qhfuncs
import ErrorHandlerFunctions as ehfuncs


logging.basicConfig(format="%(asctime)s [%(name)s][%(levelname)s] %(message)s",
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    pass


def read_config(config_file:str, section:str, key:str):
    config = configparser.ConfigParser()
    config.read(config_file)
    if section in config:
        if key in config[section]:
            return config[section][key]
        else:
            raise ConfigError('Key not found in config file.')
    else:
        raise ConfigError('Section not found in config file.')


def main():

    # initiate the updater with persistence to keep data between restarts
    persistence_keeper = telegram.ext.PicklePersistence(filename = \
            read_config('config.ini','General','Datafile_Name'))
    updater = Updater(read_config('config.ini','General','Token'), \
            persistence = persistence_keeper, use_context=True)

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
    
    updater.start_polling()
    logger.info("Started the bot!")
    updater.idle()


if __name__ == '__main__':
    main()

