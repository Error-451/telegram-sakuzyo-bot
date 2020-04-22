#!/usr/bin/python
# -*- coding: utf-8 -*-

# This is where functions for handling errors are registered.

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
import logging


logger = logging.getLogger(__name__)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)
