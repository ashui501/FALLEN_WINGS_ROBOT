#MADE BY @KIRITO1240
#PROVIDED BY @NovaXMod


#IMPORTS
import re
import html

from telegram import ParseMode
from telegram.update import Update
from telegram.ext import ChatJoinRequestHandler, CallbackQueryHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.utils.helpers import mention_html
from functools import wraps


#NAME - YOUR BOTS NAME (EG. from Raiden import dispatcher)
from YutaRobot import dispatcher, DEV_USERS
from YutaRobot.modules.helper_funcs.chat_status import bot_admin
from YutaRobot.modules.log_channel import loggable



def user_can_restrict_no_reply(func):
    @wraps(func)
    def u_can_restrict_noreply(
        update: Update, context: CallbackContext, *args, **kwargs
    ):
        bot = context.bot
        user = update.effective_user
        chat = update.effective_chat
        query = update.callback_query
        member = chat.get_member(user.id)

        if user:
            if (
                member.can_restrict_members
                or member.status == "creator"
                or user.id in DEV_USERS
            ):
                return func(update, context, *args, **kwargs)
            elif member.status == 'administrator':
                query.answer("You're missing the `can_restrict_members` permission.")
            else:
                query.answer("You need to be admin with `can_restrict_users` permission to do this.")
        elif " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass

    return u_can_restrict_noreply



def chat_join_req(upd: Update, ctx: CallbackContext):
    bot = ctx.bot
    user = upd.chat_join_request.from_user
    chat = upd.chat_join_request.chat
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✘ ᴀᴘᴘʀᴏᴠᴇ ✘", callback_data="cb_approve={}".format(user.id)
                ),
                InlineKeyboardButton(
                    "✘ ᴅᴇᴄʟɪɴᴇ ✘", callback_data="cb_decline={}".format(user.id)
                ),
            ]
        ]
    )
    bot.send_message(
        chat.id,
        "This Simp {} wants to join {}".format(
            mention_html(user.id, user.first_name), chat.title or "this chat"
        ),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )


@user_can_restrict_no_reply
@bot_admin
@loggable
def approve_joinreq(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    query = update.callback_query
    user = update.effective_user
    chat = update.effective_chat
    match = re.match(r"cb_approve=(.+)", query.data)

    user_id = match.group(1)
    try:
        bot.approve_chat_join_request(chat.id, user_id)
        update.effective_message.edit_text(
            f"Join Request Approved by{mention_html(user.id, user.first_name)}.",
            parse_mode="HTML",
        )
        logmsg = (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#JOIN_REQUEST\n"
                f"Approved\n"
                f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
                f"<b>User:</b> {mention_html(user_id, html.escape(user.first_name))}\n"
        )
        return logmsg
    except Exception as e:
        update.effective_message.edit_text(str(e))
        pass


@user_can_restrict_no_reply
@bot_admin
@loggable
def decline_joinreq(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    query = update.callback_query
    user = update.effective_user
    chat = update.effective_chat
    match = re.match(r"cb_decline=(.+)", query.data)

    user_id = match.group(1)
    try:
        bot.decline_chat_join_request(chat.id, user_id)
        update.effective_message.edit_text(
            f"Join Request declined by {mention_html(user.id, user.first_name)}.",
            parse_mode="HTML",
        )
        logmsg = (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#JOIN_REQUEST\n"
                f"Declined\n"
                f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
                f"<b>User:</b> {mention_html(user_id, html.escape(user.first_name))}\n"
        )
        return logmsg
    except Exception as e:
        update.effective_message.edit_text(str(e))
        pass


dispatcher.add_handler(ChatJoinRequestHandler(callback=chat_join_req, run_async=True))
dispatcher.add_handler(CallbackQueryHandler(approve_joinreq, pattern=r"cb_approve=", run_async=True))
dispatcher.add_handler(CallbackQueryHandler(decline_joinreq, pattern=r"cb_decline=", run_async=True))
