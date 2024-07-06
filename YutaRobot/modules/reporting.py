import html
import re
from typing import Optional
from YutaRobot import DRAGONS, LOGGER, TIGERS, WOLVES, dispatcher
from YutaRobot.modules.helper_funcs.chat_status import (
    user_admin,
    user_not_admin,
)
from YutaRobot.modules.log_channel import loggable
from YutaRobot.modules.sql import reporting_sql as sql
from YutaRobot.modules.helper_funcs.chat_status import (
    user_admin,
    is_user_admin,
)
from telegram import (
    CallbackQuery,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
    User,
)
from telegram.error import BadRequest
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.utils.helpers import mention_html

REPORT_GROUP = 12
REPORT_IMMUNE_USERS = DRAGONS + TIGERS + WOLVES


@user_admin
def report_setting(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat
    msg = update.effective_message

    if len(args) >= 1:
        if args[0] in ("yes", "on"):
            sql.set_chat_setting(chat.id, True)
            msg.reply_text("Users will now be able to report messages.")

        elif args[0] in ("no", "off"):
            sql.set_chat_setting(chat.id, False)
            msg.reply_text("Users will no longer be able to report via @admin or /report.")
    else:
        reportable = sql.chat_should_report(chat.id)
        R_STRING = "To change this setting, try this command again, with one of the following args: yes/no/on/off"
        if reportable:
            msg.reply_text(f"Reports are currently enabled in this chat.\nUsers can use the /report command, or mention @admin, to tag all admins.\n\n{R_STRING}")
        else:
            msg.reply_text(f"Reports are currently disabled in this chat.\n\n{R_STRING}")


@user_not_admin
@loggable
def report(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if chat and sql.chat_should_report(chat.id):
        args = message.text.split(None, 1)
        if len(args) < 2:
            message.reply_text("You must provide a reason while reporting!")
            return ""
        admin_list = bot.getChatAdministrators(chat.id)
        message = update.effective_message

        if message.reply_to_message:
            reported_user = message.reply_to_message.from_user
            if reported_user.id == bot.id:
                message.reply_text("Why would I report myself?")
                return ""
            if reported_user.id == user.id:
                message.reply_text("You cannot report yourself")
                return ""
            for x in admin_list:
                admins = []
                admins.append(x.user.id)
                if reported_user.id in admins:
                    return ""
            reported = f"Reported {mention_html(reported_user.id, reported_user.first_name)} to admins."
        else:
            reported_user = user
            reported = "Reported to admins."

        msg = "<b>{}:</b>" \
        "\n<b>Reported user:</b> {} (<code>{}</code>)" \
        "\n<b>Reported by:</b> {} (<code>{}</code>)".format(
            html.escape(chat.title),
            mention_html(reported_user.id, reported_user.first_name),
            reported_user.id,
            mention_html(user.id, user.first_name),
            user.id,
        )
        for admin in admin_list:
            if admin.user.is_bot:  # can't message bots
                continue
            try:
                reported += f"<a href=\"tg://user?id={admin.user.id}\">\u2063</a>"
            except BadRequest:  # TODO: cleanup exceptions
                LOGGER.exception("Exception while reporting user")

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔘 Mark as resolved", callback_data="rm_report",
                    ),
                ],
            ],
        )
        message.reply_text(reported, reply_markup=keyboard, parse_mode=ParseMode.HTML)

        return msg

    return ""


@loggable
def rm_button(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    chat: Optional[Chat] = update.effective_chat
    match = re.match(r"rm_report", query.data)
    if match:
        if (not is_user_admin(chat, user.id)) and (not user.id in DRAGONS):
            return ""
        update.effective_message.edit_text(
            f"Problem solved by {mention_html(user.id, user.first_name)}.",
            parse_mode=ParseMode.HTML,
        )
    return ""



def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, _):
    return f"This chat is setup to send user reports to admins, via /report and @admin: `{sql.chat_should_report(chat_id)}`"


def __user_settings__(user_id):
    if sql.user_should_report(user_id) is True:
        text = "You will receive reports from chats you're admin."
    else:
        text = "You will *not* receive reports from chats you're admin."
    return text


__help__ = """
 • `/report <reason>`*:* reply to a message to report it to admins.
 • `@admin`*:* reply to a message to report it to admins.
*NOTE:* Neither of these will get triggered if used by admins.
*Admins only:*
 • `/reports <on/off>`*:* change report setting, or view current status.
   • If done in pm, toggles your status.
   • If in group, toggles that groups's status.
"""

SETTING_HANDLER = CommandHandler("reports", report_setting, run_async=True)
REPORT_HANDLER = CommandHandler("report", report, filters=Filters.chat_type.groups, run_async=True)
ADMIN_REPORT_HANDLER = MessageHandler(Filters.regex(r"(?i)@admin(s)?"), report, run_async=True)
CALLBACK_QUERY_HANDLER = CallbackQueryHandler(rm_button, pattern=r"rm_report", run_async=True)

dispatcher.add_handler(SETTING_HANDLER)
dispatcher.add_handler(CALLBACK_QUERY_HANDLER)
dispatcher.add_handler(REPORT_HANDLER, REPORT_GROUP)
dispatcher.add_handler(ADMIN_REPORT_HANDLER, REPORT_GROUP)

__mod_name__ = "ʀᴇᴘᴏʀᴛɪɴɢꜱ"
__handlers__ = [
    (REPORT_HANDLER, REPORT_GROUP),
    (ADMIN_REPORT_HANDLER, REPORT_GROUP),
    (CALLBACK_QUERY_HANDLER),
    (SETTING_HANDLER),
]
