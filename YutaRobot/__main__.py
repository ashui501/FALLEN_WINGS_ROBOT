import importlib
import html
import time
import re
from sys import argv
from typing import Optional

from YutaRobot import (ALLOW_EXCL, CERT_PATH, DONATION_LINK, LOGGER,
                          OWNER_ID, BOT_NAME, PORT, SUPPORT_CHAT, TOKEN, URL, WEBHOOK,
                          dispatcher, StartTime, telethn, updater, pbot)
# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from YutaRobot.modules import ALL_MODULES
from YutaRobot.modules.helper_funcs.chat_status import is_user_admin
from YutaRobot.modules.helper_funcs.misc import paginate_modules
import YutaRobot.modules.sql.users_sql as sql
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ParseMode,
                      Update)
from telegram.error import (BadRequest, ChatMigrated, NetworkError,
                            TelegramError, TimedOut, Unauthorized)
from telegram.ext import (CallbackContext, CallbackQueryHandler, CommandHandler,
                          Filters, MessageHandler)
from telegram.ext.dispatcher import DispatcherHandlerStop
from telegram.utils.helpers import escape_markdown


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time

START_TEX = """𝖧𝖾𝗅𝗅𝗈 {}, 𝗐𝖺𝗂𝗍 𝖺 𝗆𝗂𝗇 𝖻𝗋𝗈..."""

PM_START_TEXT = """
𝖧𝖾𝗒 {}, 💌
𝖬𝗒𝗌𝖾𝗅𝖿 *𝖸umeko*, 𝖠𝗇 𝖠𝖽𝗏𝖺𝗇𝖼𝖾 𝖦𝗋𝗈𝗎𝗉 𝖬𝖺𝗇𝖺𝗀𝖾𝗆𝖾𝗇𝗍 𝖡𝗈𝗍 𝖡𝗎𝗂𝗅𝗍 𝗍𝗈 𝖬𝖺𝗇𝖺𝗀𝖾 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉𝗌[.](https://graph.org/file/f33e8f0cd00f7ff3245ae.jpg)
───────────────────────
**◎ 𝖧𝗂𝗍 𝗍𝗁𝖾 𝗁𝖾𝗅𝗉 𝖻𝗎𝗍𝗍𝗈𝗇 𝗍𝗈 𝖿𝗂𝗇𝖽 𝗈𝗎𝗍 𝗆𝗈𝗋𝖾 𝖺𝖻𝗈𝗎𝗍 𝗁𝗈𝗐 𝗍𝗈 𝗎𝗌𝖾 𝗆𝖾 𝗍𝗈 𝗆𝗒 𝖿𝗎𝗅𝗅 𝗉𝗈𝗍𝖾𝗇𝗍𝗂𝖺𝗅.**
"""


buttons = [
    [
        InlineKeyboardButton(
            text="➕ sᴜᴍᴍᴏɴ ᴍᴇ ➕",url="t.me/Yumekoproxbot?startgroup=true"),
    ],
    [
        InlineKeyboardButton(
            text="𝖲𝗎𝗉𝗉𝗈𝗋𝗍 ∘",url="https://t.me/infinity_anime_gang"),
        InlineKeyboardButton(
            text="𝖠𝖻𝗈𝗎𝗍 ∘", callback_data="_yuta"),              
    ],   
    [                    
        InlineKeyboardButton(
            text="❓ 𝖧𝖾𝗅𝗉 & 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌❓ ", callback_data="help_back"
        ),
    ],
]


HELP_STRINGS = """
ᴍᴀɪɴ ᴄᴏᴍᴍᴀɴᴅs ᴀᴠᴀɪʟᴀʙʟᴇ:
➛ /𝗁𝖾𝗅𝗉: 𝖯𝖬'𝗌 𝗒𝗈𝗎 𝗍𝗁𝗂𝗌 𝗆𝖾𝗌𝗌𝖺𝗀𝖾.
➛ /𝗁𝖾𝗅𝗉 <𝗆𝗈𝖽𝗎𝗅𝖾 𝗇𝖺𝗆𝖾>: 𝖯𝖬'𝗌 𝗒𝗈𝗎 𝗂𝗇𝖿𝗈 𝖺𝖻𝗈𝗎𝗍 𝗍𝗁𝖺𝗍 𝗆𝗈𝖽𝗎𝗅𝖾.
➛ /𝖽𝗈𝗇𝖺𝗍𝖾: 𝗂𝗇𝖿𝗈𝗋𝗆𝖺𝗍𝗂𝗈𝗇 𝗈𝗇 𝗁𝗈𝗐 𝗍𝗈 𝖽𝗈𝗇𝖺𝗍𝖾!
➛ /𝗌𝖾𝗍𝗍𝗂𝗇𝗀𝗌:
➛ 𝗂𝗇 𝖯𝖬: 𝗐𝗂𝗅𝗅 𝗌𝖾𝗇𝖽 𝗒𝗈𝗎 𝗒𝗈𝗎𝗋 𝗌𝖾𝗍𝗍𝗂𝗇𝗀𝗌 𝖿𝗈𝗋 𝖺𝗅𝗅 𝗌𝗎𝗉𝗉𝗈𝗋𝗍𝖾𝖽 𝗌𝗈𝗎𝗋𝖼𝖾.
➛ 𝗂𝗇 𝖺 𝗀𝗋𝗈𝗎𝗉: 𝗐𝗂𝗅𝗅 𝗋𝖾𝖽𝗂𝗋𝖾𝖼𝗍 𝗒𝗈𝗎 𝗍𝗈 𝗉𝗆, 𝗐𝗂𝗍𝗁 𝖺𝗅𝗅 𝗍𝗁𝖺𝗍 𝖼𝗁𝖺𝗍'𝗌 𝗌𝖾𝗍𝗍𝗂𝗇𝗀𝗌
""".format(
    dispatcher.bot.first_name,
    "" if not ALLOW_EXCL else "All commands can either be used with / or !.",
)

GABIIMGSTART = "https://graph.org/file/8c34a1870249b41ec36d5.jpg"

DONATE_STRING = """Heya, glad to hear you want to donate!
 You can support the project via [Paytm](#) or by contacting Anonymous
 Supporting isnt always financial!
 Those who cannot provide monetary support are welcome to help us develop the bot at ."""

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("YutaRobot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    
    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


def test(update: Update, context: CallbackContext):
    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)


def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="× BACK ×", callback_data="help_back")]]
                    ),
                )

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name

            usr = update.effective_user
            lol = update.effective_message.reply_text(
                START_TEX.format(usr.first_name), parse_mode=ParseMode.MARKDOWN
            )
            
            time.sleep(0.1)
            lol.edit_text("💥")
            time.sleep(0.3)
            lol.edit_text("⚡")
            time.sleep(0.3)
            lol.edit_text("Starting...")
            time.sleep(0.2)
            lol.delete()
            
            
            update.effective_message.reply_text(
                PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )            
    else:
        update.effective_message.reply_animation(
            GABIIMGSTART, caption= "<b>ayee stoopid, I'm alive!!\nHaven't sleep since</b>: <code>{}</code>".format(
                uptime
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Support",
                            url=f"https://t.me/infinity_anime_gang",
                        ),
                    ]
                ]
            ),
        )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "Here is the help for the *{}* module:\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass


def yuta_about_callback(update, context):
    query = update.callback_query
    if query.data == "_yuta":
        query.message.edit_text(
            text=""" 𝖧𝖾𝗒 𝖨'𝗆 𝖸𝗎𝗎𝗍𝖺, 𝖠 𝗉𝗈𝗐𝖾𝗋𝖿𝗎𝗅 𝗀𝗋𝗈𝗎𝗉 𝗆𝖺𝗇𝖺𝗀𝖾𝗆𝖾𝗇𝗍 𝖻𝗈𝗍 𝖻𝖺𝗌𝖾𝖽 𝗈𝗇 𝗃𝗎𝗃𝗎𝗍𝗌𝗎 𝗄𝖺𝗂𝗌𝖾𝗇 𝖺𝗇𝗂𝗆𝖾.
𝖨'𝗅𝗅 𝗁𝖾𝗅𝗉 𝗒𝗈𝗎 𝗆𝖺𝗇𝖺𝗀𝖾 𝗒𝗈𝗎𝗋 𝗀𝗋𝗈𝗎𝗉 𝖺𝗇𝖽 𝗄𝖾𝖾𝗉 𝗂𝗍 𝗌𝖺𝖿𝖾 𝖿𝗋𝗈𝗆 𝗌𝗉𝖺𝗆𝗆𝖾𝗋𝗌 𝖺𝗇𝖽 𝗌𝖼𝖺𝗆𝗆𝖾𝗋𝗌.
◉ 𝖨 𝗁𝖺𝗏𝖾 𝖺𝗇 𝖺𝖽𝗏𝖺𝗇𝖼𝖾 𝖺𝗇𝗍𝗂-𝖿𝗅𝗈𝗈𝖽 𝗌𝗒𝗌𝗍𝖾𝗆
◉ 𝖨 𝖼𝖺𝗇 𝗋𝖾𝗌𝗍𝗋𝗂𝖼𝗍 𝗎𝗌𝖾𝗋𝗌
◉ 𝖨 𝖼𝖺𝗇 𝗐𝖺𝗋𝗇 𝗎𝗌𝖾𝗋𝗌 𝗎𝗇𝗍𝗂𝗅 𝗍𝗁𝖾𝗒 𝗋𝖾𝖺𝖼𝗁 𝗆𝖺𝗑 𝗐𝖺𝗋𝗇𝗌, 𝗐𝗂𝗍𝗁 𝖾𝖺𝖼𝗁 𝗉𝗋𝖾𝖽𝖾𝖿𝗂𝗇𝖾𝖽 𝖺𝖼𝗍𝗂𝗈𝗇𝗌 𝗌𝗎𝖼𝗁 𝖺𝗌 𝖻𝖺𝗇, 𝗆𝗎𝗍𝖾, 𝗄𝗂𝖼𝗄, 𝖾𝗍𝖼.
◉ 𝖨 𝖼𝖺𝗇 𝗀𝗋𝖾𝖾𝗍 𝗎𝗌𝖾𝗋𝗌 𝗐𝗂𝗍𝗁 𝖼𝗎𝗌𝗍𝗈𝗆𝗂𝗌𝖺𝖻𝗅𝖾 𝗐𝖾𝗅𝖼𝗈𝗆𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌
""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="𝖲𝗎𝗉𝗉𝗈𝗋𝗍 ∘", url="https://t.me/infinity_anime_gang"),                               
                    InlineKeyboardButton(text="𝖴𝗉𝖽𝖺𝗍𝖾𝗌 ∘", url="https://t.me/yumeko_update"),                            
                 ],
                 [
                    InlineKeyboardButton(text="🏠", callback_data="donate_back")
                 ]
                ]
            ),
        )
    elif query.data == "source_back":
        query.message.edit_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
        )

def donate_callback(update, context):
    query = update.callback_query
    if query.data == "donate_":
        query.message.edit_text(
            text="""*Ohayo*\nWeebs Or Otakus!\nI'm Makise  and I'm am Official bot of samurai network.
Let us tell you that we are managing Makise bot without any problem till now but as it is growing.
We need your help to keep it better.\nYou can help us by donating.We will be happy if you donate With which we will be able to make Gabi even better without any problem. 
• DM To [RONIN](https://t.me/DushmanXRonin) for donation information.
It would be great if you would help us!""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="Support", url="https://t.me/infinity_anime_gang"),                               
                    InlineKeyboardButton(text="NETWORK", url="https://t.me/yumeko_update"),                            
                 ],
                 [
                    InlineKeyboardButton(text="🔙Back", callback_data="donate_back")
                 ]
                ]
            ),
        )
    elif query.data == "donate_back":
        query.message.edit_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
        )


def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Help",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_text(
            "Contact me in PM to get the list of possible commands.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Help",
                            url="t.me/{}?start=help".format(context.bot.username),
                        )
                    ]
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )


def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Back",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Settings",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "Click here to check your settings."

    else:
        send_settings(chat.id, user.id, True)


def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )

        if OWNER_ID != 1610284626 and DONATION_LINK:
            update.effective_message.reply_text(
                "You can also donate to the person currently running me "
                "[here]({})".format(DONATION_LINK),
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        try:
            bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

            update.effective_message.reply_text(
                "I've PM'ed you about donating to my creator!"
            )
        except Unauthorized:
            update.effective_message.reply_text(
                "Contact me in PM first to get donation information."
            )


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop




def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.sendMessage(f"@{SUPPORT_CHAT}", "Online Again")
        except Unauthorized:
            LOGGER.warning(
                "Bot isnt able to send message to support_chat, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

    test_handler = CommandHandler("test", test, run_async=True)
    start_handler = CommandHandler("start", start, run_async=True)

    help_handler = CommandHandler("help", get_help, run_async=True)
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_.*", run_async=True)

    settings_handler = CommandHandler("settings", get_settings, run_async=True)
    settings_callback_handler = CallbackQueryHandler(settings_button, pattern=r"stngs_", run_async=True)

    yuta_callback_handler = CallbackQueryHandler(yuta_about_callback, pattern=r"_yuta", run_async=True)
    donate_callback_handler = CallbackQueryHandler(donate_callback, pattern=r"donate_", run_async=True)

    donate_handler = CommandHandler("donate", donate, run_async=True)
    migrate_handler = MessageHandler(Filters.status_update.migrate, migrate_chats, run_async=True)

    # dispatcher.add_handler(test_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(yuta_callback_handler)
    dispatcher.add_handler(donate_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)

    dispatcher.add_error_handler(error_callback)

    if WEBHOOK:
        LOGGER.info("Using webhooks.")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + TOKEN, certificate=open(CERT_PATH, "rb"))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)

    else: 
        LOGGER.info("Using long polling.")
        updater.start_polling(timeout=1, read_latency=4, allowed_updates=Update.ALL_TYPES, 
                              drop_pending_updates=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == '__main__':
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()
