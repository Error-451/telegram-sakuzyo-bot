#!/usr/bin/python
# -*- coding: utf-8 -*-

# This is where functions for handling queries are registered.

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
import logging
import json
from threading import Thread
from decorators import *


logger = logging.getLogger(__name__)


@in_new_thread
def process_callback_query(update:telegram.Update, context:telegram.ext.CallbackContext):
    query = update.callback_query
    operator = query.from_user
    query_content = json.loads(query.data)
    origin = query.message

    if query_content["t"] == "del":
        result = process_deletion_request_confirmation(query_content, operator,
                                                       context, update.effective_chat.id)
        if result >= 0: # successful deletion
            query.answer(text="Your deletion request is processed successfully.", show_alert=True)
            logger.info(("User %s (%d) in chat %s (%d) confirmed the deletion request with timestamp %s,"
                        " deleting %d messages.") % ( \
                        update.effective_user.full_name,
                        update.effective_user.id,
                        update.effective_chat.title,
                        update.effective_chat.id,
                        query_content["c"]["t"],
                        result))
        elif result == -1: # user cancellation
            query.edit_message_text("Request cancelled by yourself.")
            query.answer(text="Cancelled.")
            logger.info("User %s (%d) in chat %s (%d) cancelled the deletion request with timestamp %s." % ( \
                        update.effective_user.full_name,
                        update.effective_user.id,
                        update.effective_chat.title,
                        update.effective_chat.id,
                        query_content["c"]["t"]))
        elif result == -2:
            query.answer(text=("Failed to process confirmation. \n"
                         "Make sure that you are the person who initiated the request."))
            logger.info(("User %s (%d) in chat %s (%d) failed to process the deletion request with timestamp %s."
                        "The deletion request belongs to user with id %d.") % ( \
                        update.effective_user.full_name,
                        update.effective_user.id,
                        update.effective_chat.title,
                        update.effective_chat.id,
                        query_content["c"]["t"],
                        query_content["c"]["u"]))


def process_deletion_request_confirmation(query_content:dict, operator:telegram.User,
                                          context:telegram.ext.CallbackContext,
                                          chat_id:int):
    deletion_request = {"operator": operator.id,
                        "request_time": query_content["c"]["t"]}
    if query_content["c"]["u"] == operator.id and \
            deletion_request in context.chat_data["deletion_requests"]: # validate the confirmation
        if query_content["c"]["c"]: # Does the user confirm or cancel?
            count = 0
            while context.chat_data[operator.id] != []: # do the deletion
                try: # Don't let any error interrupt this process
                    context.bot.delete_message(chat_id, context.chat_data[operator.id].pop())
                    count += 1
                except:
                    pass
            context.chat_data["deletion_requests"].remove(deletion_request) # remove the processed request
            return count # successful deletion
        else:
            context.chat_data["deletion_requests"].remove(deletion_request) # only remove the request
            return -1 # user cancellation
    else:
        return -2 # failed deletion
