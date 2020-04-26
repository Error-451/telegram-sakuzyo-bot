#!/usr/bin/python
# -*- coding: utf-8 -*-

# This is where functions for handling messages are registered.

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
import logging
from decorators import *


logger = logging.getLogger(__name__)


@with_checks(silent=True)
def record(update:telegram.Update, context:telegram.ext.CallbackContext):
    if not context.chat_data["recording"]: return
    context.chat_data[update.effective_user.id].append(update.message.message_id)
    logger.info("Recorded a message in chat %s (%d). User: %s (%d), Message ID: %d" % (
        update.effective_chat.title,
        update.effective_chat.id,
        update.effective_user.full_name,
        update.effective_user.id,
        update.message.message_id))


