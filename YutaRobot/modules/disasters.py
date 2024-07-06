import html
import json
from typing import Optional

from YutaRobot import (
    DEV_USERS,
    OWNER_ID,
    DRAGONS,
    SUPPORT_CHAT,
    DEMONS,
    TIGERS,
    WOLVES,
    dispatcher,
    ELEVATED_USERS_FILE,
)
from YutaRobot.modules.helper_funcs.chat_status import (
    dev_plus,
    sudo_plus,
    whitelist_plus,
)
from YutaRobot.modules.disable import DisableAbleCommandHandler
from YutaRobot.modules.helper_funcs.extraction import extract_user
from YutaRobot.modules.log_channel import gloggable
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, TelegramError, Update
from telegram.ext import CallbackContext, CommandHandler
from telegram.utils.helpers import mention_html


def check_user_id(user_id: int, context: CallbackContext) -> Optional[str]:
    bot = context.bot
    if not user_id:
        reply = "That...is a chat! baka ka omae?"

    elif user_id == bot.id:
        reply = "This does not work that way."

    else:
        reply = None
    return reply


# This can serve as a deeplink example.
# disasters =
# """ Text here """

# do not async, not a handler
# def send_disasters(update):
#    update.effective_message.reply_text(
#        disasters, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

### Deep link example ends


@dev_plus
@gloggable
def addsudo(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE) as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        message.reply_text("This member is already a Titan")
        return ""

    if user_id in DEMONS:
        rt += "Requested EA to promote a Surveycorp to Titan."
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        rt += "Requested EA to promote a Marleyan to Titan."
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    data["sudos"].append(user_id)
    DRAGONS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt
        + "\nSuccessfully set Disaster level of {} to Titan!".format(
            user_member.first_name,
        ),
    )

    log_message = (
        f"#SUDO's\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@sudo_plus
@gloggable
def addsupport(
    update: Update,
    context: CallbackContext,
) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE) as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "Requested EA to demote this Titan to Surveycorp"
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        message.reply_text("This user is already a Surveycorp")
        return ""

    if user_id in WOLVES:
        rt += "Requested EA to promote this Marleyan to Surveycorp"
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    data["supports"].append(user_id)
    DEMONS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\n{user_member.first_name} was added as a Surveycorp!",
    )

    log_message = (
        f"#SUPPORT's\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@sudo_plus
@gloggable
def addwhitelist(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE) as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "This member is a Titan, Demoting to Marleyan."
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        rt += "This user is already a Surveycorp, Demoting to Marleyan."
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        message.reply_text("This user is already a Marleyan.")
        return ""

    data["whitelists"].append(user_id)
    WOLVES.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\nSuccessfully promoted {user_member.first_name} to a Marleyan!",
    )

    log_message = (
        f"#WHITRLIST's\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)} \n"
        f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@sudo_plus
@gloggable
def addtiger(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE) as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "This member is a Titan, Demoting to Eldian."
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        rt += "This user is already a Surveycorp, Demoting to Eldian."
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        rt += "This user is already a Marleyan, Promoting to Eldian."
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    if user_id in TIGERS:
        message.reply_text("This user is already a Eldian.")
        return ""

    data["tigers"].append(user_id)
    TIGERS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\nSuccessfully promoted {user_member.first_name} to a Eldian!",
    )

    log_message = (
        f"#ELDIAN\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)} \n"
        f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@dev_plus
@gloggable
def removesudo(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE) as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        message.reply_text("Requested EA to demote this user to Mindless Titan")
        DRAGONS.remove(user_id)
        data["sudos"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNSUDO\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message

    else:
        message.reply_text("This user is not a Titan!")
        return ""


@sudo_plus
@gloggable
def removesupport(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE) as infile:
        data = json.load(infile)

    if user_id in DEMONS:
        message.reply_text("Requested EA to demote this user to Mindless Titan")
        DEMONS.remove(user_id)
        data["supports"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNSUPPORT\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message

    else:
        message.reply_text("This user is not a Surveycorp")
        return ""


@sudo_plus
@gloggable
def removewhitelist(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE) as infile:
        data = json.load(infile)

    if user_id in WOLVES:
        message.reply_text("Demoting to Mindless Titan")
        WOLVES.remove(user_id)
        data["whitelists"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNWHITELIST\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message
    else:
        message.reply_text("This user is not a Marleyan!")
        return ""


@sudo_plus
@gloggable
def removetiger(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE) as infile:
        data = json.load(infile)

    if user_id in TIGERS:
        message.reply_text("Demoting to Mindless Titan")
        TIGERS.remove(user_id)
        data["tigers"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNTIGER\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message
    else:
        message.reply_text("This user is not a Eldian!")
        return ""


@whitelist_plus
def whitelistlist(update: Update, context: CallbackContext):
    reply = "<b>Marleyans List:</b>\n"
    m = update.effective_message.reply_text(
        "<code>Gathering intel..</code>", parse_mode=ParseMode.HTML,
    )
    bot = context.bot
    for each_user in WOLVES:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)

            reply += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def tigerlist(update: Update, context: CallbackContext):
    reply = "<b>Eldians List:</b>\n"
    m = update.effective_message.reply_text(
        "<code>Gathering intel..</code>", parse_mode=ParseMode.HTML,
    )
    bot = context.bot
    for each_user in TIGERS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def supportlist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "<code>Gathering intel..</code>", parse_mode=ParseMode.HTML,
    )
    reply = "<b>Surveycorp List:</b>\n"
    for each_user in DEMONS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def sudolist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "<code>Gathering intel..</code>", parse_mode=ParseMode.HTML,
    )
    true_sudo = list(set(DRAGONS) - set(DEV_USERS))
    reply = "<b>Titans List:</b>\n"
    for each_user in true_sudo:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def devlist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "<code>Gathering intel..</code>", parse_mode=ParseMode.HTML,
    )
    true_dev = list(set(DEV_USERS) - {OWNER_ID})
    reply = "<b>Members Of Eldian Arena:</b>\n"
    for each_user in true_dev:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)

def disasters(update: Update, context: CallbackContext):
    msg = update.effective_message
    reply_text = (
        msg.reply_to_message.reply_text if msg.reply_to_message else msg.reply_text
    )
    text = "<b>ℹ️ Read up on disasters here:</b>"
    keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text = "Click Here",
                url="https://t.me/EldianGabi_UpdateChannel/3",
            ),
        ],
    ],
    )
    reply_text(text=text, reply_markup=keyboard, parse_mode=ParseMode.HTML)


__help__ = f"""
*⚠️ Notice:*
Commands listed here only work for users with special access and are mainly used for troubleshooting, debugging purposes.
Group admins/group owners do not need these commands.

 ╔ *List all special users:*
 ╠ `/disasters`*:* Learn what disasters are
 ╠ `/titans`*:* Lists all Titans 
 ╠ `/surveycorp s`*:* Lists all Surveycorps
 ╠ `/eldians`*:* Lists all Eldians
 ╠ `/marleyans`*:* Lists all Marleyans 
 ╠ `/royals`*:* Lists all Royals
 ╠ `/addtitan`*:* Adds a user to Titan 
 ╠ `/addsurveycorp`*:* Adds a user to Surveycorp 
 ╠ `/addeldian`*:* Adds a user to Eldian 
 ╠ `/addmarleyan`*:* Adds a user to Marleyan 
 ╚ `Add dev doesnt exist, devs should know how to add themselves`

 ╔ *Ping:*
 ╠ `/ping`*:* gets ping time of bot to telegram server
 ╚ `/pingall`*:* gets all listed ping times

 ╔ *Broadcast: (Bot owner only)*
 ╠  *Note:* This supports basic markdown
 ╠ `/broadcastall`*:* Broadcasts everywhere
 ╠ `/broadcastusers`*:* Broadcasts too all users
 ╚ `/broadcastgroups`*:* Broadcasts too all groups

 ╔ *Groups Info:*
 ╠ `/groups`*:* List the groups with Name, ID, members count as a txt
 ╠ `/leave <ID>`*:* Leave the group, ID must have hyphen
 ╠ `/stats`*:* Shows overall bot stats
 ╠ `/getchats`*:* Gets a list of group names the user has been seen in. Bot owner only
 ╚ `/ginfo username/link/ID`*:* Pulls info panel for entire group

 ╔ *Access control:*
 ╠ `/ignore`*:* Blacklists a user from
 ╠  using the bot entirely
 ╠ `/lockdown <off/on>`*:* Toggles bot adding to groups
 ╠ `/notice`*:* Removes user from blacklist
 ╚ `/ignoredlist`*:* Lists ignored users

 ╔ *Module loading:*
 ╠ `/listmodules`*:* Prints modules and their names
 ╠ `/unload <name>`*:* Unloads module dynamically
 ╚ `/load <name>`*:* Loads module

 ╔ *Global Bans:*
 ╠ `/gban user reason`*:* Globally bans a user
 ╚ `/ungban user reason`*:* Unbans the user from the global bans list

 ╔ *Module loading:*
 ╠ `/listmodules`*:* Lists names of all modules
 ╠ `/load modulename`*:* Loads the said module to
 ╠   memory without restarting.
 ╠ `/unload modulename`*:* Loads the said module from
 ╚   memory without restarting.memory without restarting the bot

 ╔ *Remote commands:*
 ╠ `/rban user group`*:* Remote ban
 ╠ `/runban user group`*:* Remote un-ban
 ╠ `/rpunch user group`*:* Remote punch
 ╠ `/rmute user group`*:* Remote mute
 ╚ `/runmute user group`*:* Remote un-mute

 ╔ *Windows self hosted only:*
 ╠ `/reboot`*:* Restarts the bots service
 ╚ `/gitpull`*:* Pulls the repo and then restarts the bots service

 ╔ *Chatbot:*
 ╚ `/listaichats`*:* Lists the chats the chatmode is enabled in

 ╔ *Debugging and Shell:*
 ╠ `/debug <on/off>`*:* Logs commands to updates.txt
 ╠ `/logs`*:* Run this in support group to get logs in pm
 ╠ `/eval`*:* Self explanatory
 ╠ `/sh`*:* Runs shell command
 ╠ `/shell`*:* Runs shell command
 ╠ `/clearlocals`*:* As the name goes
 ╠ `/dbcleanup`*:* Removes deleted accs and groups from db
 ╚ `/py`*:* Runs python code

 ╔ *Global Bans:*
 ╠ `/gban <id> <reason>`*:* Gbans the user, works by reply too
 ╠ `/ungban`*:* Ungbans the user, same usage as gban
 ╚ `/gbanlist`*:* Outputs a list of gbanned users

Done.
"""

DISASTERS_HANDLER = DisableAbleCommandHandler("disasters", disasters, run_async=True)
SUDO_HANDLER = CommandHandler(("addsudo", "addtitan"), addsudo, run_async=True)
SUPPORT_HANDLER = CommandHandler(("addsupport", "addsurveycorp"), addsupport, run_async=True)
TIGER_HANDLER = CommandHandler(("addeldian"), addtiger, run_async=True)
WHITELIST_HANDLER = CommandHandler(("addwhitelist", "addmarleyan"), addwhitelist, run_async=True)
UNSUDO_HANDLER = CommandHandler(("removesudo", "removetitan"), removesudo, run_async=True)
UNSUPPORT_HANDLER = CommandHandler(("removesupport", "removesurveycorp"), removesupport, run_async=True)
UNTIGER_HANDLER = CommandHandler(("removeeldian"), removetiger, run_async=True)
UNWHITELIST_HANDLER = CommandHandler(("removewhitelist", "removemarleyan"), removewhitelist, run_async=True)

WHITELISTLIST_HANDLER = CommandHandler(["whitelistlist", "marleyans"], whitelistlist, run_async=True)
TIGERLIST_HANDLER = CommandHandler(["eldians"], tigerlist, run_async=True)
SUPPORTLIST_HANDLER = CommandHandler(["supportlist", "surveycorps"], supportlist, run_async=True)
SUDOLIST_HANDLER = CommandHandler(["sudolist", "titans"], sudolist, run_async=True)
DEVLIST_HANDLER = CommandHandler(["devlist", "royals"], devlist, run_async=True)

dispatcher.add_handler(SUDO_HANDLER)
dispatcher.add_handler(SUPPORT_HANDLER)
dispatcher.add_handler(TIGER_HANDLER)
dispatcher.add_handler(WHITELIST_HANDLER)
dispatcher.add_handler(UNSUDO_HANDLER)
dispatcher.add_handler(UNSUPPORT_HANDLER)
dispatcher.add_handler(UNTIGER_HANDLER)
dispatcher.add_handler(UNWHITELIST_HANDLER)
dispatcher.add_handler(DISASTERS_HANDLER)
dispatcher.add_handler(WHITELISTLIST_HANDLER)
dispatcher.add_handler(TIGERLIST_HANDLER)
dispatcher.add_handler(SUPPORTLIST_HANDLER)
dispatcher.add_handler(SUDOLIST_HANDLER)
dispatcher.add_handler(DEVLIST_HANDLER)

__mod_name__ = "ᴅɪꜱᴀꜱᴛᴇʀꜱ"
__handlers__ = [
    SUDO_HANDLER,
    SUPPORT_HANDLER,
    TIGER_HANDLER,
    WHITELIST_HANDLER,
    UNSUDO_HANDLER,
    UNSUPPORT_HANDLER,
    UNTIGER_HANDLER,
    UNWHITELIST_HANDLER,
    WHITELISTLIST_HANDLER,
    TIGERLIST_HANDLER,
    SUPPORTLIST_HANDLER,
    SUDOLIST_HANDLER,
    DEVLIST_HANDLER,
    DISASTERS_HANDLER,
]
