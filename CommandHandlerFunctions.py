#!/usr/bin/python
# -*- coding: utf-8 -*-

# This is where functions for handling commands are registered.

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
import logging
import json
from threading import Thread
from time import strftime, sleep

from decorators import *


logger = logging.getLogger(__name__)


@recorded
@with_checks(silent=False)
@admins_only
def check(update:telegram.Update, context:telegram.ext.CallbackContext):
    if context.chat_data["recording"]:
        update.message.reply_text("All checks passed. Recording is on.")
    elif not context.chat_data["recording"]:
        update.message.reply_text("All checks passed. Recording is off.")


@recorded
@with_checks(silent=False)
@admins_only
def start(update:telegram.Update, context:telegram.ext.CallbackContext):

    myself = context.bot

    # does the check first
    if not check_group_type(update.message): return
    if not check_permission(update.message, myself): return

    if context.chat_data["recording"]: # check if already recording
        update.message.reply_text("Already recording.")
    else:
        context.chat_data["recording"] = 1
        update.message.reply_text("Started recording.")
        logger.info("Started recording in chat %s (%d)." % (
            update.effective_chat.title,
            update.effective_chat.id))


@recorded
@with_checks(silent=False)
@admins_only
def stop(update:telegram.Update, context:telegram.ext.CallbackContext):

    if not context.chat_data["recording"]: # check if not recording at all
        update.message.reply_text("Not recording so not stopped.")
    else:
        context.chat_data["recording"] = 0
        update.message.reply_text("Stopped recording!")
        logger.info("Stopped recording in chat %s (%d)." % (
            update.effective_chat.title,
            update.effective_chat.id))


@recorded
@with_checks(silent=False)
def delete(update:telegram.Update, context:telegram.ext.CallbackContext):

    operator = update.effective_user
    myself = context.bot
    chat_id = update.effective_chat.id
    request_time = strftime("%M%S")

    button_cancel = telegram.InlineKeyboardButton("Cancel", callback_data=json.dumps(
        {"t": "del", "c": {"u":operator.id, "t": request_time, "c": False}}))
    button_confirm = telegram.InlineKeyboardButton("Confirm", callback_data=json.dumps(
        {"t": "del", "c": {"u":operator.id, "t": request_time, "c": True}}))
    inline_keyboard = telegram.InlineKeyboardMarkup([[button_cancel, button_confirm]])

    deletion_request = {"operator": operator.id, "request_time": request_time}
    context.chat_data["deletion_requests"].append(deletion_request)

    confirmation = update.message.reply_text(("You have %d messages in my records. \n"
        "Are you sure you want to delete all of them? \n"
        "If you don't respond, this request will be cancelled in a minute."
        ) % len(context.chat_data[operator.id]),
        reply_markup=inline_keyboard)
    logger.info("User %s (%d) in chat %s (%d) sent a deletion request. Timestamp: %s" % ( \
                update.effective_user.full_name,
                update.effective_user.id,
                update.effective_chat.title,
                update.effective_chat.id,
                request_time))
    
    # automatically cancel the request after a minute
    def timeout():
        sleep(60)
        if deletion_request in context.chat_data["deletion_requests"]:
            context.chat_data["deletion_requests"].remove(deletion_request)
            confirmation.edit_text("Request confirmation timed out.")
            logger.info("In chat %s (%d), user %s (%d)'s deletion request with time stamp %s timed out." % ( \
                        update.effective_chat.title,
                        update.effective_chat.id,
                        update.effective_user.full_name,
                        update.effective_user.id,
                        request_time))
    request_timer = Thread(target=timeout)
    request_timer.start()

