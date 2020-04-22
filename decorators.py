#!/usr/bin/python
# -*- coding: utf-8 -*-

# This is where several decorators are defined.

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from functools import wraps # use decorators without disturbing introspection


# a decorator for admin-only commands
def admins_only(func:callable):
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        update = args[0]
        if update.effective_chat.get_member(update.effective_user.id).status \
                not in ["creator", "administrator"]:
                    update.message.reply_text("Permission denied.")
                    logger.info("Non-admin user %s (%d) tried to [%s] in chat %s (%d)." % \
                                (update.effective_user.full_name, 
                                 update.effective_user.id, 
                                 func.__name__,
                                 update.effective_chat.title,
                                 update.effective_chat.id))
                    return
        else:
            return func(*args, **kwargs)
    return wrapped_func


# a decorator for checks-dependent commands
# Actually all command handler functions should use this decorator.
def with_checks(silent:bool):
    def decorator(func:callable):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            update = args[0]
            context = args[1]

            if not check_chat_type(update.effective_chat, silent): return # only usable in groups
            if ((func.__name__ != "record") and (context.bot.name not in update.message.text)): return
                    # only respond to commands issued to this bot
            if not check_permission(update.message, context.bot, silent): return
                    # must have the ability to delete others' messages

            if "recording" not in context.chat_data:
                context.chat_data["recording"] = None # add recording keypair
            if "deletion_requests" not in context.chat_data:
                context.chat_data["deletion_requests"] = []

            if update.effective_user.id not in context.chat_data:
                context.chat_data[update.effective_user.id] = [] # add user directory

            return func(*args, **kwargs)
        return wrapped_func
    return decorator


def check_chat_type(chat:telegram.Chat, silent:bool=False):
    if chat.type not in ["group", "supergroup"]:
        if not silent:
            message.reply_text("Use me in groups or supergroups only!")
        return 0
    else:
        return 1


def check_permission(message:telegram.Message, bot:telegram.Bot, silent:bool=False):

    if message.chat.get_member(bot.id).status != "administrator":
        if not silent:
            message.reply_text("Please set me as an admin first!")
        return 0

    if not message.chat.get_member(bot.id).can_delete_messages:
        if not silent:
            message.reply_text("Please allow me to delete messages first!")
        return 0

    return 1


# a decorator for recording commands
def recorded(func:callable):
    from MessageHandlerFunctions import record
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        record(*args, **kwargs)
        return func(*args, **kwargs)
    return wrapped_func


